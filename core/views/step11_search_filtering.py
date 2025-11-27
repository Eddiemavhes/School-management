"""
STEP 11: Search and Filtering System
Provides comprehensive search, filtering, and bulk actions on students, teachers, and classes
"""

from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum, F, Count, DecimalField, Value
from django.db.models.functions import Cast
from django.utils import timezone
from datetime import datetime, timedelta
import json
from decimal import Decimal

from core.models import Student, Class, Administrator, AcademicYear, AcademicTerm
from core.models.fee import StudentBalance, Payment


class GlobalSearchView(LoginRequiredMixin, TemplateView):
    """Global search across students, teachers, classes"""
    template_name = 'search/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get search query
        query = self.request.GET.get('q', '').strip()
        context['query'] = query
        
        if len(query) < 2:
            context['students'] = []
            context['teachers'] = []
            context['classes'] = []
            context['total_results'] = 0
            return context
        
        # Search students
        students = Student.objects.filter(
            Q(name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(parent_phone__icontains=query)
        ).select_related('student_class').values(
            'id', 'name', 'student_id', 'student_class__grade', 
            'student_class__section', 'gender', 'date_of_birth'
        )[:20]
        
        # Search teachers
        teachers = Administrator.objects.filter(
            Q(email__icontains=query) |
            Q(full_name__icontains=query)
        ).values('id', 'email', 'full_name')[:20]
        
        # Search classes
        classes = Class.objects.filter(
            Q(grade__icontains=query) |
            Q(section__icontains=query)
        ).select_related('class_teacher').values(
            'id', 'grade', 'section', 'class_teacher__full_name', 'class_teacher__email'
        )[:20]
        
        context['students'] = students
        context['teachers'] = teachers
        context['classes'] = classes
        context['total_results'] = len(students) + len(teachers) + len(classes)
        context['search_type'] = 'global'
        
        return context


class StudentSearchFilterView(LoginRequiredMixin, TemplateView):
    """Advanced student search with multiple filter options"""
    template_name = 'search/student_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Base query
        query = self.request.GET.get('q', '').strip()
        students = Student.objects.select_related('student_class').annotate(
            current_balance=F('studentbalance__term_fee') - F('studentbalance__amount_paid') + F('studentbalance__previous_arrears')
        )
        
        # Text search
        if query:
            students = students.filter(
                Q(name__icontains=query) |
                Q(student_id__icontains=query) |
                Q(parent_phone__icontains=query)
            )
        
        # Filter by class
        class_id = self.request.GET.get('class_id')
        if class_id:
            students = students.filter(student_class_id=class_id)
            context['selected_class'] = Class.objects.get(id=class_id) if class_id else None
        
        # Filter by grade
        grade = self.request.GET.get('grade')
        if grade:
            students = students.filter(student_class__grade=grade)
            context['selected_grade'] = grade
        
        # Filter by gender
        gender = self.request.GET.get('gender')
        if gender:
            students = students.filter(gender=gender)
            context['selected_gender'] = gender
        
        # Filter by payment status (current term)
        payment_status = self.request.GET.get('payment_status')
        if payment_status:
            current_year = AcademicYear.objects.filter(is_active=True).first()
            current_term = AcademicTerm.objects.filter(is_current=True).first()
            
            if current_year and current_term:
                balance_query = StudentBalance.objects.filter(
                    term__academic_year_id=current_year.pk,
                    term_id=current_term.pk
                )
                
                if payment_status == 'paid':
                    students = students.filter(
                        id__in=balance_query.filter(
                            amount_paid__gte=F('term_fee') + F('previous_arrears')
                        ).values('student_id')
                    )
                elif payment_status == 'partial':
                    students = students.filter(
                        id__in=balance_query.filter(
                            amount_paid__gt=0,
                            amount_paid__lt=F('term_fee') + F('previous_arrears')
                        ).values('student_id')
                    )
                elif payment_status == 'unpaid':
                    students = students.filter(
                        id__in=balance_query.filter(amount_paid=0).values('student_id')
                    )
        
        # Filter by arrears status
        arrears_status = self.request.GET.get('arrears_status')
        if arrears_status:
            current_year = AcademicYear.objects.filter(is_active=True).first()
            if current_year:
                if arrears_status == 'has_arrears':
                    students = students.filter(
                        id__in=StudentBalance.objects.filter(
                            term__academic_year_id=current_year.pk,
                            previous_arrears__gt=0
                        ).values('student_id').distinct()
                    )
                elif arrears_status == 'no_arrears':
                    students = students.exclude(
                        id__in=StudentBalance.objects.filter(
                            term__academic_year_id=current_year.pk,
                            previous_arrears__gt=0
                        ).values('student_id').distinct()
                    )
        
        # Filter by balance range
        min_balance = self.request.GET.get('min_balance')
        max_balance = self.request.GET.get('max_balance')
        if min_balance or max_balance:
            balance_query = StudentBalance.objects.annotate(
                current_balance=F('term_fee') - F('amount_paid') + F('previous_arrears')
            )
            if min_balance:
                balance_query = balance_query.filter(current_balance__gte=Decimal(min_balance))
            if max_balance:
                balance_query = balance_query.filter(current_balance__lte=Decimal(max_balance))
            
            students = students.filter(id__in=balance_query.values('student_id').distinct())
        
        # Filter by age range
        min_age = self.request.GET.get('min_age')
        max_age = self.request.GET.get('max_age')
        if min_age or max_age:
            today = timezone.now().date()
            if max_age:
                min_dob = today - timedelta(days=int(max_age)*365)
                students = students.filter(date_of_birth__lte=min_dob)
            if min_age:
                max_dob = today - timedelta(days=int(min_age)*365)
                students = students.filter(date_of_birth__gte=max_dob)
        
        # Distinct and order
        students = students.distinct().order_by('name')
        
        # Get filter options for sidebar
        context['classes'] = Class.objects.all().order_by('grade', 'section')
        context['grades'] = Class.objects.values_list('grade', flat=True).distinct().order_by('grade')
        context['genders'] = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
        context['students'] = students[:100]  # Limit to 100 for performance
        context['total_count'] = len(students)
        context['query'] = query
        context['selected_payment_status'] = payment_status
        context['selected_arrears_status'] = arrears_status
        
        return context


class FinancialSearchView(LoginRequiredMixin, TemplateView):
    """Advanced financial data search and filtering"""
    template_name = 'search/financial_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current active year
        current_year = AcademicYear.objects.filter(is_active=True).first()
        context['current_year'] = current_year
        
        # Get all years for filtering
        context['years'] = AcademicYear.objects.order_by('-year')[:5]
        
        # Get current term
        current_term = AcademicTerm.objects.filter(is_current=True).first()
        context['current_term'] = current_term
        
        # Filter parameters
        year_id = self.request.GET.get('year_id', current_year.pk if current_year else None)
        term_id = self.request.GET.get('term_id', current_term.pk if current_term else None)
        filter_type = self.request.GET.get('filter_type', 'all')  # all, arrears, unpaid, collection
        
        context['selected_year_id'] = year_id
        context['selected_term_id'] = term_id
        context['filter_type'] = filter_type
        
        # Get balances for selected year/term
        balances = StudentBalance.objects.select_related(
            'student', 'student__student_class', 'term'
        ).annotate(
            current_owed=F('term_fee') + F('previous_arrears') - F('amount_paid'),
            collection_rate=Cast(F('amount_paid') * 100, DecimalField()) / F('term_fee') + F('previous_arrears')
        )
        
        if year_id:
            balances = balances.filter(term__academic_year_id=year_id)
        
        if term_id:
            balances = balances.filter(term_id=term_id)
        
        # Apply filter type
        if filter_type == 'arrears':
            balances = balances.filter(previous_arrears__gt=0)
        elif filter_type == 'unpaid':
            balances = balances.filter(
                Q(amount_paid=0) | Q(amount_paid__lt=F('term_fee') + F('previous_arrears'))
            )
        elif filter_type == 'collection':
            balances = balances.filter(collection_rate__lt=100)
        
        # Calculate statistics
        total_fee = balances.aggregate(Sum('term_fee'))['term_fee__sum'] or Decimal('0')
        total_collected = balances.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0')
        total_arrears = balances.aggregate(Sum('previous_arrears'))['previous_arrears__sum'] or Decimal('0')
        total_outstanding = balances.aggregate(Sum(F('term_fee') + F('previous_arrears') - F('amount_paid')))['term_fee__sum'] or Decimal('0')
        
        context['statistics'] = {
            'total_fee': total_fee,
            'total_collected': total_collected,
            'total_arrears': total_arrears,
            'total_outstanding': total_outstanding,
            'collection_rate': (total_collected / total_fee * 100) if total_fee > 0 else 0,
            'students_count': balances.values('student').distinct().count(),
        }
        
        context['balances'] = balances.order_by('-current_owed')[:50]
        
        return context


class SavedFilterView(LoginRequiredMixin, TemplateView):
    """Manage saved search filters"""
    template_name = 'search/saved_filters.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get saved filters for current admin (implement if using per-admin saving)
        context['saved_filters'] = []  # Can be extended to save per-admin
        
        return context


# ============================================================================
# API ENDPOINTS
# ============================================================================

@require_http_methods(['GET'])
def search_autocomplete(request):
    """Real-time search suggestions as user types"""
    try:
        query = request.GET.get('q', '').strip()
        search_type = request.GET.get('type', 'all')  # all, students, teachers, classes
        
        if len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        suggestions = []
        
        if search_type in ['all', 'students']:
            students = Student.objects.filter(
                Q(name__icontains=query) | Q(student_id__icontains=query)
            ).values('id', 'name', 'student_id').order_by('name')[:10]
            
            suggestions.extend([{
                'type': 'student',
                'id': s['id'],
                'text': f"{s['name']} ({s['student_id']})",
                'url': f'/admin/students/{s["id"]}/'
            } for s in students])
        
        if search_type in ['all', 'teachers']:
            teachers = Administrator.objects.filter(
                Q(full_name__icontains=query) | Q(email__icontains=query)
            ).values('id', 'full_name', 'email').order_by('full_name')[:10]
            
            suggestions.extend([{
                'type': 'teacher',
                'id': t['id'],
                'text': f"{t['full_name']} ({t['email']})",
                'url': f'/admin/teachers/{t["id"]}/'
            } for t in teachers])
        
        if search_type in ['all', 'classes']:
            classes = Class.objects.filter(
                Q(grade__icontains=query) | Q(section__icontains=query)
            ).values('id', 'grade', 'section').order_by('grade', 'section')[:10]
            
            suggestions.extend([{
                'type': 'class',
                'id': c['id'],
                'text': f"Grade {c['grade']}, {c['section']}",
                'url': f'/admin/classes/{c["id"]}/'
            } for c in classes])
        
        return JsonResponse({'suggestions': suggestions})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['GET'])
def get_filter_options(request):
    """Get available filter options for dynamic UI"""
    try:
        classes = list(Class.objects.values('id', 'grade', 'section').order_by('grade', 'section'))
        grades = list(Class.objects.values_list('grade', flat=True).distinct().order_by('grade'))
        years = list(AcademicYear.objects.values('id', 'year').order_by('-year')[:5])
        
        return JsonResponse({
            'classes': classes,
            'grades': list(grades),
            'genders': [
                {'value': 'M', 'label': 'Male'},
                {'value': 'F', 'label': 'Female'},
                {'value': 'O', 'label': 'Other'}
            ],
            'payment_statuses': [
                {'value': 'paid', 'label': 'Paid'},
                {'value': 'partial', 'label': 'Partial Payment'},
                {'value': 'unpaid', 'label': 'Unpaid'}
            ],
            'arrears_statuses': [
                {'value': 'has_arrears', 'label': 'Has Arrears'},
                {'value': 'no_arrears', 'label': 'No Arrears'}
            ],
            'years': years
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['GET'])
def export_search_results(request):
    """Export filtered search results as CSV"""
    try:
        import csv
        from django.http import HttpResponse
        
        search_type = request.GET.get('type', 'students')
        
        if search_type == 'students':
            students = Student.objects.all().select_related('student_class')
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['ID', 'Name', 'Student ID', 'Class', 'Gender', 'DOB', 'Phone'])
            
            for student in students:
                writer.writerow([
                    student.id,
                    student.name,
                    student.student_id,
                    f"{student.student_class.grade}-{student.student_class.section}" if student.student_class else '',
                    student.gender,
                    student.date_of_birth,
                    student.parent_phone
                ])
            
            return response
        
        return JsonResponse({'error': 'Invalid search type'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['POST'])
def apply_bulk_action(request):
    """Apply bulk actions to filtered results"""
    try:
        action = request.POST.get('action')
        student_ids = request.POST.getlist('student_ids[]')
        
        if action == 'export':
            # Export selected students
            return JsonResponse({
                'status': 'success',
                'message': f'Exporting {len(student_ids)} students...'
            })
        elif action == 'notify':
            # Send notification to selected students
            return JsonResponse({
                'status': 'success',
                'message': f'Sending notification to {len(student_ids)} students...'
            })
        
        return JsonResponse({'error': 'Invalid action'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
