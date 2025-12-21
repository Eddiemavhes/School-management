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
    
    # Check if system is in Term 1 AND no arrears import has been attempted yet
    # Show arrears import only in Term 1 before any import batch has been created
    arrears_import_completed = ArrearsImportBatch.objects.filter(
        status__in=['IMPORTED', 'READY', 'VALIDATING']
    ).exists()
    
    # DEBUG: Log the values
    import sys
    all_terms = list(AcademicTerm.objects.all().values('id', 'academic_year', 'term', 'is_current'))
    print(f"DEBUG: All AcademicTerms: {all_terms}", file=sys.stderr)
    print(f"DEBUG: current_term = {current_term}", file=sys.stderr)
    if current_term:
        print(f"DEBUG: current_term.term = {current_term.term} (type: {type(current_term.term)})", file=sys.stderr)
        print(f"DEBUG: current_term.term == 1: {current_term.term == 1}", file=sys.stderr)
        print(f"DEBUG: int(current_term.term) == 1: {int(current_term.term) == 1}", file=sys.stderr)
    print(f"DEBUG: arrears_import_completed = {arrears_import_completed}", file=sys.stderr)
    print(f"DEBUG: ArrearsImportBatch.objects.all().count() = {ArrearsImportBatch.objects.all().count()}", file=sys.stderr)
    
    is_system_new = (current_term and int(current_term.term) == 1 and not arrears_import_completed)
    print(f"DEBUG: is_system_new = {is_system_new}", file=sys.stderr)
    print(f"DEBUG: Condition breakdown: current_term={bool(current_term)}, term==1={int(current_term.term)==1 if current_term else False}, not completed={not arrears_import_completed}", file=sys.stderr)

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
    }
    
    return render(request, 'dashboard/dashboard.html', context)