from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from core.models import Class
from .academic import AcademicTerm


# Custom manager to exclude deleted students by default
class ActiveStudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllStudentsManager(models.Manager):
    """Manager that includes deleted students for audit purposes"""
    def get_queryset(self):
        return super().get_queryset()


class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    STATUS_CHOICES = [
        ('ENROLLED', 'Enrolled'),
        ('ACTIVE', 'Active'),
        ('ALUMNI', 'Alumni'),
        ('GRADUATED', 'Graduated'),
        ('EXPELLED', 'Expelled'),
    ]

    # Personal Information
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    birth_entry_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9-]+$',
                message='Birth entry number must contain only uppercase letters, numbers, and hyphens'
            )
        ]
    )

    # Class Information
    current_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        related_name='students'
    )
    date_enrolled = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False, help_text="Graduated with all arrears paid - can be deleted")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ENROLLED')
    alumni_date = models.DateTimeField(null=True, blank=True, help_text="When student became alumni (immediately upon full fee payment in Grade 7)")
    
    # Audit Trail - Soft Delete
    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag - financial records preserved for audit")
    deleted_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when student was deleted")
    deleted_reason = models.CharField(max_length=255, blank=True, help_text="Reason for deletion")

    # Financial Information
    current_term_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    previous_term_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    # Managers
    objects = ActiveStudentManager()  # Default - excludes deleted
    all_students = AllStudentsManager()  # Includes deleted - for audit

    # Cache for overall_balance to avoid multiple queries
    _overall_balance_cache = None

    class Meta:
        ordering = ['surname', 'first_name']
        indexes = [
            models.Index(fields=['surname', 'first_name']),
            models.Index(fields=['birth_entry_number']),
        ]

    def __str__(self):
        return f"{self.surname}, {self.first_name}"

    def clean(self):
        """Validate student data including status transitions and dates"""
        # Validation 1: Class assignment validation
        self._validate_class_assignment()
        
        # Validation 2: Date of birth validation
        self._validate_date_of_birth()
        
        # Validation 3: Enrollment date validation
        self._validate_enrollment_date()
        
        # Validation 4: Status transition validation
        self._validate_status_transition()
    
    def _validate_class_assignment(self):
        """Validation 1: Ensure student can be assigned to class (implicit uniqueness)"""
        # When assigning a new class to a student, the ForeignKey constraint ensures
        # only one current_class. We just validate the class exists and is valid.
        if self.current_class:
            # Check that class academic year is valid
            try:
                from .academic_year import AcademicYear
                AcademicYear.objects.get(year=self.current_class.academic_year)
            except AcademicYear.DoesNotExist:
                raise ValidationError(
                    f"Cannot assign student to {self.current_class}. "
                    f"Academic year {self.current_class.academic_year} is invalid."
                )
            # If this is an ECD class, enforce capacity and premium constraints
            try:
                student_grade = str(self.current_class.grade)
                if student_grade.startswith('ECD'):  # Matches ECDA, ECDB
                    from .ecd import ECDClassProfile
                    profile = getattr(self.current_class, 'ecd_profile', None)
                    if profile:
                        # Count students excluding self (in case of edits)
                        current_count = self.current_class.students.exclude(pk=self.pk).count()
                        if profile.capacity and current_count >= profile.capacity:
                            raise ValidationError(
                                f"Cannot assign student to {self.current_class}: class is at full capacity ({profile.capacity})."
                            )
            except ValidationError:
                # Re-raise validation errors for capacity
                raise
            except Exception:
                # Any unexpected issues loading ECD profile should not block enrollment
                pass
    
    def _validate_date_of_birth(self):
        """Validation 2: Date of birth must be valid (age 4-25, not in future)"""
        from datetime import datetime
        today = timezone.now()
        # Ensure date_of_birth is a date object for comparison
        if isinstance(self.date_of_birth, datetime):
            date_of_birth_value = self.date_of_birth.date()
        else:
            date_of_birth_value = self.date_of_birth
        
        today_date = today.date() if isinstance(today, datetime) else today
        
        # Check not in future
        if date_of_birth_value > today_date:
            raise ValidationError(
                f"Date of birth cannot be in the future. "
                f"Date of birth: {date_of_birth_value}, Today: {today_date}"
            )
        
        # Calculate age
        age = (today_date - date_of_birth_value).days // 365
        
        # Check age is between 4 and 25
        if age < 4:
            raise ValidationError(
                f"Student age must be at least 4 years old. Current age: {age} years"
            )
        if age > 25:
            raise ValidationError(
                f"Student age cannot exceed 25 years old. Current age: {age} years"
            )
    
    def _validate_enrollment_date(self):
        """Validation 3: Enrollment date must be valid (not in future, not too far past)"""
        from datetime import datetime
        today = timezone.now()
        # Ensure date_enrolled is a date object for comparison
        if isinstance(self.date_enrolled, datetime):
            date_enrolled_value = self.date_enrolled.date()
        else:
            date_enrolled_value = self.date_enrolled
        
        today_date = today.date() if isinstance(today, datetime) else today
        
        # Check not in future
        if date_enrolled_value > today_date:
            raise ValidationError(
                f"Enrollment date cannot be in the future. "
                f"Enrollment date: {date_enrolled_value}, Today: {today_date}"
            )
        
        # Check not too far in the past (more than 20 years)
        from datetime import timedelta
        max_past_date = today_date - timedelta(days=20*365)
        if date_enrolled_value < max_past_date:
            raise ValidationError(
                f"Enrollment date cannot be more than 20 years in the past. "
                f"Enrollment date: {date_enrolled_value}"
            )
    
    def _validate_status_transition(self):
        """Validation 4: Validate status transitions follow allowed paths"""
        # Only validate if student already exists (has pk)
        if not self.pk:
            # New student - status must be ENROLLED or ACTIVE
            if self.status not in ['ENROLLED', 'ACTIVE']:
                raise ValidationError(
                    f"New student must have status ENROLLED or ACTIVE, not {self.status}"
                )
            return
        
        # Get the current database state
        old_student = Student.objects.get(pk=self.pk)
        old_status = old_student.status
        new_status = self.status
        
        # Status can only change in valid ways
        # ENROLLED -> ACTIVE
        # ACTIVE -> GRADUATED or EXPELLED
        # GRADUATED or EXPELLED -> no changes allowed
        
        if old_status == new_status:
            # No change
            return
        
        # Validation 5: Cannot deactivate active students (only graduated or expelled can be deactivated)
        if old_status == 'ACTIVE' and not self.is_active and new_status == 'ACTIVE':
            raise ValidationError(
                "Cannot deactivate an ACTIVE student. "
                "Student must first be transitioned to GRADUATED or EXPELLED status."
            )
        
        # Validation 4: Cannot reactivate graduated students (EXCEPT to archive them)
        if old_status == 'GRADUATED' and new_status != 'GRADUATED' and new_status != 'ALUMNI':
            raise ValidationError(
                f"Cannot change status of a GRADUATED student. "
                f"Graduated students cannot be re-enrolled."
            )
        
        if old_status == 'EXPELLED' and new_status != 'EXPELLED':
            raise ValidationError(
                f"Cannot change status of an EXPELLED student."
            )
        
        # Validate allowed transitions
        allowed_transitions = {
            'ENROLLED': ['ACTIVE', 'GRADUATED', 'ALUMNI', 'EXPELLED'],  # Allow direct transitions
            'ACTIVE': ['GRADUATED', 'ALUMNI', 'EXPELLED'],  # Allow ACTIVE->ALUMNI for Grade 7 completion
            'ALUMNI': [],  # Alumni status is final
            'GRADUATED': ['ALUMNI'],  # Graduated students can become Alumni when paid
            'EXPELLED': [],  # Expelled status is final
        }
        
        if new_status not in allowed_transitions.get(old_status, []):
            raise ValidationError(
                f"Invalid status transition: {old_status} → {new_status}. "
                f"Allowed transitions from {old_status}: {', '.join(allowed_transitions.get(old_status, []))} "
                f"or no change."
            )
    
    def save(self, *args, **kwargs):
        """Call clean() before saving"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.surname}, {self.first_name}"

    def get_full_name(self):
        """Return full name in format: Surname, FirstName"""
        return f"{self.surname}, {self.first_name}"

    @property
    def initials(self):
        return f"{self.surname[0]}{self.first_name[0]}"

    @property
    def age(self):
        today = timezone.now().date()
        return (today - self.date_of_birth).days // 365

    def get_next_class(self):
        """Get the next class for student progression.
        
        Progression path:
        ECDA (Age 4-5) → ECDB (Age 5-6, same year) → Grade 1 (next year, random section A-D)
                                                    → Grade 2 → ... → Grade 7 (final)
        
        Special Handling:
        - ECDA → ECDB: Same academic year, preserve section (A→A, B→B)
        - ECDB → Grade 1: Next academic year, RANDOM section selection (A, B, C, or D)
        - Grade 1-6 → Next: Keep same section and year progression
        - Grade 7: No progression (final grade, student graduates)
        
        Returns: Class object or None if student is in Grade 7 (final grade)
        """
        import random
        
        if not self.current_class:
            return None
        
        current_grade = self.current_class.grade
        current_section = self.current_class.section
        
        # Define progression map
        progression_map = {
            'ECDA': 'ECDB',  # ECDA → ECDB (same year)
            'ECDB': '1',     # ECDB → Grade 1 (next year, random section)
            '1': '2',
            '2': '3',
            '3': '4',
            '4': '5',
            '5': '6',
            '6': '7',
            '7': None,  # Grade 7 is final, no progression
        }
        
        next_grade = progression_map.get(str(current_grade))
        
        if not next_grade:
            return None  # No progression for Grade 7
        
        # Determine next year
        # ECDA → ECDB stays in same year; ECDB → Grade 1 goes to next year
        if current_grade == 'ECDB':
            next_year = self.current_class.academic_year + 1
        else:
            next_year = self.current_class.academic_year
        
        # For ECDB → Grade 1 transition: randomly select from available sections
        if current_grade == 'ECDB' and next_grade == '1':
            available_classes = Class.objects.filter(
                grade=next_grade,
                academic_year=next_year
            ).order_by('section')
            
            if available_classes.exists():
                # Randomly select one of the available Grade 1 sections
                next_class = random.choice(list(available_classes))
                return next_class
            else:
                return None
        
        # For all other transitions: try to preserve section first, then fall back
        try:
            next_class = Class.objects.get(
                grade=next_grade,
                section=current_section,
                academic_year=next_year
            )
            return next_class
        except Class.DoesNotExist:
            # If same section doesn't exist, try to get any available class of that grade
            try:
                next_class = Class.objects.filter(
                    grade=next_grade,
                    academic_year=next_year
                ).first()
                return next_class
            except:
                return None
    
    def promote_to_next_class(self, next_year=None):
        """Promote student to the next class.
        
        Args:
            next_year: Academic year for the next class (auto-calculated if not provided)
        
        Returns:
            tuple: (success: bool, message: str, new_class: Class or None)
        """
        if not self.current_class:
            return False, "Student has no current class assigned", None
        
        if next_year is None:
            next_year = self.current_class.academic_year + 1
        
        next_class = self.get_next_class()
        
        if not next_class:
            return False, "Student cannot progress further (likely in Grade 7)", None
        
        # Update student's class
        old_class = self.current_class
        self.current_class = next_class
        
        try:
            self.save()
            return True, f"Student promoted from {old_class} to {next_class}", next_class
        except Exception as e:
            return False, f"Error promoting student: {str(e)}", None
    
        """Get total payments made for the current term"""
        current_term = AcademicTerm.get_current_term()
        return self.payments.filter(
            term=current_term
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    def get_previous_term_payments(self):
        """Get total payments made for the previous term"""
        previous_term = AcademicTerm.get_previous_term()
        return self.payments.filter(
            term=previous_term
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @property
    def previous_term_arrears(self):
        """Get current term's previous arrears from StudentBalance model"""
        from .fee import StudentBalance
        current_term = AcademicTerm.get_current_term()
        if not current_term:
            return 0
        
        balance = StudentBalance.objects.filter(
            student=self,
            term=current_term
        ).first()
        
        if balance:
            return balance.previous_arrears
        
        # Fallback to old calculation if no StudentBalance exists
        previous_payments = self.get_previous_term_payments()
        return max(0, self.previous_term_fee - previous_payments)

    @property
    def current_term_balance(self):
        """Get current term balance from StudentBalance model"""
        from .fee import StudentBalance
        current_term = AcademicTerm.get_current_term()
        if not current_term:
            return 0
        
        balance = StudentBalance.objects.filter(
            student=self,
            term=current_term
        ).first()
        
        if balance:
            return balance.current_balance
        
        # Fallback to old calculation if no StudentBalance exists
        current_payments = self.get_current_term_payments()
        total_due = self.current_term_fee + self.previous_term_arrears
        return max(0, total_due - current_payments)

    @property
    def overall_balance(self):
        """Get total outstanding balance - only the CURRENT or LATEST PAST term
        
        Returns the balance from the most recent term that is either:
        1. The current active term, OR
        2. A past term (if no current term balance exists)
        
        Does NOT include future terms that haven't become current yet.
        This ensures students aren't charged for terms they haven't reached.
        
        Note: Uses instance-level caching to avoid multiple queries in a single request.
        """
        # Return cached value if available
        if self._overall_balance_cache is not None:
            return self._overall_balance_cache
        
        from .fee import StudentBalance, TermFee
        from .academic import AcademicTerm
        
        result = 0.0
        
        # Try to get current term first
        current_term = AcademicTerm.get_current_term()
        if current_term:
            # Check prefetched data first if available
            if hasattr(self, '_prefetched_objects_cache') and 'balances' in self._prefetched_objects_cache:
                current_balance = next(
                    (b for b in self.balances.all() if b.term_id == current_term.id),
                    None
                )
            else:
                current_balance = StudentBalance.objects.filter(
                    student=self,
                    term=current_term
                ).first()
            
            if current_balance:
                result = float(current_balance.current_balance)
                self._overall_balance_cache = result
                return result
            
            # No StudentBalance yet, but check if student is active and current term has a fee
            if self.is_active:
                try:
                    term_fee = TermFee.objects.get(term=current_term)
                    result = float(term_fee.amount)  # Student owes the term fee
                    self._overall_balance_cache = result
                    return result
                except TermFee.DoesNotExist:
                    pass
        
        # If no current term balance, get the most recent term balance from past terms
        latest_balance = StudentBalance.objects.filter(
            student=self,
            term__is_current=False  # Only past terms
        ).order_by('-term__academic_year', '-term__term').first()
        
        if latest_balance:
            return float(latest_balance.current_balance)
        
        return 0

    @property
    def total_due(self):
        """Get total amount due for current term (term fee + previous arrears)"""
        from .fee import StudentBalance
        from .academic import AcademicTerm
        
        # Get current term
        current_term = AcademicTerm.get_current_term()
        if not current_term:
            return 0
        
        # Get current term balance
        balance = StudentBalance.objects.filter(
            student=self,
            term=current_term
        ).first()
        
        if balance:
            # Total due = term fee + previous arrears (which can be negative if there's a credit)
            return float(balance.term_fee + balance.previous_arrears)
        
        return 0

    @property
    def payment_status(self):
        """Return payment status color code based on StudentBalance"""
        from .fee import StudentBalance
        current_term = AcademicTerm.get_current_term()
        if not current_term:
            return 'green'
        
        balance = StudentBalance.objects.filter(
            student=self,
            term=current_term
        ).first()
        
        if balance:
            if balance.current_balance <= 0:
                return 'green'  # Fully paid
            elif balance.amount_paid > 0:
                return 'yellow'  # Partial payment
            return 'red'  # No payment
        
        # Fallback to old logic if no StudentBalance exists
        if self.current_term_balance == 0:
            return 'green'  # Fully paid
        elif self.current_term_balance < (self.current_term_fee + self.previous_term_arrears):
            return 'yellow'  # Partial payment
        return 'red'  # No payment

    @property
    def has_arrears(self):
        return self.previous_term_arrears > 0

    def transfer_to_class(self, new_class):
        """Transfer student to a new class"""
        self.current_class = new_class
        self.save()

    def auto_graduate_if_eligible(self):
        """
        Automatically graduate Grade 7 students who have completed their year.
        
        IMPORTANT: This should ONLY be called during year-end rollover processing,
        NOT during payment processing. Grade 7 students must remain active throughout
        their entire Grade 7 academic year (all 3 terms) before graduating to Alumni.
        
        Eligibility criteria:
        - Must be Grade 7 student
        - Must have completed their full Grade 7 year (all 3 terms done)
        - Must have all fees paid ($0 or negative balance)
        
        Called by: Year-end rollover process (e.g., when moving to next academic year)
        """
        # Only process if student is active and enrolled
        if not self.is_active or self.status != 'ENROLLED':
            return False
        
        # Check if in Grade 7 (highest grade)
        if not self.current_class or int(self.current_class.grade) < 7:
            return False
        
        # Check if all fees are paid ($0 or negative balance)
        if self.overall_balance > 0:
            return False  # Still owes money
        
        # All conditions met - graduate the student
        from .student_movement import StudentMovement
        
        try:
            # Create graduation movement record
            movement = StudentMovement(
                student=self,
                from_class=self.current_class,
                to_class=None,
                movement_type='GRADUATION',
                moved_by=None,  # System automatic
                previous_arrears=self.previous_term_arrears + self.current_term_balance,
                preserved_arrears=self.previous_term_arrears + self.current_term_balance,
                reason='Auto-graduated: Grade 7 completed with fees paid'
            )
            # Save without full_clean 
            movement.save()
            
            # Mark as graduated
            self.is_active = False
            self.status = 'GRADUATED'
            self.is_archived = True
            self.save()
            
            return True
        except Exception as e:
            print(f"Error auto-graduating {self.full_name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def check_and_archive(self):
        """
        Check if student should be archived:
        - Must be inactive (graduated or not currently in class)
        - Must have GRADUATED status (not just any inactive status)
        - Must have paid all arrears (overall_balance = 0 or negative)
        """
        # Can't archive if already archived
        if self.is_archived:
            return False
        
        # Must have GRADUATED status to be archived
        if self.status != 'GRADUATED':
            return False
        
        # Must be inactive (not currently attending school)
        if self.is_active:
            return False
        
        # Check if all arrears are paid (overall_balance should be 0 or negative)
        if self.overall_balance <= 0:
            self.is_archived = True
            self.save()
            return True
        
        return False