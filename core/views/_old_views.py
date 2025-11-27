from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils import timezone
from .models import Administrator

class AdminLoginView(LoginView):
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True

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

class AdminLogoutView(LogoutView):
    template_name = 'authentication/logout.html'
    next_page = reverse_lazy('login')

@method_decorator(login_required, name='dispatch')
class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        
        # Get class statistics
        from .models.class_model import Class
        total_classes = Class.objects.count()
        
        # Get teacher statistics
        total_teachers = Administrator.objects.filter(is_teacher=True).count()
        
        # Get student statistics
        total_students = 0
        for class_obj in Class.objects.all():
            total_students += class_obj.student_count
        
        # Calculate occupancy rate (assuming ideal class size of 30)
        ideal_capacity = total_classes * 30 if total_classes > 0 else 1
        occupancy_rate = round((total_students / ideal_capacity) * 100) if ideal_capacity > 0 else 0
        
        context.update({
            'total_classes': total_classes,
            'total_teachers': total_teachers,
            'total_students': total_students,
            'occupancy_rate': min(occupancy_rate, 100),  # Cap at 100%
        })
        return context
