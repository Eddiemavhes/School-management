from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from ..models import Administrator
from ..models.class_model import Class
from ..models.student_movement import StudentMovement

class AdminLoginView(LoginView):
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # Route based on email:
        # admin@school.com -> superuser dashboard
        # admin@dashboard.com -> admin dashboard
        if self.request.user.email == 'admin@school.com':
            return reverse_lazy('superuser_dashboard')
        # All other admins go to admin dashboard
        return reverse_lazy('admin_dashboard')

    def form_valid(self, form):
        # Reset failed login attempts on successful login
        user = Administrator.objects.get(email=form.cleaned_data['username'])
        user.failed_login_attempts = 0
        user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        email = form.cleaned_data.get('username')
        if email:
            try:
                user = Administrator.objects.get(email=email)
                user.failed_login_attempts += 1
                user.last_failed_login = timezone.now()
                user.save()
            except Administrator.DoesNotExist:
                pass
        return super().form_invalid(form)


class SuperuserLoginView(LoginView):
    """Dedicated superuser login page"""
    template_name = 'superuser/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('superuser_dashboard')

    def form_valid(self, form):
        # Check if user is superuser
        user = Administrator.objects.get(email=form.cleaned_data['username'])
        if not user.is_superuser:
            form.add_error(None, 'This account does not have superuser privileges.')
            return self.form_invalid(form)
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        email = form.cleaned_data.get('username')
        if email:
            try:
                user = Administrator.objects.get(email=email)
                user.failed_login_attempts += 1
                user.last_failed_login = timezone.now()
                user.save()
            except Administrator.DoesNotExist:
                pass
        return super().form_invalid(form)


class AdminLogoutView(View):
    """Custom logout view that handles both GET and POST requests"""
    
    def get(self, request):
        logout(request)
        return redirect('login')
    
    def post(self, request):
        logout(request)
        return redirect('login')

@method_decorator(login_required, name='dispatch')
class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        
        # Get current active academic year
        from ..models import AcademicYear
        current_year = AcademicYear.objects.filter(is_active=True).first()
        
        # Get classes data and statistics - ONLY from current active year
        if current_year:
            classes = Class.objects.filter(academic_year=current_year.year)
        else:
            classes = Class.objects.none()
        
        total_classes = len(classes)
        class_distribution = [{
            'grade': cls.grade,
            'section': cls.section,
            'student_count': cls.student_count
        } for cls in classes]
        
        # Get teacher statistics
        total_teachers = Administrator.objects.filter(is_teacher=True).count()
        
        # Get student statistics
        total_students = sum(cls.student_count for cls in classes)
        
        # Calculate occupancy rate (assuming ideal class size of 30)
        ideal_capacity = total_classes * 30 if total_classes > 0 else 1
        occupancy_rate = round((total_students / ideal_capacity) * 100) if ideal_capacity > 0 else 0
        
        # Get recent movements for the promotion widget
        recent_movements = StudentMovement.objects.select_related(
            'student', 'from_class', 'to_class', 'moved_by'
        ).order_by('-movement_date')[:5]
        
        # Get recent students for the students widget
        from ..models.student import Student
        recent_students = Student.objects.select_related('current_class').order_by('-date_enrolled')[:5]
        
        # Get recent payments
        from ..models.academic import Payment
        recent_payments = Payment.objects.select_related('student', 'term').order_by('-payment_date')[:5]
        
        # Get current term
        from ..models.academic import AcademicTerm
        current_term = AcademicTerm.get_current_term()
        
        context.update({
            'total_classes': total_classes,
            'total_teachers': total_teachers,
            'total_students': total_students,
            'occupancy_rate': min(occupancy_rate, 100),  # Cap at 100%
            'recent_movements': recent_movements,  # Add recent movements to context
            'recent_students': recent_students,  # Add recent students to context
            'recent_payments': recent_payments,  # Add recent payments to context
            'class_distribution': class_distribution,  # Add class distribution data
            'current_term': current_term,  # Add current term to context
        })
        return context


def error_404(request, exception=None):
    """Custom 404 error page handler"""
    from django.shortcuts import render
    return render(request, '404.html', status=404)