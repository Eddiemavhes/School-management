from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
import uuid

class AcademicTerm(models.Model):
    TERM_CHOICES = [
        (1, 'First Term'),
        (2, 'Second Term'),
        (3, 'Third Term'),
    ]

    academic_year = models.IntegerField()
    term = models.IntegerField(choices=TERM_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)  # Track if term has been passed

    class Meta:
        ordering = ['-academic_year', '-term']
        unique_together = ['academic_year', 'term']

    def __str__(self):
        return f"{self.get_term_display()} {self.academic_year}"

    def clean(self):
        # Validation 1: Date validation
        if self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date")
        
        # Validation 2: Cannot skip terms sequentially
        self._validate_term_sequentiality()
        
        # Validation 3: Current term exclusivity
        if self.is_current:
            AcademicTerm.objects.filter(is_current=True).exclude(id=self.id).update(is_current=False)
    
    def _validate_term_sequentiality(self):
        """Validation 2: Cannot skip terms - all preceding terms must exist"""
        if self.term == 1:
            # First term doesn't need preceding terms
            return
        
        # Check if all preceding terms exist in the same academic year
        missing_terms = []
        for term_num in range(1, self.term):
            if not AcademicTerm.objects.filter(
                academic_year=self.academic_year,
                term=term_num
            ).exists():
                missing_terms.append(f"Term {term_num}")
        
        if missing_terms:
            raise ValidationError(
                f"Cannot create {self.get_term_display()}. Please create preceding terms first. "
                f"Required: {', '.join(missing_terms)}"
            )

    def can_move_to_next_term(self):
        """Check if this term can move to the next term"""
        if self.term >= 3:
            return False  # No term after Term 3
        
        if self.is_completed:
            return False  # Cannot move from a completed term
        
        return True

    def get_next_term(self):
        """Get the next term"""
        if self.term >= 3:
            return None
        
        return AcademicTerm.objects.filter(
            academic_year=self.academic_year,
            term=self.term + 1
        ).first()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_current_term(cls):
        """Get the current academic term"""
        try:
            return cls.objects.get(is_current=True)
        except cls.DoesNotExist:
            # If no term is marked as current, get the latest term
            return cls.objects.order_by('-academic_year', '-term').first()

    @classmethod
    def get_previous_term(cls):
        """Get the previous academic term relative to the current term"""
        current = cls.get_current_term()
        if not current:
            return None
        
        if current.term > 1:
            # Previous term in the same academic year
            return cls.objects.filter(
                academic_year=current.academic_year,
                term=current.term - 1
            ).first()
        else:
            # Last term of the previous academic year
            return cls.objects.filter(
                academic_year=current.academic_year - 1,
                term=3
            ).first()

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('MOBILE', 'Mobile Money'),
        ('CHEQUE', 'Cheque'),
    ]

    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        default='CASH'
    )
    receipt_number = models.CharField(max_length=50, unique=True, editable=False, null=True, blank=True)
    reference_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        'Administrator',
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        receipt = self.receipt_number if self.receipt_number else "NEW"
        student_name = str(self.student) if self.student else "Unknown"
        return f"Payment {receipt} - {student_name}"

    def clean(self):
        """Comprehensive payment validation"""
        # Validation 0: Term must be set
        if not self.term_id:
            raise ValidationError("Academic term must be set before recording a payment")
        
        # Validation 1: Allow payments for current term or past terms (for arrears clearing)
        # We used to restrict to only current term, but Grade 7 students need to pay arrears
        # from past terms before graduating, so this check is now removed/relaxed
        # Note: recorded_by can be None for system-generated payments
        
        # Validation 2: Amount >= 0 (can be zero for placeholder payments, but typically > 0)
        if self.amount is not None and self.amount < 0:
            raise ValidationError("Payment amount cannot be negative")
        
        if self.amount is not None and self.amount == 0:
            # Allow zero but warn - could be for adjustment purposes
            pass
        
        # Validation 3: Student eligibility
        if self.student_id:
            self._validate_student_eligibility()
        
        # Validation 4: Term fee existence check
        if self.term_id:
            self._validate_term_fee_exists()
    
    def _validate_student_eligibility(self):
        """Validation 3: Student must have a balance record for this term (or be graduated paying arrears)"""
        from .fee import StudentBalance
        
        # Graduated students CAN make payments (for their arrears)
        # They just won't have a current term balance
        # So we check if they have ANY balance record (from previous terms)
        if self.student.is_active:
            # Active student - must have a balance record for this term
            try:
                StudentBalance.objects.get(student=self.student, term=self.term)
            except StudentBalance.DoesNotExist:
                raise ValidationError(
                    f"No balance record exists for {self.student.full_name} in {self.term}. "
                    f"Please initialize the balance first."
                )
        else:
            # Graduated student - must have at least one balance record (from previous terms)
            if not StudentBalance.objects.filter(student=self.student).exists():
                raise ValidationError(
                    f"No balance record exists for graduated student {self.student.full_name}. "
                    f"Cannot record payment."
                )
    
    def _validate_term_fee_exists(self):
        """Validation 4: Term fee must be set for this term"""
        from .fee import TermFee
        
        try:
            TermFee.objects.get(term=self.term)
        except TermFee.DoesNotExist:
            raise ValidationError(f"Term fee has not been set for {self.term}")

    def _generate_reference_number(self):
        """Generate reference number based on payment method"""
        if self.reference_number:
            return self.reference_number
        
        method_prefix = {
            'CASH': 'CSH',
            'BANK': 'BNK',
            'MOBILE': 'MOB',
            'CHEQUE': 'CHQ',
        }
        
        prefix = method_prefix.get(self.payment_method, 'PAY')
        timestamp = str(timezone.now().strftime('%Y%m%d%H%M%S'))
        unique_id = str(uuid.uuid4().int)[:4]
        
        return f"{prefix}-{timestamp}-{unique_id}"

    def save(self, *args, **kwargs):
        # Validate before saving
        self.full_clean()
        
        # Generate reference number if not provided
        if not self.reference_number:
            self.reference_number = self._generate_reference_number()
        
        # Generate receipt number if not exists
        if not self.receipt_number and self.term:
            year = str(timezone.now().year)[-2:]
            term = str(self.term.term)
            unique_id = str(uuid.uuid4().int)[:6]
            self.receipt_number = f"PMT{year}{term}{unique_id}"
        
        super().save(*args, **kwargs)
        
        # Handle excess payments going to next term
        self._handle_excess_payment()
    
    def _handle_excess_payment(self):
        """Handle excess payments - amount > total due goes to next term
        
        NOTE: This method does NOT manually set amount_paid. The amount_paid field 
        is ALWAYS recalculated from actual Payment records via update_balance().
        This method only logs/tracks that excess exists, but the actual amount_paid
        calculation happens automatically from Payment records.
        """
        from .fee import StudentBalance, TermFee
        
        # Safety check: term must exist
        if not self.term:
            return  # Can't handle excess without a term
        
        # Get current balance
        try:
            current_balance = StudentBalance.objects.get(
                student=self.student,
                term=self.term
            )
        except StudentBalance.DoesNotExist:
            return  # Should not happen after validation, but be safe
        
        # Calculate if there's excess
        if current_balance.current_balance < 0:
            # Student has overpaid - excess amount
            excess_amount = abs(current_balance.current_balance)
            
            # Get or create next term balance so the system knows excess credit exists
            next_term = self._get_next_term()
            if next_term:
                try:
                    term_fee = TermFee.objects.get(term=next_term)
                except TermFee.DoesNotExist:
                    # No term fee set for next term - don't create balance yet
                    return
                
                # Get or create balance for next term
                next_balance, _ = StudentBalance.objects.get_or_create(
                    student=self.student,
                    term=next_term,
                    defaults={
                        'term_fee': term_fee.amount,
                        'previous_arrears': Decimal('0')
                    }
                )
                # NOTE: amount_paid will be recalculated from Payment records
                # The excess credit is implicitly available when next term payments are processed
                next_balance.save()

    
    def _get_next_term(self):
        """Get the next term after current payment term"""
        if self.term.term < 3:
            # Next term is in the same academic year
            return AcademicTerm.objects.filter(
                academic_year=self.term.academic_year,
                term=self.term.term + 1
            ).first()
        else:
            # Next term is first term of next year
            return AcademicTerm.objects.filter(
                academic_year=self.term.academic_year + 1,
                term=1
            ).first()