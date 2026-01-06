from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, F, Q
from django.utils import timezone
from datetime import timedelta
import json
from ..models import Student, Class, AcademicTerm, Payment, TermFee, Administrator
from ..models.fee import StudentBalance
from decimal import Decimal

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_term = AcademicTerm.get_current_term()

        # Student Statistics - use single aggregation query instead of multiple .count() calls
        student_stats = Student.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True))
        )
        context['total_students'] = student_stats['total'] or 0
        context['active_students'] = student_stats['active'] or 0
        context['inactive_students'] = context['total_students'] - context['active_students']

        # Teacher and Class Statistics - batch query
        teacher_stats = Administrator.objects.aggregate(
            total=Count('id', filter=Q(is_teacher=True)),
            active=Count('id', filter=Q(is_teacher=True, is_active=True))
        )
        class_count = Class.objects.count()
        context['total_classes'] = class_count
        context['total_teachers'] = teacher_stats['total'] or 0
        context['assigned_teachers'] = teacher_stats['active'] or 0
        context['unassigned_teachers'] = context['total_teachers'] - context['assigned_teachers']

        # Fee Collection Statistics - use StudentBalance (including arrears)
        current_balances = StudentBalance.objects.filter(term=current_term)
        context['current_term_fee'] = current_balances.aggregate(total=Sum('term_fee'))['total'] or Decimal('0')
        context['current_term_collected'] = current_balances.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
        context['current_term_outstanding'] = current_balances.aggregate(
            total=Sum(F('term_fee') + F('previous_arrears') - F('amount_paid'))
        )['total'] or Decimal('0')
        context['total_arrears'] = current_balances.aggregate(total=Sum('previous_arrears'))['total'] or Decimal('0')

        # Collection rate
        total_due = context['current_term_fee'] + context['total_arrears']
        context['collection_rate'] = (
            (float(context['current_term_collected']) / float(total_due) * 100) 
            if total_due > 0 else 0
        )

        # Arrears Calculations - combine with prefetch for better performance
        students_with_arrears = StudentBalance.objects.filter(
            term=current_term,
            previous_arrears__gt=0
        ).select_related('student').order_by('-previous_arrears')[:5]
        context['students_with_arrears'] = students_with_arrears
        
        # Get counts in single query
        arrears_counts = StudentBalance.objects.filter(term=current_term).aggregate(
            arrears_count=Count('id', filter=Q(previous_arrears__gt=0)),
            no_payment_count=Count('id', filter=Q(amount_paid=0))
        )
        context['students_in_arrears_count'] = arrears_counts['arrears_count'] or 0
        context['no_payment_count'] = arrears_counts['no_payment_count'] or 0
        
        # Students with no payment (highest priority)
        no_payment_students = StudentBalance.objects.filter(
            term=current_term,
            amount_paid=0
        ).select_related('student').order_by('student__surname')[:5]
        context['no_payment_students'] = no_payment_students

        # Recent Registrations
        context['recent_students'] = Student.objects.order_by('-date_enrolled')[:5]

        # Fee Collection Chart Data (Last 6 terms) - CRITICAL FIX: avoid N+1 queries
        term_labels = []
        term_collected = []
        term_due = []
        
        all_terms = list(AcademicTerm.objects.order_by('-academic_year', '-term')[:6])
        # Pre-fetch all balances for these terms in ONE query with aggregation
        term_aggregates = StudentBalance.objects.filter(
            term__in=all_terms
        ).values('term').annotate(
            total_collected=Sum('amount_paid'),
            total_due=Sum(F('term_fee') + F('previous_arrears'))
        )
        # Create lookup dict for O(1) access
        term_data = {agg['term']: agg for agg in term_aggregates}
        
        for term_obj in reversed(all_terms):
            agg = term_data.get(term_obj.id, {})
            collected = Decimal(str(agg.get('total_collected') or 0))
            due = Decimal(str(agg.get('total_due') or 0))
            
            term_labels.append(f"{term_obj.academic_year} T{term_obj.term}")
            term_collected.append(float(collected))
            term_due.append(float(due))

        context['fee_collection_labels'] = json.dumps(term_labels)
        context['term_collected'] = json.dumps(term_collected)
        context['term_due'] = json.dumps(term_due)

        # Class Distribution Chart
        class_stats = Class.objects.annotate(
            student_count=Count('students')
        ).values('grade', 'section', 'student_count').order_by('grade', 'section')
        
        context['class_distribution_labels'] = json.dumps([
            f"Grade {c['grade']} {c['section']}" for c in class_stats
        ])
        context['class_distribution_data'] = json.dumps([c['student_count'] for c in class_stats])

        # Outstanding Balance Distribution (for pie chart)
        # Calculate in Python since current_balance is a property
        all_balances = StudentBalance.objects.filter(term=current_term)
        paid_count = 0
        partial_count = 0
        unpaid_count = 0
        
        for balance in all_balances:
            if balance.current_balance <= 0:
                paid_count += 1
            elif balance.amount_paid > 0:
                partial_count += 1
            else:
                unpaid_count += 1
        
        context['balance_paid_count'] = paid_count
        context['balance_partial_count'] = partial_count
        context['balance_unpaid_count'] = unpaid_count
        
        return context


class ClassDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for a specific class with financial and demographic info"""
    template_name = 'dashboard/class_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get('class_id')
        current_term = AcademicTerm.get_current_term()
        
        try:
            class_obj = Class.objects.prefetch_related('students').get(id=class_id)
        except Class.DoesNotExist:
            context['error'] = 'Class not found'
            return context
        
        context['class_obj'] = class_obj
        students = class_obj.students.all()
        context['students'] = students
        context['total_students'] = students.count()
        
        # Payment Statistics for this class in current term
        class_balances = StudentBalance.objects.filter(
            term=current_term,
            student__current_class=class_obj
        )
        
        context['class_fee_collected'] = class_balances.aggregate(
            total=Sum('amount_paid')
        )['total'] or Decimal('0')
        context['class_fee_due'] = class_balances.aggregate(
            total=Sum(F('term_fee') + F('previous_arrears'))
        )['total'] or Decimal('0')
        context['class_fee_outstanding'] = class_balances.aggregate(
            total=Sum(F('term_fee') + F('previous_arrears') - F('amount_paid'))
        )['total'] or Decimal('0')
        context['class_total_arrears'] = class_balances.aggregate(
            total=Sum('previous_arrears')
        )['total'] or Decimal('0')
        
        # Collection rate for class
        context['class_collection_rate'] = (
            (float(context['class_fee_collected']) / float(context['class_fee_due']) * 100)
            if float(context['class_fee_due']) > 0 else 0
        )
        
        # Average balance per student including arrears
        if students.count() > 0:
            context['avg_balance_per_student'] = float(context['class_fee_outstanding']) / students.count()
            context['avg_arrears_per_student'] = float(context['class_total_arrears']) / students.count()
        else:
            context['avg_balance_per_student'] = 0
            context['avg_arrears_per_student'] = 0
        
        # Gender distribution
        male_count = students.filter(sex='M').count()
        female_count = students.filter(sex='F').count()
        context['gender_labels'] = json.dumps(['Male', 'Female'])
        context['gender_data'] = json.dumps([male_count, female_count])
        
        # Age distribution (if we have dates of birth)
        from datetime import date as date_class
        today = date_class.today()
        age_ranges = {
            '4-6': 0,
            '7-9': 0,
            '10-12': 0,
            '13-15': 0,
            '16+': 0
        }
        
        for student in students:
            if student.date_of_birth:
                age = (today - student.date_of_birth).days // 365
                if age <= 6:
                    age_ranges['4-6'] += 1
                elif age <= 9:
                    age_ranges['7-9'] += 1
                elif age <= 12:
                    age_ranges['10-12'] += 1
                elif age <= 15:
                    age_ranges['13-15'] += 1
                else:
                    age_ranges['16+'] += 1
        
        context['age_labels'] = json.dumps(list(age_ranges.keys()))
        context['age_data'] = json.dumps(list(age_ranges.values()))
        
        # Students needing attention (no payment or high arrears)
        context['students_needing_attention'] = class_balances.filter(
            Q(amount_paid=0) | Q(previous_arrears__gte=100)
        ).select_related('student').order_by('-previous_arrears')[:5]
        
        # Payment progress - calculate in Python since current_balance is a property
        fully_paid = 0
        partial_paid = 0
        unpaid = 0
        
        for balance in class_balances:
            if balance.current_balance <= 0:
                fully_paid += 1
            elif balance.amount_paid > 0:
                partial_paid += 1
            else:
                unpaid += 1
        
        context['fully_paid'] = fully_paid
        context['partial_paid'] = partial_paid
        context['unpaid'] = unpaid
        
        return context


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for a specific student with detailed financial history"""
    template_name = 'dashboard/student_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs.get('student_id')
        
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            context['error'] = 'Student not found'
            return context
        
        context['student'] = student
        current_term = AcademicTerm.get_current_term()
        
        # Current balance information
        current_balance_obj = None
        try:
            current_balance_obj = StudentBalance.objects.get(student=student, term=current_term)
            context['current_balance_obj'] = current_balance_obj
            context['current_balance'] = current_balance_obj.current_balance
            context['current_term_fee'] = current_balance_obj.term_fee
            context['current_arrears'] = current_balance_obj.previous_arrears
            context['current_total_due'] = current_balance_obj.total_due
            context['current_amount_paid'] = current_balance_obj.amount_paid
            context['payment_priority'] = current_balance_obj.payment_priority
            
            # Percentage progress
            if float(current_balance_obj.total_due) > 0:
                context['payment_progress'] = (
                    float(current_balance_obj.amount_paid) / float(current_balance_obj.total_due) * 100
                )
            else:
                context['payment_progress'] = 0
        except StudentBalance.DoesNotExist:
            context['current_balance'] = 0
            context['payment_progress'] = 0
        
        # All balances and payments
        all_balances = StudentBalance.objects.filter(student=student).order_by(
            'term__academic_year', 'term__term'
        ).select_related('term')
        
        all_payments = Payment.objects.filter(student=student).order_by(
            'term__academic_year', 'term__term', 'payment_date'
        ).select_related('term')
        
        context['all_balances'] = all_balances
        context['all_payments'] = all_payments
        
        # Historical summary
        total_due = all_balances.aggregate(
            total=Sum(F('term_fee') + F('previous_arrears'))
        )['total'] or Decimal('0')
        total_paid = all_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        context['total_ever_due'] = total_due
        context['total_ever_paid'] = total_paid
        context['lifetime_balance'] = total_due - total_paid
        context['collection_rate'] = (
            (float(total_paid) / float(total_due) * 100) if float(total_due) > 0 else 0
        )
        
        # Arrears timeline data
        arrears_timeline = []
        for balance in all_balances:
            arrears_timeline.append({
                'term': f"{balance.term.academic_year} T{balance.term.term}",
                'arrears': float(balance.previous_arrears),
                'balance': float(balance.current_balance)
            })
        
        context['arrears_timeline_labels'] = json.dumps([a['term'] for a in arrears_timeline])
        context['arrears_timeline_data'] = json.dumps([a['arrears'] for a in arrears_timeline])
        context['balance_timeline_data'] = json.dumps([a['balance'] for a in arrears_timeline])
        
        # Payment method distribution
        payment_methods = all_payments.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        context['payment_method_labels'] = json.dumps([
            p['payment_method'] for p in payment_methods
        ])
        context['payment_method_data'] = json.dumps([
            float(p['total']) for p in payment_methods
        ])
        
        # Upcoming term projection
        next_terms = AcademicTerm.objects.filter(
            Q(academic_year__gt=current_term.academic_year) |
            Q(academic_year=current_term.academic_year, term__gt=current_term.term)
        ).order_by('academic_year', 'term')[:2]
        
        context['projected_next_terms'] = []
        if current_balance_obj and next_terms.exists():
            # If there's outstanding balance now, it becomes arrears for next term
            next_arrears = max(Decimal('0'), current_balance_obj.current_balance)
            for next_term in next_terms:
                try:
                    next_fee = TermFee.objects.get(term=next_term).amount
                except:
                    next_fee = current_balance_obj.term_fee  # Assume same
                
                context['projected_next_terms'].append({
                    'term': f"{next_term.academic_year} T{next_term.term}",
                    'fee': float(next_fee),
                    'projected_arrears': float(next_arrears),
                    'projected_total': float(next_fee + next_arrears)
                })
        
        return context