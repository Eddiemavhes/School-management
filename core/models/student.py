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
        
        # Validation 4: Cannot reactivate graduated students
        if old_status == 'GRADUATED' and new_status != 'GRADUATED':
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
            'ENROLLED': ['ACTIVE', 'GRADUATED', 'EXPELLED'],  # Allow direct ENROLLED->GRADUATED for Grade 7 auto-graduation
            'ACTIVE': ['GRADUATED', 'EXPELLED'],
            'GRADUATED': [],
            'EXPELLED': [],
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

    def get_current_term_payments(self):
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
        """Get total outstanding balance for CURRENT TERM ONLY (including credits as negative values)"""
        from .fee import StudentBalance
        from .academic import AcademicTerm
        
        # Get current term
        current_term = AcademicTerm.get_current_term()
        if not current_term:
            return 0
        
        # Get ONLY the current term balance
        current_balance = StudentBalance.objects.filter(
            student=self,
            term=current_term
        ).first()
        
        if current_balance:
            return float(current_balance.current_balance)
        
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

    def auto_graduate_if_eligible(self):
        """
        Automatically graduate Grade 7 students who have paid all fees.
        This allows students to transition to Alumni status automatically
        when they complete Grade 7 and pay all fees.
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