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
                balances = StudentBalance.objects.filter(term=current_term)
                
                if balance_filter == 'paid':
                    # Students with zero balance: (term_fee + previous_arrears - amount_paid) <= 0
                    paid_student_ids = balances.annotate(
                        current_balance=F('term_fee') + F('previous_arrears') - F('amount_paid')
                    ).filter(
                        term_fee__gt=0,
                        current_balance__lte=0
                    ).values_list('student_id', flat=True)
                    queryset = queryset.filter(id__in=paid_student_ids)
                    
                elif balance_filter == 'partial':
                    # Students with partial payment (some paid but not all)
                    partial_student_ids = balances.annotate(
                        current_balance=F('term_fee') + F('previous_arrears') - F('amount_paid')
                    ).filter(
                        amount_paid__gt=0,
                        current_balance__gt=0
                    ).values_list('student_id', flat=True)
                    queryset = queryset.filter(id__in=partial_student_ids)
                    
                elif balance_filter == 'unpaid':
                    # Students with no payments
                    unpaid_student_ids = balances.annotate(
                        current_balance=F('term_fee') + F('previous_arrears') - F('amount_paid')
                    ).filter(
                        amount_paid=0,
                        current_balance__gt=0
                    ).values_list('student_id', flat=True)
                    queryset = queryset.filter(id__in=unpaid_student_ids)
                    
                elif balance_filter == 'arrears':
                    # Students with arrears (previous_arrears > 0)
                    arrears_student_ids = balances.filter(
                        previous_arrears__gt=0
                    ).values_list('student_id', flat=True)
                    queryset = queryset.filter(id__in=arrears_student_ids)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.all()
        context['current_term'] = AcademicTerm.get_current_term()
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
        context['classes'] = Class.objects.all()
        context['current_term'] = AcademicTerm.get_current_term()
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
        context['classes'] = Class.objects.all()
        context['current_term'] = AcademicTerm.get_current_term()
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
    student = get_object_or_404(Student, pk=pk)
    new_class_id = request.POST.get('new_class')
    
    if new_class_id:
        new_class = get_object_or_404(Class, id=new_class_id)
        student.transfer_to_class(new_class)
        messages.success(request, f'{student.full_name} transferred to {new_class.name} successfully!')
    
    return redirect('student_detail', pk=pk)


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
