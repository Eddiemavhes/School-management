"""
Superuser Management Views
Allows superuser to manage admin credentials and system data
"""
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.core.management import call_command
from io import StringIO
from decimal import Decimal

from core.models.administrator import Administrator
from core.models.student import Student
from core.models.academic import Payment, AcademicTerm
from core.models.academic_year import AcademicYear
from core.models.fee import StudentBalance, TermFee
from core.models.class_model import Class
from core.models.school_details import SchoolDetails
from core.forms.admin_forms import ResetAdminPasswordForm


class IsSuperUserMixin(UserPassesTestMixin):
    """Mixin to check if user is superuser"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('superuser_login')
        messages.error(self.request, 'Access denied. Superuser privileges required.')
        return redirect('admin_dashboard')


class SuperuserDashboardView(IsSuperUserMixin, TemplateView):
    """Main superuser dashboard - minimal stats to avoid slowness"""
    template_name = 'superuser/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only show the dashboard - no statistics needed for performance
        return context


class ResetAdminPasswordView(IsSuperUserMixin, FormView):
    """Reset admin password"""
    form_class = ResetAdminPasswordForm
    template_name = 'superuser/reset_admin_password.html'
    success_url = reverse_lazy('superuser_dashboard')
    
    def form_valid(self, form):
        admin_id = form.cleaned_data['admin']
        new_password = form.cleaned_data['new_password']
        
        admin = Administrator.objects.get(id=admin_id)
        admin.set_password(new_password)
        admin.save()
        
        messages.success(
            self.request,
            f'Password reset for {admin.get_full_name()} successfully!'
        )
        return super().form_valid(form)


@login_required
@require_http_methods(["POST"])
def reset_system_api(request):
    """
    API endpoint to reset system data
    Clears all students, teachers, payments, balances, and terms
    BUT keeps administrator credentials intact
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        # Get confirmation token
        reset_token = request.POST.get('reset_token')
        if reset_token != 'CONFIRM_SYSTEM_RESET_2025':
            return JsonResponse({'error': 'Invalid confirmation token'}, status=400)
        
        # Count items before deletion
        stats = {
            'students': Student.objects.count(),
            'teachers': Administrator.objects.filter(is_teacher=True).count(),
            'payments': Payment.objects.count(),
            'balances': StudentBalance.objects.count(),
            'term_fees': TermFee.objects.count(),
            'terms': AcademicTerm.objects.count(),
            'classes': Class.objects.count(),
            'years': AcademicYear.objects.count(),
            'school_details': SchoolDetails.objects.count(),
        }
        
        # Delete in optimized order to avoid cascade issues
        # Delete payments first (they reference students and terms)
        Payment.objects.all().delete()
        # Delete student balances (they reference students and terms)
        StudentBalance.objects.all().delete()
        # Delete students (cascade will handle related records)
        Student.objects.all().delete()
        # Delete teachers (Administrator accounts with is_teacher=True)
        Administrator.objects.filter(is_teacher=True).delete()
        # Delete classes (they reference teachers and years)
        Class.objects.all().delete()
        # Delete term fees (reference terms and years)
        TermFee.objects.all().delete()
        # Delete academic terms (reference years)
        AcademicTerm.objects.all().delete()
        # Delete academic years
        AcademicYear.objects.all().delete()
        # Delete school details
        SchoolDetails.objects.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': 'System reset complete!',
            'stats': stats
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@login_required
@require_http_methods(["POST"])
def clear_payments_api(request):
    """Clear only payment-related data"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        reset_token = request.POST.get('reset_token')
        if reset_token != 'CONFIRM_PAYMENTS_CLEAR_2025':
            return JsonResponse({'error': 'Invalid confirmation token'}, status=400)
        
        stats = {
            'payments': Payment.objects.count(),
            'balances': StudentBalance.objects.count(),
        }
        
        Payment.objects.all().delete()
        StudentBalance.objects.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Payment data cleared!',
            'stats': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def clear_students_api(request):
    """Clear only student data"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        reset_token = request.POST.get('reset_token')
        if reset_token != 'CONFIRM_STUDENTS_CLEAR_2025':
            return JsonResponse({'error': 'Invalid confirmation token'}, status=400)
        
        # Also delete related payments and balances
        Payment.objects.all().delete()
        StudentBalance.objects.all().delete()
        
        count = Student.objects.count()
        Student.objects.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Student data cleared!',
            'stats': {'students': count}
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def clear_terms_api(request):
    """Clear only academic terms"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        reset_token = request.POST.get('reset_token')
        if reset_token != 'CONFIRM_TERMS_CLEAR_2025':
            return JsonResponse({'error': 'Invalid confirmation token'}, status=400)
        
        stats = {
            'term_fees': TermFee.objects.count(),
            'terms': AcademicTerm.objects.count(),
        }
        
        TermFee.objects.all().delete()
        AcademicTerm.objects.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Academic terms cleared!',
            'stats': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
