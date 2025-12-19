"""
Payment Allocation System - Model for tracking how payments are allocated across terms
"""

from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, F, Q
from django.core.exceptions import ValidationError

class PaymentAllocation(models.Model):
    """
    Track how a bulk payment is allocated across multiple terms.
    
    Example:
    - Student pays 400 in one transaction
    - This creates 1 Payment record with amount=400
    - But creates 4 PaymentAllocation records:
      - Allocation 1: Term 1, allocated 100
      - Allocation 2: Term 2, allocated 100
      - Allocation 3: Term 3, allocated 100
      - Allocation 4: Term 4 (or credit), allocated 100 (as credit)
    """
    
    payment = models.ForeignKey(
        'Payment',
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name='payment_allocations'
    )
    term = models.ForeignKey(
        'AcademicTerm',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The term this allocation applies to. NULL for credit balances."
    )
    allocated_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount allocated to this term or held as credit"
    )
    allocation_type = models.CharField(
        max_length=20,
        choices=[
            ('TERM_PAYMENT', 'Payment for specific term'),
            ('ARREARS_CLEARANCE', 'Clearing arrears from previous term'),
            ('CREDIT', 'Excess payment held as credit'),
        ],
        default='TERM_PAYMENT'
    )
    priority_order = models.IntegerField(
        help_text="Order in which allocations are applied (lower = first). Arrears cleared first."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['payment', 'priority_order']
        unique_together = ['payment', 'term', 'allocation_type']
    
    def __str__(self):
        if self.allocation_type == 'CREDIT':
            return f"Credit {self.allocated_amount} for {self.student}"
        return f"Allocation {self.allocated_amount} to {self.term} for {self.student}"


class PaymentAllocationLog(models.Model):
    """
    Audit log for payment allocation process.
    Tracks the state before and after each allocation decision.
    """
    
    payment = models.ForeignKey(
        'Payment',
        on_delete=models.CASCADE,
        related_name='allocation_logs'
    )
    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name='allocation_logs'
    )
    action = models.CharField(
        max_length=200,
        help_text="Description of allocation action taken"
    )
    remaining_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Payment amount remaining after this action"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} - {self.action}"


class StudentCredit(models.Model):
    """
    Track credit balances for students.
    
    Credits are created when:
    1. Student overpays (payment > total due)
    2. Explicitly issued for good performance, scholarships, etc.
    
    Credits are used when:
    1. Allocated to next term's fees (oldest first)
    2. Student withdraws (less common, usually not allowed)
    """
    
    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name='credits'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount of credit available"
    )
    source = models.CharField(
        max_length=50,
        choices=[
            ('OVERPAYMENT', 'From overpayment'),
            ('SCHOLARSHIP', 'Scholarship/waiver'),
            ('ADJUSTMENT', 'Administrative adjustment'),
            ('GOODWILL', 'Goodwill credit'),
        ],
        default='OVERPAYMENT'
    )
    source_payment = models.ForeignKey(
        'Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_credits',
        help_text="The payment that generated this credit (if from overpayment)"
    )
    applied_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Amount that has been applied/used from this credit"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        remaining = self.available_amount
        return f"Credit ${remaining:.2f} for {self.student}"
    
    @property
    def available_amount(self):
        """Amount of credit still available to use"""
        return self.amount - self.applied_amount
    
    @property
    def is_fully_used(self):
        """Check if credit has been completely applied"""
        return self.available_amount <= 0
    
    def apply_credit(self, amount):
        """Apply credit to a payment"""
        if amount > self.available_amount:
            raise ValidationError(
                f"Cannot apply ${amount:.2f}. Only ${self.available_amount:.2f} available."
            )
        self.applied_amount += amount
        self.save()
    
    def refund_credit(self, amount):
        """Refund/reverse credit application (e.g., if payment was reversed)"""
        self.applied_amount = max(Decimal('0'), self.applied_amount - amount)
        self.save()
