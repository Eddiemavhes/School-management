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
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

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

        # Perform deletions using ORM within a transaction to ensure consistency
        errors = []
        try:
            with transaction.atomic():
                # Delete non-admin teacher accounts
                Administrator.objects.filter(is_teacher=True).delete()

                # Delete arrears import entries and batches
                from core.models.arrears_import import ArrearsImportEntry, ArrearsImportBatch
                ArrearsImportEntry.objects.all().delete()
                ArrearsImportBatch.objects.all().delete()

                # ZIMSEC and statistics
                try:
                    from core.models.zimsecresults import ZimsecResults
                    ZimsecResults.objects.all().delete()
                except Exception:
                    logger.debug('No ZimsecResults model or table present')

                try:
                    from core.models.grade7statistics import Grade7Statistics
                    Grade7Statistics.objects.all().delete()
                except Exception:
                    logger.debug('No Grade7Statistics model or table present')

                # ZIMSEC results must be deleted before students (protected foreign key)
                try:
                    from core.models.zimsec import ZimsecResults
                    ZimsecResults.objects.all().delete()
                except Exception:
                    logger.debug('No ZimsecResults model or table present')

                # Student movements, payments, balances
                from core.models.student_movement import StudentMovement
                StudentMovement.objects.all().delete()
                Payment.objects.all().delete()
                StudentBalance.objects.all().delete()

                # Term fees and students
                TermFee.objects.all().delete()
                Student.objects.all().delete()

                # Classes, terms, school details, years
                Class.objects.all().delete()
                AcademicTerm.objects.all().delete()
                SchoolDetails.objects.all().delete()
                AcademicYear.objects.all().delete()

        except Exception as e:
            logger.exception('Exception during system reset')
            errors.append(str(e))

        # Reset DB sequences for PostgreSQL or sqlite auto-increment
        try:
            with connection.cursor() as cursor:
                if 'sqlite' in db_engine.lower():
                    cursor.execute("PRAGMA writable_schema = 1")
                    # Update sqlite_sequence to 0 for common tables if present
                    cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name IN ('core_student','core_payment','core_class')")
                elif 'postgresql' in db_engine.lower():
                    seq_tables = ['core_student', 'core_payment', 'core_class', 'core_academicterm']
                    for tbl in seq_tables:
                        try:
                            cursor.execute("SELECT pg_catalog.setval(pg_get_serial_sequence(%s, 'id'), 1, false)", [tbl])
                        except Exception:
                            logger.debug('Could not reset seq for %s', tbl)
                elif 'mysql' in db_engine.lower() or 'mariadb' in db_engine.lower():
                    # Reset AUTO_INCREMENT for common tables
                    ai_tables = ['core_student', 'core_payment', 'core_class', 'core_academicterm']
                    for tbl in ai_tables:
                        try:
                            cursor.execute(f"ALTER TABLE {tbl} AUTO_INCREMENT = 1")
                        except Exception:
                            logger.debug('Could not reset AUTO_INCREMENT for %s', tbl)
                else:
                    logger.debug('DB engine not recognized for sequence reset: %s', db_engine)
        except Exception as e:
            logger.exception('Failed to reset DB sequences')
            errors.append(str(e))

        # Log the reset summary
        try:
            logger.info('System reset performed by %s; before=%s; errors=%s', request.user.email if hasattr(request.user, 'email') else str(request.user), stats_before, errors)
        except Exception:
            logger.debug('Could not write detailed reset log')

        # Verify admin data is intact
        admin_count = Administrator.objects.filter(is_teacher=False).count()
        superuser_count = Administrator.objects.filter(is_superuser=True, is_teacher=False).count()
        teacher_count = Administrator.objects.filter(is_teacher=True).count()

        result = {
            'success': True if not errors else False,
            'message': 'System reset completed' if not errors else 'System reset completed with errors',
            'stats_deleted': stats_before,
            'admins_remaining': admin_count,
            'superusers_remaining': superuser_count,
            'teachers_deleted': stats_before['teachers'],
            'teachers_remaining': teacher_count,
            'errors': errors,
        }

        status_code = 200 if not errors else 500
        return JsonResponse(result, status=status_code)
        
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
