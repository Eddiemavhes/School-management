"""
GRADUATED WITH ARREARS MANAGEMENT SYSTEM
A strict, immutable, zero-tolerance system for Grade 7 students with unpaid fees.

Core Philosophy:
- Binary only: Either ALUMNI (paid in full) or GRADUATED_WITH_ARREARS (unpaid indefinitely)
- Immutable records: No adjustments, no waivers, no exceptions
- Automated enforcement: No administrative discretion
- Permanent tracking: Balances remain fixed forever
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class ArrearsVault(models.Model):
    """
    Permanent, immutable record for students who graduated with outstanding fees.
    
    This is a separate vault system to ensure complete isolation from active students
    and to enforce immutability of all records.
    
    CRITICAL CONSTRAINTS:
    - Once created, balance is IMMUTABLE
    - Only payment of 100% of balance triggers transition to ALUMNI
    - No updates, no adjustments, no exceptions
    - Records persist forever (no write-offs, no statute of limitations)
    """
    
    # Unique identifier
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Reference to original student (but no foreign key - keeps vault independent)
    student_id = models.IntegerField(
        help_text="Original student database ID (reference only, no FK)"
    )
    student_full_name = models.CharField(
        max_length=200,
        help_text="Snapshot of student name at graduation"
    )
    student_birth_entry = models.CharField(
        max_length=20,
        help_text="Snapshot of birth entry number at graduation"
    )
    
    # Immutable graduation data (frozen at creation)
    graduation_date = models.DateField(auto_now_add=True)
    graduation_year = models.IntegerField()  # 2026, 2027, etc.
    graduation_grade = models.CharField(max_length=3, default='7')  # Always 7
    
    # Frozen academic snapshot
    final_aggregate = models.CharField(
        max_length=50,
        blank=True,
        help_text="Academic performance at graduation (reference only)"
    )
    
    # FIXED BALANCE - THIS IS IMMUTABLE
    fixed_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],  # Must always be > 0 (else they'd be ALUMNI)
        help_text="Fixed outstanding amount - NEVER CHANGES until paid"
    )
    
    required_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount required for alumni transition - EQUALS fixed_balance"
    )
    
    # Frozen contact information
    parent_name = models.CharField(max_length=200)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField()
    
    # Status - always GRADUATED_WITH_ARREARS until transition
    status = models.CharField(
        max_length=50,
        default='GRADUATED_WITH_ARREARS',
        editable=False,  # Cannot be changed in admin
        help_text="Status is always GRADUATED_WITH_ARREARS until 100% paid"
    )
    
    # Payment tracking (not for balance, just for audit)
    total_payment_attempts = models.IntegerField(default=0)
    last_payment_attempt_date = models.DateTimeField(null=True, blank=True)
    last_payment_attempt_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Record of rejected or held payment"
    )
    total_escrowed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Partial payments held in escrow (awaiting full payment)"
    )
    
    # Timeline
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Transition (only when full payment received)
    transition_date = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        help_text="When student transitioned to ALUMNI (null if unpaid)"
    )
    transition_payment_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="How the final payment was made"
    )
    
    # Frozen flags
    is_locked = models.BooleanField(
        default=True,
        editable=False,
        help_text="Record is always locked (immutable)"
    )
    
    class Meta:
        db_table = 'arrears_vault_permanent'
        verbose_name = 'Graduated with Arrears (Vault)'
        verbose_name_plural = 'Graduated with Arrears (Vault)'
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['graduation_year']),
            models.Index(fields=['status']),
            models.Index(fields=['fixed_balance']),
        ]
        # Prevent any updates to balance or key fields
        constraints = [
            models.CheckConstraint(
                check=models.Q(fixed_balance__gt=0),
                name='arrears_balance_must_be_positive'
            ),
            models.CheckConstraint(
                check=models.Q(required_payment=models.F('fixed_balance')),
                name='required_payment_must_equal_balance'
            ),
            models.CheckConstraint(
                check=models.Q(status='GRADUATED_WITH_ARREARS'),
                name='status_must_be_graduated_with_arrears'
            ),
        ]
    
    def __str__(self):
        return f"{self.student_full_name} - {self.graduation_year} - ${self.fixed_balance}"
    
    def save(self, *args, **kwargs):
        """
        Override save to enforce immutability and ensure integrity.
        Only allow creation or transition payment.
        """
        if self.pk:  # Existing record
            # Check if this is an existing record
            existing = ArrearsVault.objects.filter(pk=self.pk).first()
            
            if existing:
                # Only allow setting transition_date (when paid)
                # Prevent all other changes
                if self.fixed_balance != existing.fixed_balance:
                    raise ValidationError("Balance is immutable - cannot be changed")
                if self.required_payment != existing.required_payment:
                    raise ValidationError("Required payment is immutable - cannot be changed")
                if self.status != existing.status and self.transition_date:
                    # This is transition to ALUMNI - allow it
                    pass
                elif self.status != existing.status:
                    raise ValidationError("Status can only change via full payment")
                if self.parent_name != existing.parent_name:
                    raise ValidationError("Parent information is frozen - cannot be changed")
        
        # Ensure required_payment equals fixed_balance
        self.required_payment = self.fixed_balance
        
        # Ensure status is always GRADUATED_WITH_ARREARS (unless transitioning)
        if not self.transition_date:
            self.status = 'GRADUATED_WITH_ARREARS'
        
        super().save(*args, **kwargs)
    
    def can_process_payment(self, amount):
        """
        Check if payment can be processed.
        
        ABSOLUTE RULE:
        - Only EXACT amount (fixed_balance) is accepted
        - Partial payments are rejected (but can be held in escrow)
        
        Returns: (accepted: bool, reason: str)
        """
        amount = Decimal(str(amount))
        
        if self.transition_date:
            return False, "Already paid in full and transitioned to ALUMNI"
        
        if amount == self.fixed_balance:
            return True, "Full payment - will transition to ALUMNI"
        elif amount > 0 and amount < self.fixed_balance:
            return False, f"Partial payment rejected. Required: ${self.fixed_balance}, Received: ${amount}. Full payment only."
        elif amount > self.fixed_balance:
            return False, f"Payment exceeds required amount. Required: ${self.fixed_balance}, Received: ${amount}"
        else:
            return False, "Invalid payment amount"
    
    def process_full_payment(self, amount, payment_method='Manual'):
        """
        Process payment that equals fixed_balance.
        This triggers transition to ALUMNI.
        """
        amount = Decimal(str(amount))
        
        if amount != self.fixed_balance:
            raise ValidationError(f"Payment must be exactly ${self.fixed_balance}")
        
        if self.transition_date:
            raise ValidationError("Already transitioned to ALUMNI")
        
        # Mark transition
        self.transition_date = timezone.now()
        self.transition_payment_method = payment_method
        self.status = 'ALUMNI'
        self.fixed_balance = Decimal('0.00')
        self.save()
        
        # Log this major event
        ArrearsPaymentLog.objects.create(
            vault=self,
            payment_amount=amount,
            payment_method=payment_method,
            result='ACCEPTED_FULL_PAYMENT',
            details=f'Transitioned to ALUMNI - Full payment received'
        )
        
        return True
    
    def hold_partial_payment(self, amount):
        """
        Hold partial payment in escrow.
        Balance remains unchanged.
        """
        amount = Decimal(str(amount))
        
        if amount >= self.fixed_balance:
            raise ValidationError("Use process_full_payment for full or exceeding amounts")
        
        self.total_escrowed += amount
        self.total_payment_attempts += 1
        self.last_payment_attempt_date = timezone.now()
        self.last_payment_attempt_amount = amount
        self.save(update_fields=[
            'total_escrowed',
            'total_payment_attempts',
            'last_payment_attempt_date',
            'last_payment_attempt_amount'
        ])
        
        # Log rejection
        ArrearsPaymentLog.objects.create(
            vault=self,
            payment_amount=amount,
            payment_method='Escrow',
            result='REJECTED_PARTIAL_PAYMENT',
            details=f'Partial payment held in escrow. Balance remains ${self.fixed_balance}'
        )
        
        return False


class ArrearsPaymentLog(models.Model):
    """Audit log for all payment attempts - never modified, only appended."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vault = models.ForeignKey(ArrearsVault, on_delete=models.PROTECT, related_name='payment_logs')
    
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    
    result = models.CharField(
        max_length=50,
        choices=[
            ('ACCEPTED_FULL_PAYMENT', 'Full Payment Accepted - Transition to ALUMNI'),
            ('REJECTED_PARTIAL_PAYMENT', 'Partial Payment Rejected - Held in Escrow'),
            ('REJECTED_EXCESS_PAYMENT', 'Excess Payment Rejected'),
            ('INVALID_AMOUNT', 'Invalid Amount'),
        ]
    )
    
    details = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    
    class Meta:
        db_table = 'arrears_payment_log'
        ordering = ['-created_at']
        verbose_name = 'Arrears Payment Log'
        verbose_name_plural = 'Arrears Payment Logs'
    
    def __str__(self):
        return f"{self.vault.student_full_name} - {self.result} - ${self.payment_amount}"


class ArrearsReport(models.Model):
    """System-generated reports (read-only) for tracking purposes."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Report metadata
    generated_date = models.DateTimeField(auto_now_add=True)
    report_type = models.CharField(
        max_length=50,
        choices=[
            ('DAILY_SUMMARY', 'Daily Summary'),
            ('MONTHLY_REPORT', 'Monthly Report'),
            ('ANNUAL_REPORT', 'Annual Report'),
            ('PERMANENT_REGISTER', 'Permanent Register'),
        ]
    )
    
    # Counts
    total_in_vault = models.IntegerField()
    total_arrears_amount = models.DecimalField(max_digits=12, decimal_places=2)
    oldest_graduation_year = models.IntegerField()
    collections_this_period = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    number_transitioned_to_alumni = models.IntegerField(default=0)
    
    # Statistics
    average_arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    largest_single_arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smallest_single_arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Policy enforcement
    rejected_partial_payments = models.IntegerField(default=0)
    administrative_exceptions_granted = models.IntegerField(default=0)  # Should always be 0
    
    report_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'arrears_reports'
        verbose_name = 'Arrears Report'
        verbose_name_plural = 'Arrears Reports'
        ordering = ['-generated_date']
    
    def __str__(self):
        return f"{self.report_type} - {self.generated_date.date()}"
