from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, F
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models.academic import Payment, AcademicTerm
from ..models.fee import TermFee, StudentBalance
from ..models.student import Student
from ..forms.payment_form import PaymentForm
from ..utils.pdf_reports_modern import PaymentHistoryReport, ArrearsReport, create_pdf_response
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from decimal import Decimal
import csv
from datetime import datetime

@csrf_exempt
@require_http_methods(["GET"])
def student_payment_details_api(request, student_id):
    """API endpoint to get student payment details"""
    try:
        student = get_object_or_404(Student, id=student_id)
        current_term = AcademicTerm.get_current_term()
        
        if not current_term:
            return JsonResponse({'error': 'No current term set'}, status=400)
        
        # Reject archived students - they cannot make payments
        if student.is_archived:
            return JsonResponse({
                'error': 'This student has been archived',
                'student_name': student.get_full_name(),
                'is_archived': True,
                'message': f'{student.full_name} is archived (graduated with all fees paid). No further payments can be recorded.'
            }, status=403)
        
        # Check if student is graduated (not active) - they can only pay arrears
        if not student.is_active:
            # Graduated student - show ONLY their latest balance (which includes all arrears)
            # NOT sum of all balances (that would double-count)
            latest_balance = StudentBalance.objects.filter(student=student).order_by('-term__academic_year', '-term__term').first()
            
            if latest_balance:
                # Use the latest balance - this represents all money owed
                total_outstanding = float(latest_balance.current_balance)
            else:
                total_outstanding = Decimal('0')
            
            response_data = {
                'student_name': student.get_full_name(),
                'is_graduated': True,
                'is_archived': False,
                'message': 'Student has graduated. Can only pay ARREARS from previous terms.',
                'total_arrears': total_outstanding,
                'term_fee': 0.0,
                'previous_arrears': total_outstanding,
                'arrears_remaining': total_outstanding,
                'term_fee_remaining': 0.0,
                'amount_paid': 0.0,
                'current_balance': total_outstanding,
                'total_outstanding': total_outstanding,
                'payment_priority': f'GRADUATED - Must pay ${total_outstanding:.2f} in ARREARS'
            }
            return JsonResponse(response_data)
        
        # Active student - get their current term balance
        balance = StudentBalance.initialize_term_balance(student, current_term)
        
        if balance is None:
            # Active student but no balance - shouldn't happen, but handle gracefully
            return JsonResponse({'error': 'No balance record for this student in current term'}, status=400)
        
        # Calculate TOTAL outstanding - use CURRENT TERM balance only
        # (Previous terms' balances are already included as arrears in current term)
        total_outstanding = float(balance.current_balance) if balance and balance.current_balance > 0 else Decimal('0')
        
        response_data = {
            'student_name': student.get_full_name(),
            'is_graduated': False,
            'is_archived': False,
            'term_fee': float(balance.term_fee),
            'previous_arrears': float(balance.previous_arrears),
            'arrears_remaining': float(balance.arrears_remaining),
            'term_fee_remaining': float(balance.term_fee_remaining),
            'amount_paid': float(balance.amount_paid),
            'current_balance': float(balance.current_balance),
            'total_outstanding': float(total_outstanding),  # Current term balance only
        }
        
        # Determine payment priority - show total outstanding
        if total_outstanding > 0:
            response_data['payment_priority'] = f"${total_outstanding:.2f} total outstanding"
        else:
            response_data['payment_priority'] = "Fully paid"
        
        return JsonResponse(response_data)
    except Exception as e:
        import traceback
        print(f"DEBUG: Exception occurred: {str(e)}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)

class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    template_name = 'payments/payment_form.html'
    form_class = PaymentForm
    success_url = reverse_lazy('payment_list')

    def get_form_kwargs(self):
        """Pre-populate the form with the student if provided"""
        kwargs = super().get_form_kwargs()
        student_id = self.request.GET.get('student')
        if student_id:
            initial = kwargs.get('initial', {})
            initial['student'] = student_id
            kwargs['initial'] = initial
        return kwargs

    def form_valid(self, form):
        """Set the term and recorded_by before saving"""
        current_term = AcademicTerm.get_current_term()
        
        if not current_term:
            form.add_error(None, "❌ No current academic term set. Please set a current term in settings.")
            return self.form_invalid(form)
        
        student = form.cleaned_data['student']
        
        # IMPORTANT: Archived students cannot make payments - they have graduated with all fees paid
        if student.is_archived:
            form.add_error('student', 
                f"❌ {student.full_name} is archived (graduated with all fees paid). "
                f"No further payments can be recorded for this student.")
            return self.form_invalid(form)
        
        # For graduated students, find their LATEST balance term to record payment against
        if not student.is_active:
            # Graduated student - find their most recent balance
            # This will be their latest balance record (usually from the current term or last term they have a balance for)
            latest_balance = StudentBalance.objects.filter(student=student).order_by('-term__academic_year', '-term__term').first()
            if latest_balance:
                payment_term = latest_balance.term
            else:
                form.add_error('student',
                    f"❌ {student.full_name} has no balance records. Cannot record payment.")
                return self.form_invalid(form)
        else:
            # Active student - use current term
            payment_term = current_term
        
        # Both active AND graduated (but not archived) students can make payments
        # - Active students pay their current term fees/arrears
        # - Graduated students can pay any remaining arrears
        # The system will apply it correctly via the signal
        
        try:
            # Create a new Payment instance with all required fields
            payment = Payment(
                student=student,
                amount=form.cleaned_data['amount'],
                payment_method=form.cleaned_data.get('payment_method', 'CASH'),
                reference_number=form.cleaned_data.get('reference_number', ''),
                notes=form.cleaned_data.get('notes', ''),
                term=payment_term,
                recorded_by=self.request.user
            )
            
            # Don't call full_clean() - the model's clean() requires term to be set
            # Just validate the basics here
            if not payment.student:
                raise ValidationError("Student is required")
            if payment.amount is None or payment.amount < 0:
                raise ValidationError("Invalid amount")
            
            # Save the payment
            payment.save()
            
            # Check if student should be archived (graduated with all fees paid)
            student.check_and_archive()
            
            # The post_save signal automatically updates the student balance,
            # so we just need to fetch the updated balance for the success message
            balance = StudentBalance.objects.filter(
                student=student,
                term=current_term
            ).first()
            
            if balance:
                messages.success(
                    self.request, 
                    f"✓ Payment of ${payment.amount:.2f} recorded for {student.full_name}. "
                    f"Outstanding balance: ${balance.current_balance:.2f}"
                )
            
            self.object = payment
            return redirect(self.get_success_url())
            
        except ValidationError as e:
            form.add_error(None, f"Validation error: {str(e)}")
            return self.form_invalid(form)
        except Exception as e:
            import traceback
            traceback.print_exc()
            form.add_error(None, f"Error: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.request.GET.get('student')
        current_term = AcademicTerm.get_current_term()
        
        if not current_term:
            messages.warning(self.request, "⚠ No current term set. Please configure terms in Settings.")
        
        # Handle case where student_id is from POST form data (when form has errors)
        if not student_id and self.request.POST:
            student_id = self.request.POST.get('student')
        
        if student_id:
            try:
                student = Student.objects.get(id=student_id)
                balance = StudentBalance.initialize_term_balance(student, current_term) if current_term else None
                
                # Calculate TOTAL outstanding - ONLY current term balance (or latest if no current term)
                # Do NOT sum all balances from all terms - that would show accumulated fees incorrectly
                # Previous terms are already included as "previous_arrears" in the current term balance
                if balance and balance.current_balance > 0:
                    total_outstanding = float(balance.current_balance)
                else:
                    total_outstanding = 0.0
                
                # Determine payment priority - show total outstanding
                if total_outstanding > 0:
                    payment_priority = f"${total_outstanding:.2f} total outstanding"
                else:
                    payment_priority = "Fully paid"
                
                context.update({
                    'student': student,
                    'current_balance': balance.current_balance if balance else 0,
                    'term_fee': balance.term_fee if balance else 0,
                    'previous_arrears': balance.previous_arrears if balance else 0,
                    'amount_paid': balance.amount_paid if balance else 0,
                    'arrears_remaining': balance.arrears_remaining if balance else 0,
                    'term_fee_remaining': balance.term_fee_remaining if balance else 0,
                    'payment_priority': payment_priority,
                    'total_due': balance.total_due if balance else 0,
                    'total_outstanding': float(total_outstanding)
                })
            except Student.DoesNotExist:
                pass
        return context

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    ordering = ['-payment_date']
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        term_id = self.request.GET.get('term')
        student_id = self.request.GET.get('student')
        search_query = self.request.GET.get('search', '')

        if term_id:
            queryset = queryset.filter(term_id=term_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if search_query:
            # Search by student name (first name or surname)
            from django.db.models import Q
            queryset = queryset.filter(
                Q(student__first_name__icontains=search_query) |
                Q(student__surname__icontains=search_query)
            )

        return queryset.select_related('student', 'term')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['terms'] = AcademicTerm.objects.all()
        context['current_term'] = AcademicTerm.get_current_term()
        
        # Calculate summary statistics
        current_term = AcademicTerm.get_current_term()
        context['term_total'] = Payment.objects.filter(term=current_term).aggregate(
            total=Sum('amount'))['total'] or 0
        
        # Get payment status counts (using Python since term_fee is a property)
        balances = list(StudentBalance.objects.filter(term=current_term))
        fully_paid_count = sum(1 for b in balances if b.amount_paid >= (b.term_fee + b.previous_arrears))
        partial_paid_count = sum(1 for b in balances if 0 < b.amount_paid < (b.term_fee + b.previous_arrears))
        no_payment_count = sum(1 for b in balances if b.amount_paid == 0)
        
        context.update({
            'fully_paid': fully_paid_count,
            'partial_paid': partial_paid_count,
            'no_payment': no_payment_count,
        })
        
        return context

class StudentPaymentHistoryView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'payments/student_payment_history.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Get current term to filter out future terms
        current_term = AcademicTerm.get_current_term()
        
        # Get student balances UP TO AND INCLUDING current term only
        all_balances = StudentBalance.objects.filter(
            student=student
        ).select_related('term').order_by(
            'term__academic_year', 'term__term'
        )
        
        # Filter: Only show terms up to current term (past or current, not future)
        if current_term:
            all_balances = [
                b for b in all_balances 
                if (b.term.academic_year < current_term.academic_year or 
                    (b.term.academic_year == current_term.academic_year and b.term.term <= current_term.term))
            ]
        
        # Get ALL payments for the student (all time)
        all_payments = Payment.objects.filter(student=student).order_by(
            'term__academic_year', 'term__term', 'payment_date'
        ).select_related('term')
        
        # Build comprehensive payment history with running totals
        payment_history = []
        running_total_due = Decimal('0')  # Sum of term fees
        running_total_paid = Decimal('0')  # Sum of payments
        running_credits = Decimal('0')  # Track advance payments/credits
        
        for balance in all_balances:
            # Get all payments for this term
            term_payments = all_payments.filter(term=balance.term)
            
            # Add to running totals
            running_total_due += balance.term_fee  # Only count term fees, not arrears
            running_total_paid += balance.amount_paid
            
            # Check for credits (overpayment)
            term_due = balance.term_fee + balance.previous_arrears
            term_credit = Decimal('0')
            if balance.amount_paid > term_due:
                # Student overpaid - they have a credit
                term_credit = balance.amount_paid - term_due
                running_credits += term_credit
            
            # Calculate balance: what they owe after all payments and credits
            balance_owed = running_total_due - running_total_paid
            if balance_owed < 0:
                balance_owed = Decimal('0')  # Can't owe negative
            
            payment_history.append({
                'term': balance.term,
                'term_fee': balance.term_fee,
                'previous_arrears': balance.previous_arrears,
                'total_due': term_due,
                'amount_paid': balance.amount_paid,
                'credit': term_credit,  # New: overpayment for this term
                'balance': balance_owed,  # What they owe lifetime
                'payments_in_term': list(term_payments),
                'running_total_due': running_total_due,
                'running_total_paid': running_total_paid,
                'running_balance': balance_owed,
                'running_credits': running_credits if running_credits > 0 else Decimal('0'),
            })
        
        # Calculate summary statistics
        total_ever_due = sum([Decimal(str(b.term_fee)) for b in all_balances]) if all_balances else Decimal('0')
        # Use StudentBalance amount_paid instead of Payment records (more reliable)
        total_ever_paid = sum([Decimal(str(b.amount_paid)) for b in all_balances]) if all_balances else Decimal('0')
        
        # Final balance calculation: total fees - total paid
        # This works correctly when payment amounts represent actual cash paid per term
        overall_balance = total_ever_due - total_ever_paid
        if overall_balance < 0:
            overall_balance = Decimal('0')
        
        # Calculate collection rate
        collection_rate = Decimal('0')
        if total_ever_due > 0:
            collection_rate = (total_ever_paid / total_ever_due) * 100
        
        context.update({
            'payment_history': payment_history,
            'all_payments': all_payments,
            'total_ever_due': total_ever_due,
            'total_ever_paid': total_ever_paid,
            'overall_balance': overall_balance,
            'collection_rate': collection_rate,
            'running_credits': running_credits,
            'current_balance': StudentBalance.objects.filter(
                student=student,
                term=AcademicTerm.get_current_term()
            ).first(),
            'enrollment_date': student.date_enrolled,
            'years_count': len(set([b.term.academic_year for b in all_balances])) if all_balances else 0,
        })
        
        return context

class FeeDashboardView(LoginRequiredMixin, ListView):
    model = StudentBalance
    template_name = 'payments/fee_dashboard.html'
    context_object_name = 'balances'

    def get_queryset(self):
        current_term = AcademicTerm.get_current_term()
        
        # Auto-initialize balances for all active students if not yet created for this term
        if current_term:
            from core.models import Student
            for student in Student.objects.filter(is_active=True):
                StudentBalance.initialize_term_balance(student, current_term)
        
        return StudentBalance.objects.filter(term=current_term).select_related('student')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_term = AcademicTerm.get_current_term()
        
        # Payment statistics (using Python since term_fee is a property)
        balances = list(StudentBalance.objects.filter(term=current_term))
        total_expected = sum(b.term_fee + b.previous_arrears for b in balances) or 0
        
        total_collected = Payment.objects.filter(term=current_term).aggregate(
            total=Sum('amount'))['total'] or 0
        
        # Total outstanding (current balance) = sum of all current_balance amounts
        total_outstanding = sum(max(0, b.term_fee + b.previous_arrears - b.amount_paid) for b in balances) or 0
        
        context.update({
            'current_term': current_term,
            'total_expected': total_expected,
            'total_collected': total_collected,
            'collection_rate': (total_collected / total_expected * 100) if total_expected else 0,
            'total_arrears': total_outstanding
        })
        
        return context


@require_http_methods(["GET"])
def export_student_payment_history(request, student_id):
    """Export a student's complete payment history as PDF"""
    try:
        student = get_object_or_404(Student, id=student_id)
        
        # Get all payments
        all_payments = Payment.objects.filter(student=student).order_by('-created_at')
        
        # Get balance info
        current_term = AcademicTerm.get_current_term()
        balance = StudentBalance.initialize_term_balance(student, current_term)
        
        balance_info = {}
        if balance:
            balance_info = {
                'term_fee': float(balance.term_fee),
                'amount_paid': float(balance.amount_paid),
                'previous_arrears': float(balance.previous_arrears),
                'current_balance': float(balance.current_balance),
            }
        
        # Generate PDF
        pdf_buffer = PaymentHistoryReport.generate_student_payment_pdf(student, all_payments, balance_info)
        
        # Create response
        filename = f"payment_history_{student.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return create_pdf_response(pdf_buffer, filename)
        
    except Exception as e:
        return HttpResponse(f'Error exporting payment history: {str(e)}', status=400)


@require_http_methods(["GET"])
def export_fee_dashboard(request):
    """Export current term fee dashboard data as PDF"""
    try:
        current_term = AcademicTerm.get_current_term()
        if not current_term:
            return HttpResponse('No current term set', status=400)
        
        # Get all balances for the term
        balances = StudentBalance.objects.filter(term=current_term).select_related('student')
        
        # Prepare student data
        students_data = []
        for balance in balances:
            students_data.append({
                'name': balance.student.get_full_name(),
                'class': str(balance.student.current_class) if balance.student.current_class else 'N/A',
                'term_fee': float(balance.term_fee),
                'amount_paid': float(balance.amount_paid),
                'current_balance': float(balance.current_balance),
                'arrears_remaining': float(balance.arrears_remaining),
            })
        
        # Generate PDF
        pdf_buffer = PaymentHistoryReport.generate_fee_dashboard_pdf(str(current_term), students_data)
        
        # Create response
        filename = f"fee_dashboard_{datetime.now().strftime('%Y%m%d')}.pdf"
        return create_pdf_response(pdf_buffer, filename)
        
    except Exception as e:
        return HttpResponse(f'Error exporting fee dashboard: {str(e)}', status=400)


@require_http_methods(["GET"])
def arrears_report_pdf(request):
    """Export arrears report as PDF"""
    try:
        current_term = AcademicTerm.get_current_term()
        if not current_term:
            return HttpResponse('No current term set', status=400)
        
        # Get all balances for the term
        balances = StudentBalance.objects.filter(
            term=current_term
        ).select_related('student').order_by('-amount_paid')
        
        # Prepare arrears data - filter for those with outstanding balance
        students_with_arrears = []
        for balance in balances:
            # Use the property to calculate current_balance
            outstanding = balance.current_balance
            if outstanding > 0:
                students_with_arrears.append({
                    'name': balance.student.get_full_name(),
                    'id': balance.student.id,
                    'current_class': str(balance.student.current_class) if balance.student.current_class else 'N/A',
                    'balance': float(outstanding),
                })
        
        # Sort by balance descending
        students_with_arrears.sort(key=lambda x: x['balance'], reverse=True)
        
        # Generate PDF
        pdf_buffer = ArrearsReport.generate_arrears_pdf(students_with_arrears, term=str(current_term))
        
        # Create response
        filename = f"arrears_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        return create_pdf_response(pdf_buffer, filename)
        
    except Exception as e:
        return HttpResponse(f'Error exporting arrears report: {str(e)}', status=400)
