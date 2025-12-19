"""
System Administration Views
Allows superuser to reset system, manage passwords, and configure settings
"""
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import make_password
from django.db import connection

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
        # messages.error(self.request, 'Access denied. Superuser privileges required.')
        return redirect('superuser_dashboard')


class SystemAdministrationView(IsSuperUserMixin, TemplateView):
    """Main system administration interface"""
    template_name = 'admin/system_administration.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get system statistics
        context['stats'] = {
            'students': Student.objects.filter(is_deleted=False).count(),
            'payments': Payment.objects.count(),
            'balances': StudentBalance.objects.count(),
            'terms': AcademicTerm.objects.count(),
            'classes': Class.objects.count(),
            'years': AcademicYear.objects.count(),
            'teachers': Administrator.objects.filter(is_teacher=True).count(),
            'admins': Administrator.objects.filter(is_teacher=False).count(),
            'superusers': Administrator.objects.filter(is_superuser=True, is_teacher=False).count(),
        }
        
        # Get ONLY admin users (NOT teachers) for password reset
        context['admin_users'] = Administrator.objects.filter(is_teacher=False).order_by('first_name', 'last_name')
        context['password_reset_form'] = ResetAdminPasswordForm()
        
        return context


class ResetAdminPasswordView(IsSuperUserMixin, FormView):
    """Reset admin user password"""
    template_name = 'admin/reset_password.html'
    form_class = ResetAdminPasswordForm
    success_url = reverse_lazy('system_admin')
    
    def form_valid(self, form):
        admin = form.cleaned_data['admin']
        new_password = form.cleaned_data['new_password']
        
        try:
            admin.set_password(new_password)
            admin.save()
            name = f"{admin.first_name} {admin.last_name}" if admin.first_name else admin.email
            # messages.success(self.request, f'Password for {name} has been reset successfully.')
            return redirect(self.success_url)
        except Exception as e:
            # messages.error(self.request, f'Error resetting password: {str(e)}')
            return self.form_invalid(form)


def reset_system_data(request):
    """
    API endpoint to reset all system data EXCEPT admin credentials
    Clears students, payments, balances, terms, classes, etc.
    """
    if not request.user.is_superuser or request.method != 'POST':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        # Get confirmation token
        reset_token = request.POST.get('reset_token')
        if reset_token != 'CONFIRM_SYSTEM_RESET_2025':
            return JsonResponse({'error': 'Invalid confirmation token'}, status=400)
        
        from django.conf import settings
        
        db_engine = settings.DATABASES['default']['ENGINE']
        
        # Count items before deletion for report
        stats_before = {
            'students': Student.objects.count(),
            'payments': Payment.objects.count(),
            'balances': StudentBalance.objects.count(),
            'term_fees': TermFee.objects.count(),
            'terms': AcademicTerm.objects.count(),
            'classes': Class.objects.count(),
            'years': AcademicYear.objects.count(),
            'school_details': SchoolDetails.objects.count(),
            'teachers': Administrator.objects.filter(is_teacher=True).count(),
        }
        
        # STEP 1: Disable foreign key constraints
        with connection.cursor() as cursor:
            if 'mysql' in db_engine.lower():
                cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            elif 'postgresql' in db_engine.lower():
                cursor.execute("SET CONSTRAINTS ALL DEFERRED")
            elif 'sqlite' in db_engine.lower():
                cursor.execute("PRAGMA foreign_keys=OFF")
        
        # STEP 2: Delete teachers (they are NOT system admins) using ORM
        try:
            Administrator.objects.filter(is_teacher=True).delete()
        except Exception as e:
            print(f"Error deleting teachers: {e}")
        
        # STEP 3: Delete all other non-admin data using raw SQL (in dependency order)
        with connection.cursor() as cursor:
            tables_to_delete = [
                'core_zimsecresults',
                'core_grade7statistics',
                'core_studentmovement',
                'core_payment',
                'core_studentbalance',
                'core_termfee',
                'core_student',
                'core_class',
                'core_academicterm',
                'core_schooldetails',
                'core_academicyear',
                'core_arrearsimportentry',
                'core_arrearsimportbatch',
            ]
            
            for table in tables_to_delete:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                except Exception as e:
                    print(f"Error deleting {table}: {e}")
        
        # STEP 4: Reset auto-increment for SQLite
        if 'sqlite' in db_engine.lower():
            with connection.cursor() as cursor:
                cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name IN ('core_student', 'core_payment', 'core_class')")
        
        # STEP 5: Re-enable foreign key constraints
        with connection.cursor() as cursor:
            if 'mysql' in db_engine.lower():
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            elif 'postgresql' in db_engine.lower():
                cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            elif 'sqlite' in db_engine.lower():
                cursor.execute("PRAGMA foreign_keys=ON")
        
        # STEP 6: Verify admin data is intact (teachers should be gone)
        admin_count = Administrator.objects.filter(is_teacher=False).count()
        superuser_count = Administrator.objects.filter(is_superuser=True, is_teacher=False).count()
        teacher_count = Administrator.objects.filter(is_teacher=True).count()
        
        return JsonResponse({
            'success': True,
            'message': 'System reset completed successfully. All teachers deleted.',
            'stats_deleted': stats_before,
            'admins_remaining': admin_count,
            'superusers_remaining': superuser_count,
            'teachers_deleted': stats_before['teachers'],
            'teachers_remaining': teacher_count,
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Reset failed: {str(e)}',
            'success': False
        }, status=500)


def clear_student_data(request):
    """Clear only student-related data"""
    if not request.user.is_superuser or request.method != 'POST':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        reset_token = request.POST.get('reset_token')
        if reset_token != 'CONFIRM_CLEAR_STUDENTS_2025':
            return JsonResponse({'error': 'Invalid confirmation token'}, status=400)
        
        student_count = Student.objects.count()
        balance_count = StudentBalance.objects.count()
        
        # Delete in order
        StudentBalance.objects.all().delete()
        Student.objects.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Cleared {student_count} students and {balance_count} balances',
            'students_deleted': student_count,
            'balances_deleted': balance_count,
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Clear failed: {str(e)}',
            'success': False
        }, status=500)


def clear_payment_data(request):
    """Clear only payment records"""
    if not request.user.is_superuser or request.method != 'POST':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        reset_token = request.POST.get('reset_token')
        if reset_token != 'CONFIRM_CLEAR_PAYMENTS_2025':
            return JsonResponse({'error': 'Invalid confirmation token'}, status=400)
        
        payment_count = Payment.objects.count()
        Payment.objects.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Cleared {payment_count} payment records',
            'payments_deleted': payment_count,
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Clear failed: {str(e)}',
            'success': False
        }, status=500)
