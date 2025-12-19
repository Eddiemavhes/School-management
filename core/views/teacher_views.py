from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from core.models import Administrator, Class, AcademicTerm
from django.utils import timezone

class TeacherListView(LoginRequiredMixin, ListView):
    template_name = 'teachers/teacher_list.html'
    context_object_name = 'teachers'

    def get_queryset(self):
        queryset = Administrator.objects.filter(is_teacher=True)
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')
        class_filter = self.request.GET.get('class', '')

        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        if status_filter:
            queryset = queryset.filter(is_active=status_filter == 'active')

        if class_filter:
            queryset = queryset.filter(assigned_class__id=class_filter)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_term = AcademicTerm.get_current_term()
        if current_term:
            context['classes'] = Class.objects.filter(academic_year=current_term.academic_year).order_by('grade', 'section')
        else:
            context['classes'] = Class.objects.none()
        return context

class TeacherDetailView(LoginRequiredMixin, DetailView):
    template_name = 'teachers/teacher_detail.html'
    context_object_name = 'teacher'

    def get_queryset(self):
        return Administrator.objects.filter(is_teacher=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment_history'] = self.object.get_assignment_history()
        current_term = AcademicTerm.get_current_term()
        if current_term:
            context['available_classes'] = Class.objects.filter(academic_year=current_term.academic_year, teacher__isnull=True).order_by('grade', 'section')
        else:
            context['available_classes'] = Class.objects.none()
        return context

class TeacherCreateView(LoginRequiredMixin, CreateView):
    model = Administrator
    template_name = 'teachers/teacher_form.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number', 
              'specialization', 'qualification', 'is_active']
    success_url = reverse_lazy('teacher_list')

    def form_valid(self, form):
        form.instance.is_teacher = True
        messages.success(self.request, 'Teacher added successfully!')
        return super().form_valid(form)

class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = Administrator
    template_name = 'teachers/teacher_form.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number', 
              'specialization', 'qualification', 'is_active']
    success_url = reverse_lazy('teacher_list')

    def form_valid(self, form):
        messages.success(self.request, 'Teacher updated successfully!')
        return super().form_valid(form)

class TeacherDeleteView(LoginRequiredMixin, DeleteView):
    model = Administrator
    template_name = 'teachers/teacher_confirm_delete.html'
    success_url = reverse_lazy('teacher_list')
    context_object_name = 'teacher'

    def get_queryset(self):
        return Administrator.objects.filter(is_teacher=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.get_object()
        context['teacher'] = teacher
        return context

    def post(self, request, *args, **kwargs):
        teacher = self.get_object()
        if teacher.current_class:
            messages.error(request, 'Please unassign the teacher from their current class before deleting.')
            return redirect('teacher_detail', pk=teacher.id)
        messages.success(request, 'Teacher deleted successfully!')
        return super().delete(request, *args, **kwargs)

def assign_class(request, teacher_id):
    teacher = get_object_or_404(Administrator, id=teacher_id, is_teacher=True)
    class_id = request.POST.get('class_id')
    academic_year = request.POST.get('academic_year', timezone.now().year)

    if class_id:
        class_obj = get_object_or_404(Class, id=class_id)
        try:
            teacher.assign_to_class(class_obj, academic_year)
            messages.success(request, f'Teacher assigned to {class_obj} successfully!')
        except ValueError as e:
            messages.error(request, str(e))
    
    return redirect('teacher_detail', pk=teacher_id)

def unassign_class(request, teacher_id):
    """Unassign a teacher from their current class"""
    teacher = get_object_or_404(Administrator, id=teacher_id, is_teacher=True)
    
    # Find and deactivate the current active assignment
    current_assignment = teacher.assignment_history.filter(is_active=True).first()
    if current_assignment:
        current_assignment.is_active = False
        current_assignment.end_date = timezone.now().date()
        current_assignment.save()
        messages.success(request, f'Teacher unassigned from {current_assignment.class_assigned} successfully!')
    else:
        messages.warning(request, 'No active assignment found.')
    
    return redirect('teacher_detail', pk=teacher_id)