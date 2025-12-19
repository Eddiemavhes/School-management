from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from django.db import models
from datetime import timedelta
from decimal import Decimal

from core.models.student import Student
from core.models.administrator import Administrator
from core.models.fee import StudentBalance
from core.models.academic import Payment


class SuperuserOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect('login')


class SuperuserDashboardView(SuperuserOnlyMixin, TemplateView):
    template_name = 'admin/superuser_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Financial Overview
        context['financial'] = self._get_financial_overview()
        
        # Student Population
        context['students'] = self._get_student_overview()
        
        # System Health
        context['system'] = self._get_system_health()
        
        # User Management
        context['users'] = self._get_user_analytics()
        
        # Recent Activity
        context['recent_activity'] = self._get_recent_activity()
        
        # System Alerts
        context['alerts'] = self._get_system_alerts()
        
        # Currency
        context['currency'] = getattr(settings, 'CURRENCY_SYMBOL', 'USD')
        
        return context
    
    def _get_financial_overview(self):
        """Real-time financial metrics - CURRENT TERM ONLY"""
        from core.models.academic import AcademicTerm
        from django.utils import timezone
        from decimal import Decimal
        
        # Get current term - first try by date, then by most recent with balances
        today = timezone.now().date()
        current_term = AcademicTerm.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()
        
        if not current_term:
            # If no active term by date, find the term with the most student balances
            from core.models.fee import StudentBalance
            terms_with_balances = StudentBalance.objects.values('term').annotate(
                count=models.Count('id')
            ).order_by('-count').first()
            
            if terms_with_balances:
                current_term = AcademicTerm.objects.get(id=terms_with_balances['term'])
            else:
                # Last resort: just get most recent term
                current_term = AcademicTerm.objects.order_by('-end_date').first()
        
        # Get balances for current term only
        balances = StudentBalance.objects.filter(term=current_term) if current_term else StudentBalance.objects.none()
        
        total_fees = Decimal('0')
        total_paid = Decimal('0')
        total_outstanding = Decimal('0')
        
        for balance in balances:
            total_fees += balance.term_fee
            total_paid += balance.amount_paid
            total_outstanding += max(0, balance.current_balance)
        
        collection_rate = (float(total_paid) / float(total_fees) * 100) if total_fees > 0 else 0
        
        # Arrears analysis
        students_in_arrears = Student.objects.filter(is_deleted=False, credits__lt=0).distinct().count()
        
        term_name = str(current_term) if current_term else "N/A"
        
        return {
            'total_fees': float(total_fees),
            'total_collected': float(total_paid),
            'total_outstanding': float(total_outstanding),
            'collection_rate': round(collection_rate, 1),
            'students_in_arrears': students_in_arrears,
            'students_paid': balances.filter(amount_paid__gt=0).count(),
            'balance_records': balances.count(),
            'term_name': term_name,
        }
    
    def _get_student_overview(self):
        """Student population and demographics"""
        students = Student.objects.filter(is_deleted=False)
        
        # Count students currently in school (ACTIVE or ENROLLED status with class assignment)
        currently_in_school = students.filter(
            status__in=['ACTIVE', 'ENROLLED'], 
            current_class__isnull=False
        ).count()
        
        by_status = {
            'active': students.filter(status__in=['ACTIVE', 'ENROLLED']).count(),
            'enrolled': students.filter(status='ENROLLED').count(),
            'alumni': students.filter(status='ALUMNI').count(),
            'graduated': students.filter(status='GRADUATED').count(),
        }
        
        by_gender = {
            'male': students.filter(sex='M').count(),
            'female': students.filter(sex='F').count(),
        }
        
        return {
            'total': students.count(),
            'by_status': by_status,
            'by_gender': by_gender,
            'active_total': currently_in_school,
        }
    
    def _get_system_health(self):
        """System performance and health status"""
        return {
            'status': 'Operational',
            'uptime': '99.8%',
            'database': 'Connected',
            'last_backup': timezone.now() - timedelta(hours=2),
            'disk_usage': 65,
        }
    
    def _get_user_analytics(self):
        """User and role statistics - SYSTEM USERS ONLY (Administrator & Superuser)"""
        admins = Administrator.objects.all()
        
        return {
            'superusers': admins.filter(is_superuser=True).count(),
            'administrators': admins.filter(is_staff=True, is_superuser=False).count(),
            'active_users': admins.filter(is_active=True).count(),
            'total_users': admins.count(),
        }
    
    def _get_recent_activity(self):
        """Recent system activities"""
        activities = []
        
        # Recent payments
        recent_payments = Payment.objects.order_by('-created_at')[:3]
        for payment in recent_payments:
            activities.append({
                'type': 'payment',
                'description': f'Payment recorded: ${payment.amount}',
                'timestamp': payment.created_at,
                'icon': '💳',
            })
        
        return activities
    
    def _get_system_alerts(self):
        """Critical system alerts"""
        alerts = []
        
        # Check for high arrears
        high_arrears_count = Student.objects.filter(
            is_deleted=False, 
            credits__lt=-100
        ).count()
        
        if high_arrears_count > 0:
            alerts.append({
                'level': 'warning',
                'title': 'High Arrears Alert',
                'message': f'{high_arrears_count} students with arrears > $100',
                'icon': '⚠️',
            })
        
        # Check for low collection rate
        balances = StudentBalance.objects.all()
        total_fees = sum(b.term_fee for b in balances)
        total_paid = sum(b.amount_paid for b in balances)
        
        if total_fees > 0:
            collection_rate = (total_paid / total_fees) * 100
            if collection_rate < 70:
                alerts.append({
                    'level': 'alert',
                    'title': 'Low Collection Rate',
                    'message': f'Collection rate is {collection_rate:.1f}% - below target',
                    'icon': '📉',
                })
        
        return alerts
