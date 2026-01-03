from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.utils import timezone
from core.models import Student, Class, AcademicTerm, Payment
from core.models.fee import StudentBalance
from decimal import Decimal
from ..forms.student_forms import StudentForm

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 12

    def get_queryset(self):
        queryset = Student.objects.filter(is_archived=False)  # Exclude archived/alumni students
        search_query = self.request.GET.get('search', '')
        class_filter = self.request.GET.get('class', '')
        sex_filter = self.request.GET.get('sex', '')
        balance_filter = self.request.GET.get('balance', '')

        if search_query:
            queryset = queryset.filter(
                Q(surname__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(birth_entry_number__icontains=search_query)
            )

        if class_filter:
            queryset = queryset.filter(current_class_id=class_filter)

        if sex_filter:
            queryset = queryset.filter(sex=sex_filter)

        # Balance filtering - use StudentBalance model
        if balance_filter:
            current_term = AcademicTerm.get_current_term()
            if current_term:
                # Get all StudentBalance records for current term
                balances = list(StudentBalance.objects.filter(term=current_term))
                
                if balance_filter == 'paid':
                    # Students with zero balance: (term_fee + previous_arrears - amount_paid) <= 0
                    paid_student_ids = [
                        b.student_id for b in balances 
                        if (b.amount_paid >= (b.term_fee + b.previous_arrears))
                    ]
                    queryset = queryset.filter(id__in=paid_student_ids)
                    
                elif balance_filter == 'partial':
                    # Students with partial payment (some paid but not all)
                    partial_student_ids = [
                        b.student_id for b in balances 
                        if (0 < b.amount_paid < (b.term_fee + b.previous_arrears))
                    ]
                    queryset = queryset.filter(id__in=partial_student_ids)
                    
                elif balance_filter == 'unpaid':
                    # Students with no payments
                    unpaid_student_ids = [
                        b.student_id for b in balances 
                        if b.amount_paid == 0 and (b.term_fee + b.previous_arrears) > 0
                    ]
                    queryset = queryset.filter(id__in=unpaid_student_ids)
                    
                elif balance_filter == 'arrears':
                    # Students with arrears (previous_arrears > 0)
                    arrears_student_ids = [
                        b.student_id for b in balances 
                        if b.previous_arrears > 0
                    ]
                    queryset = queryset.filter(id__in=arrears_student_ids)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only show classes from current academic year
        current_term = AcademicTerm.get_current_term()
        if current_term:
            context['classes'] = Class.objects.filter(academic_year=current_term.academic_year).order_by('grade', 'section')
        else:
            context['classes'] = Class.objects.none()
        context['current_term'] = current_term
        context['filters'] = {
            'search': self.request.GET.get('search', ''),
            'class': self.request.GET.get('class', ''),
            'sex': self.request.GET.get('sex', ''),
            'balance': self.request.GET.get('balance', ''),
        }
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        current_term = AcademicTerm.get_current_term()
        
        # Get payment history
        all_payments = Payment.objects.filter(student=student).select_related('term')
        context['payment_history'] = all_payments
        context['current_term'] = current_term
        
        # Get StudentBalance for current term
        current_balance = StudentBalance.objects.filter(
            student=student,
            term=current_term
        ).first()
        context['current_balance'] = current_balance
        
        # Calculate payment progress for CURRENT TERM ONLY
        if current_balance:
            total_due = current_balance.total_due
            if total_due > 0:
                context['payment_progress'] = (
                    (total_due - current_balance.current_balance) / total_due * 100
                )
            else:
                context['payment_progress'] = 100
        else:
            context['payment_progress'] = 100
        
        # Use the Student model property for overall_balance (current term only, includes credits)
        context['overall_balance'] = student.overall_balance
            
        return context

class StudentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'students/student_form.html'
    form_class = StudentForm
    success_url = reverse_lazy('student_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_term = AcademicTerm.get_current_term()
        context['current_term'] = current_term
        if current_term:
            context['classes'] = Class.objects.filter(academic_year=current_term.academic_year).order_by('grade', 'section')
        else:
            context['classes'] = Class.objects.none()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Student registered successfully!')
        return super().form_valid(form)

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    template_name = 'students/student_form.html'
    form_class = StudentForm
    success_url = reverse_lazy('student_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_term = AcademicTerm.get_current_term()
        context['current_term'] = current_term
        if current_term:
            context['classes'] = Class.objects.filter(academic_year=current_term.academic_year).order_by('grade', 'section')
        else:
            context['classes'] = Class.objects.none()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Student information updated successfully!')
        return super().form_valid(form)

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        student_name = student.full_name
        
        # Soft delete - mark as deleted instead of hard delete
        student.is_deleted = True
        student.deleted_at = timezone.now()
        student.deleted_reason = 'Manually deleted by user'
        student.save()
        
        messages.success(
            request, 
            f'Student record "{student_name}" has been archived. Financial records are preserved for audit purposes.'
        )
        return redirect(self.success_url)

def transfer_student(request, pk):
    import json
    from django.http import JsonResponse
    
    student = get_object_or_404(Student, pk=pk)
    
    # Handle both JSON and form data
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            new_class_id = data.get('new_class_id')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    else:
        new_class_id = request.POST.get('new_class_id') or request.POST.get('new_class')
    
    if not new_class_id:
        error_msg = 'Please select a class to transfer the student to'
        if request.content_type == 'application/json':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('student_detail', pk=pk)
    
    try:
        new_class = get_object_or_404(Class, id=new_class_id)
        if not new_class:
            raise ValueError('Selected class not found')
        if student.current_class and new_class.grade != student.current_class.grade:
            raise ValueError(f'Cannot transfer to different grade. Student is in Grade {student.current_class.grade}, selected class is Grade {new_class.grade}')
        student.transfer_to_class(new_class)
        success_msg = f'{student.full_name} successfully transferred to Grade {new_class.grade}{new_class.section}'
        
        if request.content_type == 'application/json':
            return JsonResponse({'success': True, 'message': success_msg})
        messages.success(request, success_msg)
    except ValueError as e:
        error_msg = f'Transfer failed: {str(e)}'
        if request.content_type == 'application/json':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
    except Exception as e:
        error_msg = f'An error occurred during transfer: {str(e)}'
        if request.content_type == 'application/json':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
    
    if request.content_type == 'application/json':
        return JsonResponse({'success': True, 'message': 'Student transferred successfully'})
    return redirect('student_detail', pk=pk)


class GraduatedWithArrearsListView(LoginRequiredMixin, ListView):
    """View for managing graduated students who have NOT paid all their fees"""
    model = Student
    template_name = 'students/graduated_with_arrears.html'
    context_object_name = 'graduated_students'
    paginate_by = 12

    def get_queryset(self):
        # Students who are GRADUATED but NOT ARCHIVED (have outstanding arrears)
        queryset = Student.objects.filter(
            status='GRADUATED',
            is_archived=False
        ).order_by('-date_enrolled')
        
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(surname__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(birth_entry_number__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add statistics
        students = self.get_queryset()
        total_owed = Decimal('0')
        
        for student in students:
            balance = student.overall_balance
            # Ensure balance is Decimal
            if balance and balance > 0:
                total_owed += Decimal(str(balance))
        
        context['total_students'] = students.count()
        context['total_owed'] = total_owed
        context['average_owed'] = total_owed / Decimal(students.count()) if students.count() > 0 else Decimal('0')
        
        return context


class ArchivedStudentsListView(LoginRequiredMixin, ListView):
    """View for managing archived/alumni students who have graduated with paid arrears"""
    model = Student
    template_name = 'students/archived_students.html'
    context_object_name = 'archived_students'
    paginate_by = 12

    def get_queryset(self):
        queryset = Student.objects.filter(is_archived=True).order_by('-date_enrolled')
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(surname__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(birth_entry_number__icontains=search_query)
            )
        
        return queryset


class ArchivedStudentDeleteView(LoginRequiredMixin, DeleteView):
    """Soft-delete an archived student (financial records preserved for audit)"""
    model = Student
    template_name = 'students/archived_student_confirm_delete.html'
    success_url = reverse_lazy('archived_students')
    
    def get_queryset(self):
        return Student.objects.filter(is_archived=True)
    
    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        student_name = student.full_name
        
        # Soft delete - mark as deleted instead of hard delete
        student.is_deleted = True
        student.deleted_at = timezone.now()
        student.deleted_reason = 'Alumni record deleted by user'
        student.save()
        
        messages.success(
            request, 
            f'Alumni record "{student_name}" has been archived. Financial records are preserved in the system for audit purposes.'
        )
        return redirect(self.success_url)
