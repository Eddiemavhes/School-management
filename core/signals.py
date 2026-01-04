from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import TeacherAssignmentHistory, Class, Student
from .models.academic import Payment, AcademicTerm

@receiver(post_save, sender=Student)
def create_student_balance_on_enrollment(sender, instance, created, **kwargs):
    """Automatically create StudentBalance when a student is enrolled in current term"""
    from .models.fee import StudentBalance
    from .models.academic import AcademicTerm
    
    if created or instance.current_class:  # Created or class assigned
        current_term = AcademicTerm.get_current_term()
        if current_term:
            try:
                # Initialize/get student balance for current term
                StudentBalance.initialize_term_balance(instance, current_term)
            except Exception as e:
                print(f"Error creating StudentBalance for new student {instance}: {e}")

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
        
        # CHECK FOR GRADE 7 TERM 3 ALUMNI CONVERSION
        # If this is a Grade 7 student in Term 3 with zero/negative balance, convert to alumni
        if student.current_class and student.current_class.grade == 7:
            if term and term.term == 3:
                # Check if all fees are paid (balance <= 0)
                if balance and balance.current_balance <= 0:
                    # Trigger alumni conversion
                    from .services.alumni_conversion import AlumniConversionService
                    
                    try:
                        # Only convert if not already properly configured as alumni
                        if student.status != 'ALUMNI' or student.is_active:
                            if AlumniConversionService.convert_to_alumni(student):
                                print(f"✅ {student.first_name} {student.surname} converted to Alumni (Balance: {balance.current_balance})")
                    except Exception as e:
                        print(f"⚠️ Error converting {student.first_name} {student.surname} to alumni: {e}")
        
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

@receiver(post_delete, sender=Payment)
def recalculate_balance_on_payment_delete(sender, instance, **kwargs):
    """Recalculate StudentBalance.amount_paid when a payment is deleted"""
    from .models.fee import StudentBalance
    from django.db.models import Sum
    
    student = instance.student
    term = instance.term
    
    try:
        # Get the student's balance for this term
        balance = StudentBalance.objects.filter(student=student, term=term).first()
        
        if balance:
            # Recalculate total paid from remaining Payment records
            total_paid = Payment.objects.filter(
                student=student,
                term=term
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            balance.amount_paid = total_paid
            balance.save(update_fields=['amount_paid'])
            
    except Exception as e:
        print(f"Error recalculating balance after payment delete: {e}")

@receiver(post_save, sender=Payment)
def check_grade7_alumni_status(sender, instance, created, **kwargs):
    """Check if Grade 7 student should be marked as alumni upon full fee payment"""
    from .models.student import Student
    from .models.fee import StudentBalance
    from decimal import Decimal
    from django.utils import timezone
    
    student = instance.student
    
    # Only check Grade 7 students (handle both string 'ECD' and numeric grades)
    if not student.current_class:
        return
    
    try:
        grade = int(student.current_class.grade)
    except (ValueError, TypeError):
        # Not a numeric grade (e.g., 'ECD'), skip alumni check
        return
    
    if grade != 7:
        return
    
    # Only check if still active (not already archived)
    if student.is_archived:
        return
    
    try:
        # Get student's total outstanding balance across all terms
        all_balances = StudentBalance.objects.filter(student=student)
        total_outstanding = sum(b.current_balance for b in all_balances if b.current_balance > 0)
        
        # If all fees are paid (balance <= 0), mark as ALUMNI immediately
        if total_outstanding <= 0:
            student.status = 'ALUMNI'
            student.alumni_date = timezone.now()
            # Don't mark as inactive - they can still sit for exams and complete Grade 7
            student.save(update_fields=['status', 'alumni_date'])
            
            print(f"✅ {student.full_name} marked as ALUMNI - all fees paid in Grade 7")
    
    except Exception as e:
        print(f"Error checking Grade 7 alumni status: {e}")


@receiver(post_delete, sender=Payment)
def check_alumni_status_on_payment_delete(sender, instance, **kwargs):
    """Re-check alumni status if payment is deleted"""
    from .models.student import Student
    from .models.fee import StudentBalance
    
    student = instance.student
    
    # Only check Grade 7 students (skip ECD grades)
    if not student.current_class or student.current_class.grade == 'ECD':
        return
    
    try:
        grade = int(student.current_class.grade)
    except (ValueError, TypeError):
        return
    
    if grade != 7:
        return
    
    try:
        # Recalculate total outstanding
        all_balances = StudentBalance.objects.filter(student=student)
        total_outstanding = sum(b.current_balance for b in all_balances if b.current_balance > 0)
        
        # If balance became positive again (debt returned), remove alumni status if it was just for fees
        if total_outstanding > 0 and student.status == 'ALUMNI':
            # Check if this is a fee-based alumni (no graduation yet)
            current_term = AcademicTerm.get_current_term()
            if current_term and current_term.term < 3:
                # Still in Term 1 or 2, not end-of-year graduation yet
                student.status = 'ACTIVE'
                student.save(update_fields=['status'])
                print(f"❌ {student.full_name} alumni status revoked - fees unpaid again")
    
    except Exception as e:
        print(f"Error rechecking alumni status after payment delete: {e}")

@receiver(post_save, sender=AcademicTerm)
def initialize_balances_on_term_activation(sender, instance, **kwargs):
    """Initialize StudentBalance for all active students when a term becomes current
    
    Also handles auto-graduation of Grade 7 students when they complete all 3 terms
    """
    if instance.is_current:
        from .models.fee import StudentBalance
        from .models.student_movement import StudentMovement
        
        # GRADUATION: When ANY term is marked current, check if Grade 7 students have completed all 3 terms
        # Grade 7 students graduate ONLY AFTER completing Term 3, not on year activation
        
        # Check if this is Term 3 (the final term) being marked as current
        if instance.term == 3:
            # This is Term 3 - students who complete this term should graduate
            current_year = instance.academic_year
            
            # Find all ENROLLED students who have completed ALL 3 TERMS of this year
            # A student completes a term when a balance record exists for that term
            for term_num in [1, 2, 3]:
                completed_term = AcademicTerm.objects.filter(
                    academic_year=current_year,
                    term=term_num
                ).first()
                
                if not completed_term:
                    # Can't graduate yet - not all terms exist
                    return
            
            # Get students who have balance records for ALL 3 terms of this year
            from .models.academic_year import AcademicYear
            
            # Students with Term 1 balance
            term1_students = StudentBalance.objects.filter(
                term__academic_year=current_year,
                term__term=1
            ).values_list('student_id', flat=True).distinct()
            
            # Students with Term 2 balance
            term2_students = StudentBalance.objects.filter(
                term__academic_year=current_year,
                term__term=2
            ).values_list('student_id', flat=True).distinct()
            
            # Students with Term 3 balance
            term3_students = StudentBalance.objects.filter(
                term__academic_year=current_year,
                term__term=3
            ).values_list('student_id', flat=True).distinct()
            
            # Get students who have completed ALL 3 TERMS (intersection of all three)
            completed_all_terms = set(term1_students) & set(term2_students) & set(term3_students)
            
            # Get these students - but only graduate those in Grade 7!
            # CRITICAL FIX: Only Grade 7 students can graduate. Grade 1-6 remain active.
            students_to_graduate = Student.objects.filter(
                pk__in=completed_all_terms,
                status='ENROLLED',  # Not yet graduated
                is_active=True,
                is_deleted=False,
                current_class__grade=7  # ✅ CRITICAL: Only Grade 7 students graduate!
            )
            
            for student in students_to_graduate:
                # Get their final balance from Term 3 of this year
                final_balance = StudentBalance.objects.filter(
                    student=student,
                    term__academic_year=current_year,
                    term__term=3
                ).first()
                
                if final_balance:
                    # Mark as GRADUATED and determine Alumni status based on payment
                    # Alumni = student who graduated with zero or negative balance (fully paid or credit)
                    student.status = 'GRADUATED'
                    student.is_active = False
                    student.is_archived = final_balance.current_balance <= 0
                    student.save()
                    
                    # Create graduation movement record
                    StudentMovement.objects.create(
                        student=student,
                        from_class=student.current_class,
                        to_class=None,
                        movement_type='GRADUATION',
                        reason=f'Completed Grade 7 ({current_year}). Final balance: ${final_balance.current_balance:.2f}. {"Alumni (Fully Paid)" if student.is_archived else "Graduated (Arrears Outstanding)"}'
                    )
        
        # Initialize balances for remaining active students in the current term
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
                        term_fee_record=term_fee,
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
