from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from ..models.student import Student
from ..models.class_model import Class
from ..models.payment import Payment
from ..models.student_movement import StudentMovement
from ..models.academic import AcademicTerm
from ..models.arrears_import import ArrearsImportBatch
from django.utils import timezone
from datetime import timedelta

@login_required
def dashboard(request):
    # Get recent movements for the promotion widget
    recent_movements = StudentMovement.objects.select_related(
        'student', 'from_class', 'to_class'
    ).order_by('-movement_date')[:5]

    # Get recent transfers
    recent_transfers = StudentMovement.objects.select_related(
        'student', 'old_class', 'new_class'
    ).filter(
        movement_type='TRANSFER'
    ).order_by('-date')[:5]

    # Get general stats
    total_students = Student.objects.filter(status='ACTIVE').count()
    total_classes = Class.objects.count()
    
    # Get recent payments
    recent_payments = Payment.objects.select_related('student').order_by('-payment_date')[:5]
    
    # Get class distribution
    class_distribution = Class.objects.annotate(
        student_count=Count('students')
    ).values('grade', 'section', 'student_count')

    # Get payment statistics for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    payment_stats = Payment.objects.filter(
        payment_date__gte=thirty_days_ago
    ).aggregate(
        total_amount=Sum('amount'),
        total_count=Count('id')
    )

    # Get current term and academic year
    current_term = AcademicTerm.get_current_term()
    
    # Show arrears import button only in Term 1 when no relevant arrears import batch exists
    # Treat only in-progress/complete statuses as blocking: VALIDATING, READY, IMPORTED
    blocking_statuses = ['VALIDATING', 'READY', 'IMPORTED']
    blocking_count = 0
    arrears_import_completed = False

    if current_term is not None:
        # Only consider batches for the same academic year (and optionally same starting_term)
        try:
            current_year = current_term.academic_year
            blocking_qs = ArrearsImportBatch.objects.filter(academic_year=current_year, status__in=blocking_statuses)
            # Prefer batches targeting this starting term, but any batch for the year should block
            blocking_count = blocking_qs.count()
            arrears_import_completed = blocking_qs.exists()
        except Exception:
            # Fallback to global check if anything unexpected happens
            blocking_count = ArrearsImportBatch.objects.filter(status__in=blocking_statuses).count()
            arrears_import_completed = ArrearsImportBatch.objects.filter(status__in=blocking_statuses).exists()

    # Robustly compute is_system_new handling various term/flag representations
    def _to_bool(val):
        if isinstance(val, bool):
            return val
        if val is None:
            return False
        s = str(val).strip().lower()
        return s in ('1', 'true', 't', 'yes', 'y')

    arrears_import_completed_bool = _to_bool(arrears_import_completed)

    # Determine term number robustly
    term_number = None
    if current_term is not None:
        term_val = getattr(current_term, 'term', None)
        try:
            term_number = int(term_val)
        except Exception:
            # fallback for values like 'First Term' or 'First'
            if isinstance(term_val, str) and term_val.strip().lower().startswith('first'):
                term_number = 1
            else:
                term_number = None

    is_system_new = bool(current_term is not None and term_number == 1 and not arrears_import_completed_bool)

    context = {
        'recent_movements': recent_movements,
        'recent_transfers': recent_transfers,  # Add recent transfers to context
        'total_students': total_students,
        'total_classes': total_classes,
        'recent_payments': recent_payments,
        'class_distribution': class_distribution,
        'payment_stats': payment_stats,
        'current_term': current_term,
        'is_system_new': is_system_new,
        'arrears_blocking_count': blocking_count,
        # debug helpers (visible in template)
        'debug_arrears_import_completed': arrears_import_completed_bool,
        'debug_current_term_term': getattr(current_term, 'term', None),
        'debug_term_number': term_number,
    }
    
    return render(request, 'dashboard/dashboard.html', context)