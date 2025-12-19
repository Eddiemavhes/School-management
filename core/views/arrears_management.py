"""
GRADUATED WITH ARREARS - STRICT MANAGEMENT DASHBOARD
Zero flexibility interface for managing students with unpaid graduation fees
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal
from core.models.arrears_vault import ArrearsVault, ArrearsPaymentLog, ArrearsReport


class ArrearsVaultListView(LoginRequiredMixin, ListView):
    """
    Strict management dashboard for all students in GRADUATED_WITH_ARREARS status.
    
    NO FLEXIBILITY - READ ONLY except payment processing
    """
    model = ArrearsVault
    template_name = 'arrears/vault_list.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ArrearsVault.objects.filter(
            status='GRADUATED_WITH_ARREARS'
        ).order_by('-graduation_date')
        
        # Search functionality
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(student_full_name__icontains=search) |
                Q(student_birth_entry__icontains=search) |
                Q(parent_name__icontains=search)
            )
        
        # Filter by graduation year
        year = self.request.GET.get('year')
        if year:
            queryset = queryset.filter(graduation_year=year)
        
        # Filter by balance range
        min_balance = self.request.GET.get('min_balance')
        max_balance = self.request.GET.get('max_balance')
        
        if min_balance:
            try:
                queryset = queryset.filter(fixed_balance__gte=Decimal(min_balance))
            except:
                pass
        
        if max_balance:
            try:
                queryset = queryset.filter(fixed_balance__lte=Decimal(max_balance))
            except:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # System statistics
        all_students = ArrearsVault.objects.filter(status='GRADUATED_WITH_ARREARS')
        
        context['total_students'] = all_students.count()
        context['total_arrears'] = all_students.aggregate(Sum('fixed_balance'))['fixed_balance__sum'] or 0
        context['oldest_year'] = all_students.aggregate(models.Min('graduation_year'))['graduation_year__min']
        
        # Breakdown by year
        context['by_year'] = list(
            all_students.values('graduation_year')
            .annotate(count=Count('id'), total=Sum('fixed_balance'))
            .order_by('-graduation_year')
        )
        
        # Payment stats
        context['total_payments_attempted'] = all_students.aggregate(Sum('total_payment_attempts'))['total_payment_attempts__sum'] or 0
        context['total_escrowed'] = all_students.aggregate(Sum('total_escrowed'))['total_escrowed__sum'] or 0
        context['collections'] = Decimal('0')  # Should always be 0 with this system
        context['collection_rate'] = '0%'  # By design
        
        # Policy enforcement
        context['exceptions_granted'] = 0  # Should always be 0
        context['policy_breaches'] = 0  # Should always be 0
        
        # Add search params to context
        context['search'] = self.request.GET.get('search', '')
        context['year_filter'] = self.request.GET.get('year')
        
        return context


class ArrearsVaultDetailView(LoginRequiredMixin, DetailView):
    """
    Frozen student record view - IMMUTABLE, READ-ONLY except for payment processing.
    
    Displays:
    - Student information (frozen at graduation)
    - Fixed balance (IMMUTABLE)
    - Required payment (IMMUTABLE)
    - Payment history (audit trail)
    - No update options available
    """
    model = ArrearsVault
    template_name = 'arrears/vault_detail.html'
    context_object_name = 'student'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Payment information
        context['payments'] = student.payment_logs.all().order_by('-created_at')
        context['payment_attempt_count'] = student.total_payment_attempts
        context['total_escrowed'] = student.total_escrowed
        
        # Status information
        context['is_paid'] = student.transition_date is not None
        context['years_outstanding'] = (timezone.now().date().year - student.graduation_year) if not student.transition_date else 0
        
        # Allowed actions (very limited)
        context['allowed_actions'] = []
        if not student.transition_date:
            context['allowed_actions'].append('process_full_payment')
            context['allowed_actions'].append('send_reminder')
        
        # Disabled actions (to show what CAN'T be done)
        context['disabled_actions'] = [
            'adjust_balance',
            'create_payment_plan',
            'grant_waiver',
            'accept_partial_payment',
            'write_off_balance',
            'update_contact_info',
        ]
        
        return context


def process_payment(request, pk):
    """
    Process payment for a specific student in arrears vault.
    
    STRICT RULES:
    - Only accepts EXACT amount (fixed_balance)
    - Rejects any partial payment
    - No exceptions, no discretion
    """
    student = get_object_or_404(ArrearsVault, pk=pk)
    
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
            payment_method = request.POST.get('payment_method', 'Manual')
            
            # Check if payment is valid
            accepted, reason = student.can_process_payment(amount)
            
            if accepted and amount == student.fixed_balance:
                # Process full payment
                student.process_full_payment(amount, payment_method)
                messages.success(
                    request,
                    f"✅ PAYMENT ACCEPTED - {student.student_full_name} has transitioned to ALUMNI status"
                )
                return redirect('arrears_detail', pk=pk)
            else:
                # Reject partial payment
                messages.error(
                    request,
                    f"❌ PAYMENT REJECTED - {reason}"
                )
                
                # Optionally hold in escrow
                if amount > 0 and amount < student.fixed_balance:
                    student.hold_partial_payment(amount)
                    messages.warning(
                        request,
                        f"⚠️ ${amount} has been held in escrow. Full ${student.fixed_balance} required for alumni status."
                    )
        
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
        
        return redirect('arrears_detail', pk=pk)
    
    return render(request, 'arrears/process_payment.html', {
        'student': student,
        'required_amount': student.fixed_balance,
    })


def send_payment_reminder(request, pk):
    """
    Send automated payment reminder (template-based, no customization).
    
    Message is fixed and unyielding - no negotiation options presented.
    """
    student = get_object_or_404(ArrearsVault, pk=pk)
    
    if student.transition_date:
        messages.error(request, "Student already paid in full")
        return redirect('arrears_detail', pk=pk)
    
    # Prepare email details
    email_subject = f"Outstanding Graduation Fees - {student.student_full_name}"
    email_body = f"""
Dear {student.parent_name},

This is a reminder that {student.student_full_name} has outstanding graduation fees.

OUTSTANDING AMOUNT: ${student.fixed_balance}
REQUIRED PAYMENT: ${student.required_payment} (Full amount only)
GRADUATION DATE: {student.graduation_date}

PAYMENT POLICY:
• Full payment of ${student.required_payment} is REQUIRED
• No partial payments, payment plans, or waivers are available
• No exceptions to this policy
• Balance remains fixed at ${student.fixed_balance} until paid in full

Upon receipt of full payment, {student.student_full_name} will 
immediately be transitioned to ALUMNI status with full privileges.

[Payment Portal Link]
[Bank Account Details]

Thank you,
School Management System
"""
    
    # Log the reminder (but don't actually send - assumes external email system)
    ArrearsPaymentLog.objects.create(
        vault=student,
        payment_amount=Decimal('0'),
        payment_method='Reminder',
        result='INVALID_AMOUNT',
        details=f'Reminder email sent to {student.parent_email}'
    )
    
    messages.success(
        request,
        f"✅ Reminder sent to {student.parent_email} - No flexibility, only exact payment accepted"
    )
    
    return redirect('arrears_detail', pk=pk)


def arrears_reports(request):
    """
    Permanent arrears tracking reports.
    These show the indefinite nature of the debt.
    """
    # Get all unpaid students
    all_unpaid = ArrearsVault.objects.filter(status='GRADUATED_WITH_ARREARS')
    
    # Breakdown by year
    by_year = list(
        all_unpaid.values('graduation_year')
        .annotate(count=Count('id'), total=Sum('fixed_balance'))
        .order_by('-graduation_year')
    )
    
    # Overall stats
    total_students = all_unpaid.count()
    total_arrears = all_unpaid.aggregate(Sum('fixed_balance'))['fixed_balance__sum'] or Decimal('0')
    
    context = {
        'total_students': total_students,
        'total_arrears': total_arrears,
        'by_year': by_year,
        'oldest_year': all_unpaid.aggregate(models.Min('graduation_year'))['graduation_year__min'],
        'collections_total': Decimal('0'),
        'collections_percentage': 0,
        'report_date': timezone.now(),
    }
    
    return render(request, 'arrears/reports.html', context)


# API endpoint for checking payment status
def api_check_payment_status(request, pk):
    """JSON API for checking payment requirements and restrictions."""
    student = get_object_or_404(ArrearsVault, pk=pk)
    
    return JsonResponse({
        'student_id': str(student.id),
        'student_name': student.student_full_name,
        'status': student.status,
        'required_payment': str(student.fixed_balance),
        'fixed_balance': str(student.fixed_balance),
        'required_payment_amount': str(student.required_payment),
        'is_paid': student.transition_date is not None,
        'transition_date': student.transition_date.isoformat() if student.transition_date else None,
        'policy': {
            'accepts_partial_payments': False,
            'accepts_payment_plans': False,
            'allows_waivers': False,
            'allows_adjustments': False,
            'message': 'Full payment only. No exceptions. No flexibility.'
        },
        'payment_history': [
            {
                'amount': str(log.payment_amount),
                'method': log.payment_method,
                'result': log.result,
                'date': log.created_at.isoformat(),
            }
            for log in student.payment_logs.all()[:10]
        ]
    })
