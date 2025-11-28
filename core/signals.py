from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import TeacherAssignmentHistory, Class, Student
from .models.academic import Payment, AcademicTerm

@receiver(post_save, sender=Payment)
def update_student_balance_on_payment(sender, instance, created, **kwargs):
    """Update StudentBalance.amount_paid when a payment is recorded"""
    from .models.fee import StudentBalance
    from .models.academic import AcademicTerm
    from django.db.models import Sum
    
    student = instance.student
    term = instance.term
    
    try:
        # Get or initialize the student's balance for this term
        balance = StudentBalance.initialize_term_balance(student, term)
        
        if balance:
            # Recalculate total paid from ALL payments for this student/term
            # This prevents double-counting if signal runs multiple times
            total_paid = Payment.objects.filter(
                student=student, 
                term=term
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            balance.amount_paid = total_paid
            balance.save(update_fields=['amount_paid'])
        
        # IMPORTANT: Check for auto-graduation FIRST before cascading to next terms
        # If Grade 7 student reached $0 balance, they should graduate and NOT get future term fees
        student.refresh_from_db()
        if student.auto_graduate_if_eligible():
            print(f"Auto-graduated {student.full_name} (Grade 7, balance $0)")
            # Student is now archived - don't cascade to next terms
            return
        
        # ONLY cascade to next terms if student is NOT graduating
        # When a payment changes the balance for the current term,
        # we need to recalculate arrears for NEXT term(s) ONLY IF THEY ALREADY EXIST
        # This prevents creating future term fees prematurely
        if term and balance:
            # Get all subsequent terms in the same year that ALREADY HAVE balances for this student
            next_terms = AcademicTerm.objects.filter(
                academic_year=term.academic_year,
                term__gt=term.term
            ).order_by('term')
            
            for next_term in next_terms:
                # Only update if balance already exists - don't create new ones
                if StudentBalance.objects.filter(student=student, term=next_term).exists():
                    StudentBalance.initialize_term_balance(student, next_term)
            
            # Also check if there are terms in the next year (but only if they have balances)
            next_year_terms = AcademicTerm.objects.filter(
                academic_year=term.academic_year + 1
            ).order_by('term')
            
            for next_year_term in next_year_terms:
                # Only update if balance already exists - don't create new ones
                if StudentBalance.objects.filter(student=student, term=next_year_term).exists():
                    StudentBalance.initialize_term_balance(student, next_year_term)
                
    except Exception as e:
        print(f"Error updating StudentBalance for payment {instance.id}: {e}")

@receiver(post_save, sender=AcademicTerm)
def initialize_balances_on_term_activation(sender, instance, **kwargs):
    """Initialize StudentBalance for all active students when a term becomes current"""
    if instance.is_current:
        from .models.fee import StudentBalance
        
        # Get all active students
        active_students = Student.objects.filter(is_active=True, is_deleted=False)
        
        for student in active_students:
            try:
                StudentBalance.initialize_term_balance(student, instance)
            except Exception as e:
                print(f"Warning: Could not initialize balance for {student.full_name} in {instance}: {e}")

@receiver(post_save, sender=Student)
def create_student_balance_on_enrollment(sender, instance, created, **kwargs):
    """Create StudentBalance record when a new student is enrolled"""
    if created:
        from .models.fee import StudentBalance, TermFee
        from .models.academic import AcademicTerm
        
        # Get the current active term
        current_term = AcademicTerm.get_current_term()
        
        if current_term:
            # Check if StudentBalance already exists
            balance_exists = StudentBalance.objects.filter(
                student=instance,
                term=current_term
            ).exists()
            
            if not balance_exists:
                try:
                    # Get the fee for this term
                    term_fee = TermFee.objects.get(term=current_term)
                    
                    # Create StudentBalance with current term fee
                    StudentBalance.objects.create(
                        student=instance,
                        term=current_term,
                        term_fee=term_fee.amount,
                        previous_arrears=0,  # New student has no previous arrears
                        amount_paid=0
                    )
                except TermFee.DoesNotExist:
                    print(f"Warning: No TermFee found for {current_term}, balance not created")
                except Exception as e:
                    print(f"Error creating StudentBalance for {instance.full_name}: {e}")

@receiver(post_save, sender=TeacherAssignmentHistory)
def update_class_teacher_on_assignment(sender, instance, created, **kwargs):
    """Update Class.teacher field when a new active assignment is created"""
    if created and instance.is_active:
        # Update the class to point to this teacher
        class_obj = instance.class_assigned
        class_obj.teacher = instance.teacher
        class_obj.save(update_fields=['teacher'])
        
        # Deactivate any other active assignments for the same class
        other_assignments = TeacherAssignmentHistory.objects.filter(
            class_assigned=class_obj,
            is_active=True
        ).exclude(id=instance.id)
        for assignment in other_assignments:
            assignment.is_active = False
            assignment.save(update_fields=['is_active'])

@receiver(post_save, sender=TeacherAssignmentHistory)
def clear_class_teacher_on_deactivation(sender, instance, **kwargs):
    """Clear Class.teacher field when the last active assignment for a class is deactivated"""
    if not instance.is_active:
        # Check if there are any other active assignments for this class
        active_assignments = TeacherAssignmentHistory.objects.filter(
            class_assigned=instance.class_assigned,
            is_active=True
        )
        if not active_assignments.exists():
            # No more active assignments, clear the teacher
            class_obj = instance.class_assigned
            class_obj.teacher = None
            class_obj.save(update_fields=['teacher'])
