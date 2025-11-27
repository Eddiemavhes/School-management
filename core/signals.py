from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import TeacherAssignmentHistory, Class, Student
from .models.academic import Payment

@receiver(post_save, sender=Payment)
def update_student_balance_on_payment(sender, instance, created, **kwargs):
    """Update StudentBalance.amount_paid when a payment is recorded"""
    from .models.fee import StudentBalance
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
    except Exception as e:
        print(f"Error updating StudentBalance for payment {instance.id}: {e}")

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
