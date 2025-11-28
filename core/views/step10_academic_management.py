"""
STEP 10: Academic Year and Term Management with Arrears Handling
Provides comprehensive academic calendar management, timeline visualization,
fee configuration, active year/term selection, and year-rollover wizard
"""

from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, F, Count
from django.utils import timezone
from datetime import timedelta, date
import json
import csv
from io import StringIO

from core.models import AcademicYear, AcademicTerm, TermFee, Student, Class
from core.models.fee import StudentBalance
from core.models.academic import Payment
from core.models.student_movement import StudentMovement

class AcademicCalendarView(LoginRequiredMixin, TemplateView):
    """Interactive timeline view of academic calendar"""
    template_name = 'academic/calendar_timeline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current and future years
        years = AcademicYear.objects.order_by('year')[:5]
        context['academic_years'] = years
        context['current_year'] = AcademicYear.get_current_year()
        
        # Build timeline data
        timeline_data = []
        for year in years:
            year_data = {
                'year': year.year,
                'id': year.id,
                'start_date': year.start_date.isoformat(),
                'end_date': year.end_date.isoformat(),
                'is_active': year.is_active,
                'is_current': year == context['current_year'],
                'terms': []
            }
            
            for term in year.get_terms():
                term_fee = TermFee.objects.filter(term=term).first()
                term_data = {
                    'term_num': term.term,
                    'name': f"Term {term.term}",
                    'start_date': term.start_date.isoformat(),
                    'end_date': term.end_date.isoformat(),
                    'is_current': term.is_current,
                    'fee': float(term_fee.amount) if term_fee else 0,
                    'days_until_start': (term.start_date - date.today()).days,
                }
                year_data['terms'].append(term_data)
            
            timeline_data.append(year_data)
        
        context['timeline_json'] = json.dumps(timeline_data)
        
        return context


class FeeConfigurationView(LoginRequiredMixin, TemplateView):
    """Fee settings panel with term-by-term configuration"""
    template_name = 'academic/fee_configuration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['current_year'] = AcademicYear.get_current_year()
        context['all_years'] = AcademicYear.objects.order_by('-year')[:5]
        
        # Get fee structure for each year
        years_with_fees = []
        for year in context['all_years']:
            year_fees = {
                'year': year,
                'terms': [],
                'total_fees': 0
            }
            
            for term in year.get_terms():
                term_fee = TermFee.objects.filter(term=term).first()
                amount = float(term_fee.amount) if term_fee else 0
                
                # Check if this term has payments
                from core.models.academic import Payment
                has_payments = Payment.objects.filter(term=term).exists()
                
                year_fees['terms'].append({
                    'term': term,
                    'fee_obj': term_fee,
                    'amount': amount,
                    'has_payments': has_payments,
                })
                year_fees['total_fees'] += amount
            
            years_with_fees.append(year_fees)
        
        context['years_with_fees'] = years_with_fees
        
        return context


class ActiveYearTermView(LoginRequiredMixin, TemplateView):
    """Manage active year and active term with clear visual status"""
    template_name = 'academic/active_year_term.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['current_year'] = AcademicYear.get_current_year()
        context['current_term'] = AcademicTerm.get_current_term()
        context['all_years'] = AcademicYear.objects.order_by('-year')
        context['all_terms'] = AcademicTerm.objects.order_by('-academic_year', '-term')[:10]
        
        # Year status indicators
        context['year_status'] = []
        for year in AcademicYear.objects.order_by('-year')[:5]:
            status = {
                'year': year,
                'is_active': year.is_active,
                'term_count': year.get_terms().count(),
                'financial_summary': year.get_financial_summary(),
                'student_count': StudentMovement.objects.filter(
                    new_class__academic_year=year.year
                ).values('student').distinct().count(),
            }
            context['year_status'].append(status)
        
        # Term status indicators
        context['term_status'] = []
        for term in AcademicTerm.objects.order_by('-academic_year', '-term')[:12]:
            term_fee = TermFee.objects.filter(term=term).first()
            balances = StudentBalance.objects.filter(term=term)
            
            status = {
                'term': term,
                'is_current': term.is_current,
                'fee': float(term_fee.amount) if term_fee else 0,
                'student_count': balances.count(),
                'collection_rate': (
                    (balances.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0) /
                    (balances.aggregate(Sum(F('term_fee') + F('previous_arrears')))['term_fee__sum'] or 1) * 100
                ) if balances.count() > 0 else 0,
                'total_due': balances.aggregate(
                    total=Sum(F('term_fee') + F('previous_arrears'))
                )['total'] or 0,
            }
            context['term_status'].append(status)
        
        return context


class RolloverWizardView(LoginRequiredMixin, TemplateView):
    """Year rollover wizard with confirmation of arrears preservation"""
    template_name = 'academic/rollover_wizard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['current_year'] = AcademicYear.get_current_year()
        
        if context['current_year']:
            # Pre-rollover checks
            new_year_num = context['current_year'].year + 1
            new_year_exists = AcademicYear.objects.filter(year=new_year_num).exists()
            
            # Count students to be promoted
            students_to_promote = Student.objects.filter(
                is_active=True,
                current_class__isnull=False,
                current_class__grade__lt=7
            ).count()
            
            # Calculate total arrears
            total_arrears = StudentBalance.objects.filter(
                term__academic_year=context['current_year'].year
            ).aggregate(
                arrears=Sum(F('term_fee') + F('previous_arrears') - F('amount_paid'))
            )['arrears'] or 0
            
            # Get fee structure from current year
            current_fee_structure = []
            for term in context['current_year'].get_terms():
                term_fee = TermFee.objects.filter(term=term).first()
                current_fee_structure.append({
                    'term': term.term,
                    'fee': float(term_fee.amount) if term_fee else 0,
                })
            
            # Get required classes for new year
            classes_by_grade = {}
            for student in Student.objects.filter(
                is_active=True,
                current_class__isnull=False,
                current_class__grade__lt=8
            ):
                next_grade = student.current_class.grade + 1
                section = student.current_class.section
                key = f"{next_grade}{section}"
                
                if key not in classes_by_grade:
                    classes_by_grade[key] = {
                        'grade': next_grade,
                        'section': section,
                        'exists': False,
                        'count': 0
                    }
                classes_by_grade[key]['count'] += 1
            
            # Check which classes exist in new year
            if not new_year_exists:
                for key, class_info in classes_by_grade.items():
                    exists = Class.objects.filter(
                        grade=class_info['grade'],
                        section=class_info['section'],
                        academic_year=new_year_num
                    ).exists()
                    class_info['exists'] = exists
            
            context['rollover_info'] = {
                'new_year': new_year_num,
                'new_year_exists': new_year_exists,
                'students_to_promote': students_to_promote,
                'students_graduating': Student.objects.filter(
                    is_active=True,
                    current_class__isnull=False,
                    current_class__grade=8
                ).count(),
                'total_arrears': float(total_arrears),
                'fee_structure': current_fee_structure,
                'required_classes': list(classes_by_grade.values()),
                'all_classes_ready': all(c['exists'] for c in classes_by_grade.values()) or new_year_exists,
                'balances_count': StudentBalance.objects.filter(
                    term__academic_year=context['current_year'].year
                ).count(),
            }
        
        return context


class YearComparisonView(LoginRequiredMixin, TemplateView):
    """Compare fee structures and financial metrics across years"""
    template_name = 'academic/year_comparison.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get last 5 years
        years = AcademicYear.objects.order_by('-year')[:5]
        
        # Build comparison data
        comparison_data = []
        for year in years:
            year_data = {
                'year': year.year,
                'id': year.id,
                'is_active': year.is_active,
                'financial_summary': year.get_financial_summary(),
                'terms_fees': []
            }
            
            for term in year.get_terms():
                term_fee = TermFee.objects.filter(term=term).first()
                year_data['terms_fees'].append({
                    'term': term.term,
                    'fee': float(term_fee.amount) if term_fee else 0,
                })
            
            comparison_data.append(year_data)
        
        context['years'] = years
        context['comparison_data'] = comparison_data
        context['comparison_json'] = json.dumps(comparison_data)
        
        return context


# API Endpoints for academic management

@require_http_methods(["POST"])
def set_active_year_api(request, year_id):
    """Set active academic year"""
    try:
        year = AcademicYear.objects.get(id=year_id)
        year.activate()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Academic Year {year.year} is now active'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
def set_current_term_api(request, term_id):
    """Set current academic term"""
    try:
        term = AcademicTerm.objects.get(id=term_id)
        AcademicTerm.objects.all().update(is_current=False)
        term.is_current = True
        term.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'{term.academic_year} Term {term.term} is now current'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
def update_term_fee_api(request, term_id):
    """Update term fee amount (or create if doesn't exist)"""
    try:
        data = json.loads(request.body)
        
        # Get the term first
        term = AcademicTerm.objects.get(id=term_id)
        
        # Check if TermFee exists
        try:
            term_fee = TermFee.objects.get(term_id=term_id)
            created = False
            old_amount = term_fee.amount
        except TermFee.DoesNotExist:
            term_fee = TermFee(term_id=term_id)
            created = True
            old_amount = None
        
        # Handle amount - convert to Decimal, allow 0 or empty
        amount_value = data.get('amount', 0)
        if amount_value == '' or amount_value is None:
            amount_value = 0
        
        term_fee.amount = amount_value
        term_fee.save()
        
        if created:
            message = f'Fee created: ${term_fee.amount}'
        else:
            message = f'Fee updated from ${old_amount} to ${term_fee.amount}'
        
        return JsonResponse({
            'status': 'success',
            'message': message
        })
    except AcademicTerm.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Term not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
def update_term_dates_api(request, term_id):
    """Update term start and end dates"""
    try:
        data = json.loads(request.body)
        term = AcademicTerm.objects.get(id=term_id)
        
        old_start = term.start_date
        old_end = term.end_date
        
        term.start_date = data.get('start_date', term.start_date)
        term.end_date = data.get('end_date', term.end_date)
        term.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Term dates updated from {old_start} - {old_end} to {term.start_date} - {term.end_date}'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
def rollover_year_api(request, year_id):
    """Execute academic year rollover with arrears preservation"""
    try:
        current_year = AcademicYear.objects.get(id=year_id)
        
        # Validate rollover can proceed
        current_year._validate_rollover()
        
        # Execute rollover
        new_year = current_year.rollover_to_new_year()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Successfully rolled over to {new_year.year}',
            'new_year_id': new_year.id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
def verify_arrears_before_rollover(request, year_id):
    """Verify and report arrears before rollover"""
    try:
        year = AcademicYear.objects.get(id=year_id)
        
        # Get arrears details
        balances = StudentBalance.objects.filter(term__academic_year=year.year)
        
        total_arrears = balances.aggregate(
            arrears=Sum(F('term_fee') + F('previous_arrears') - F('amount_paid'))
        )['arrears'] or 0
        
        # Count students with arrears
        students_with_arrears = balances.filter(
            Q(term_fee__gt=0) | Q(previous_arrears__gt=0)
        ).values('student').distinct().count()
        
        # Get top arrears students
        from django.db.models import Q
        top_arrears = balances.filter(
            Q(term_fee__gt=F('amount_paid')) | Q(previous_arrears__gt=0)
        ).select_related('student').order_by(
            F('term_fee') + F('previous_arrears') - F('amount_paid'), ascending=False
        )[:10]
        
        arrears_list = [{
            'student': str(b.student),
            'arrears': float((b.term_fee + b.previous_arrears - b.amount_paid)),
            'term': f"{b.term.academic_year} T{b.term.term}"
        } for b in top_arrears]
        
        return JsonResponse({
            'status': 'success',
            'total_arrears': float(total_arrears),
            'students_with_arrears': students_with_arrears,
            'total_students': balances.values('student').distinct().count(),
            'top_arrears': arrears_list
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_http_methods(['POST'])
def execute_rollover(request, year_id):
    """Execute year rollover with arrears preservation"""
    try:
        year = AcademicYear.objects.get(id=year_id)
        
        # Validate rollover can proceed
        validation_error = year._validate_rollover()
        if validation_error:
            return JsonResponse({
                'status': 'error',
                'message': validation_error
            }, status=400)
        
        # Execute rollover (atomic transaction)
        year.rollover_to_new_year()
        
        # Get new year that was created
        new_year = AcademicYear.objects.get(year=year.year + 1)
        
        # Count students promoted
        promoted_count = StudentMovement.objects.filter(
            from_year=year,
            to_year=new_year
        ).count()
        
        return JsonResponse({
            'status': 'success',
            'message': f'✓ Successfully rolled over to Academic Year {new_year.year}',
            'new_year_id': new_year.id,
            'students_promoted': promoted_count,
            'redirect_url': f'/admin/academic/calendar/'
        })
    except AcademicYear.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Academic year not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Rollover failed: {str(e)}'
        }, status=400)


def export_academic_calendar(request, year_id):
    """Export academic calendar as CSV"""
    try:
        year = AcademicYear.objects.get(id=year_id)
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Academic Year Calendar Export', year.year])
        writer.writerow([])
        
        # Year info
        writer.writerow(['Year Start Date', year.start_date])
        writer.writerow(['Year End Date', year.end_date])
        writer.writerow(['Is Active', 'Yes' if year.is_active else 'No'])
        writer.writerow([])
        
        # Terms
        writer.writerow(['Term', 'Start Date', 'End Date', 'Fee Amount'])
        for term in year.get_terms():
            term_fee = TermFee.objects.filter(term=term).first()
            writer.writerow([
                f'Term {term.term}',
                term.start_date,
                term.end_date,
                term_fee.amount if term_fee else 'N/A'
            ])
        
        writer.writerow([])
        
        # Financial summary
        summary = year.get_financial_summary()
        writer.writerow(['Financial Summary', 'Amount'])
        writer.writerow(['Total Expected', f"${summary['total_expected']:.2f}"])
        writer.writerow(['Total Collected', f"${summary['total_collected']:.2f}"])
        writer.writerow(['Total Arrears', f"${summary['total_arrears']:.2f}"])
        writer.writerow(['Collection Rate', f"{summary['collection_rate']:.1f}%"])
        
        # Create response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="academic_calendar_{year.year}.csv"'
        return response
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


def export_fee_structure(request, year_id):
    """Export fee structure for year as CSV"""
    try:
        year = AcademicYear.objects.get(id=year_id)
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Fee Structure Export', year.year])
        writer.writerow([])
        
        # Terms with fees
        writer.writerow(['Term', 'Amount'])
        for term in year.get_terms():
            term_fee = TermFee.objects.filter(term=term).first()
            writer.writerow([
                f'Term {term.term}',
                term_fee.amount if term_fee else 'N/A'
            ])
        
        # Create response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="fee_structure_{year.year}.csv"'
        return response
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
def create_terms_api(request):
    """Create three standard terms for an academic year"""
    try:
        data = json.loads(request.body)
        academic_year = int(data.get('academic_year'))
        
        # Get or create the academic year
        year_obj = AcademicYear.objects.get(year=academic_year)
        
        # Check if terms already exist
        existing_terms = AcademicTerm.objects.filter(academic_year=academic_year).count()
        if existing_terms > 0:
            return JsonResponse({
                'status': 'error',
                'message': f'Year {academic_year} already has {existing_terms} term(s)'
            }, status=400)
        
        # Define standard term dates
        terms_data = [
            {
                'term': 1,
                'start_date': date(academic_year, 1, 10),
                'end_date': date(academic_year, 4, 10),
            },
            {
                'term': 2,
                'start_date': date(academic_year, 4, 20),
                'end_date': date(academic_year, 8, 10),
            },
            {
                'term': 3,
                'start_date': date(academic_year, 8, 20),
                'end_date': date(academic_year, 11, 30),
            },
        ]
        
        created_terms = []
        term_objects = []
        for term_data in terms_data:
            term, created = AcademicTerm.objects.get_or_create(
                academic_year=academic_year,
                term=term_data['term'],
                defaults={
                    'start_date': term_data['start_date'],
                    'end_date': term_data['end_date'],
                }
            )
            if created:
                created_terms.append(f"Term {term.term}")
            term_objects.append(term)
        
        # Auto-generate StudentBalance records for all active students
        # This prevents the missing balance issue
        # NOTE: Only create balances for current/past terms, not future terms
        from decimal import Decimal
        current_term = AcademicTerm.get_current_term()
        active_students = Student.objects.filter(is_active=True, is_deleted=False)
        balances_created = 0
        
        for student in active_students:
            for term in term_objects:
                # Skip future terms - only create up to current term
                if term.academic_year > current_term.academic_year or (
                    term.academic_year == current_term.academic_year and term.term > current_term.term
                ):
                    continue
                
                # Skip if balance already exists
                if StudentBalance.objects.filter(student=student, term=term).exists():
                    continue
                
                # Use the standard initialize_term_balance method which properly calculates arrears
                try:
                    balance = StudentBalance.initialize_term_balance(student, term)
                    if balance:
                        balances_created += 1
                except Exception as e:
                    print(f"Warning: Could not create balance for {student.full_name} in {term}: {e}")
        
        return JsonResponse({
            'status': 'success',
            'message': f'Created {len(created_terms)} terms and {balances_created} student balances. Ready for bulk promotion!',
            'terms_created': len(created_terms),
            'balances_created': balances_created,
            'redirect_url': '/academic-management/bulk-promotion/',
            'next_action': 'Please proceed to Bulk Promotion to move students to their new grades'
        })
    except AcademicYear.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Academic year not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
def activate_first_term_api(request):
    """Activate the first term of an academic year"""
    try:
        data = json.loads(request.body)
        academic_year = int(data.get('academic_year'))
        
        # Find first term
        first_term = AcademicTerm.objects.filter(academic_year=academic_year, term=1).first()
        if not first_term:
            return JsonResponse({
                'status': 'error',
                'message': 'First term not found for this year'
            }, status=404)
        
        # Clear all current terms
        AcademicTerm.objects.all().update(is_current=False, is_completed=False)
        
        # Activate first term
        first_term.is_current = True
        first_term.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'First Term {academic_year} activated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
