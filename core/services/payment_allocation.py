"""
Payment Allocation Service - Handles the business logic for allocating bulk payments
across multiple terms.

This service implements the allocation algorithm:
1. Get all unpaid/partially paid terms (oldest first)
2. Apply payment to arrears first (if any)
3. Apply remaining payment to term fees (oldest first)
4. Create credit for any excess payment
"""

from decimal import Decimal
from django.db.models import Sum, Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import (
    Payment, StudentBalance, AcademicTerm, PaymentAllocation, 
    PaymentAllocationLog, StudentCredit
)


class PaymentAllocationService:
    """Service for allocating bulk payments across multiple terms"""
    
    def __init__(self, payment):
        """
        Initialize the service with a payment object.
        
        Args:
            payment: Payment instance to allocate
        """
        self.payment = payment
        self.student = payment.student
        self.payment_amount = payment.amount
        self.remaining_amount = Decimal(str(payment.amount))
        self.allocations = []
        self.allocation_log = []
    
    def allocate(self):
        """
        Execute the payment allocation algorithm.
        
        Process:
        1. Get all unpaid/partially paid terms (oldest first)
        2. Apply payment to arrears first
        3. Apply payment to current term fees
        4. Create credit for excess
        
        Returns:
            dict with allocation results
        """
        # Step 1: Apply existing credits first (if any)
        self._apply_existing_credits()
        
        # Step 2: Get terms that need payment (oldest first)
        terms_to_pay = self._get_terms_needing_payment()
        
        # Step 3: Allocate to each term
        priority_order = 1
        for balance in terms_to_pay:
            if self.remaining_amount <= 0:
                break
            
            priority_order = self._allocate_to_term(balance, priority_order)
        
        # Step 4: Handle any remaining amount as credit
        if self.remaining_amount > 0:
            self._create_credit(self.remaining_amount)
        
        # Step 5: Save all allocations to database
        self._save_allocations()
        
        return {
            'payment_id': self.payment.id,
            'total_allocated': self.payment_amount - self.remaining_amount,
            'credit_created': self.remaining_amount if self.remaining_amount > 0 else Decimal('0'),
            'allocations': self.allocations,
            'log': self.allocation_log
        }
    
    def _apply_existing_credits(self):
        """Apply existing student credits to oldest unpaid terms"""
        # Get all available credits for this student (oldest first)
        available_credits = StudentCredit.objects.filter(
            student=self.student,
            applied_amount__lt=models.F('amount')
        ).order_by('created_at')
        
        for credit in available_credits:
            if self.remaining_amount <= 0:
                break
            
            credit_available = credit.available_amount
            amount_to_use = min(self.remaining_amount, credit_available)
            
            # Apply credit
            credit.apply_credit(amount_to_use)
            self.remaining_amount -= amount_to_use
            
            self.allocation_log.append(
                f"Applied existing credit of ${amount_to_use:.2f} (Credit ID: {credit.id})"
            )
    
    def _get_terms_needing_payment(self):
        """
        Get all terms that need payment, sorted by date (oldest first).
        
        Includes:
        - Current academic year terms
        - Previous academic years (for arrears)
        
        Returns:
            List of StudentBalance objects ordered by term date
        """
        # Get all balances for this student
        all_balances = StudentBalance.objects.filter(
            student=self.student
        ).select_related('term').order_by(
            'term__academic_year', 'term__term'
        )
        
        # Filter to only those that need payment (using property evaluation)
        terms_needing_payment = [
            balance for balance in all_balances 
            if balance.current_balance > Decimal('0')
        ]
        
        return terms_needing_payment
    
    def _allocate_to_term(self, balance, priority_order):
        """
        Allocate payment to a specific term.
        
        Priority:
        1. Clear arrears first (previous_arrears)
        2. Then pay current term fee
        
        Args:
            balance: StudentBalance instance
            priority_order: Order for allocation prioritization
            
        Returns:
            Updated priority_order
        """
        term = balance.term
        term_due = balance.current_balance  # Total amount still due
        
        if term_due <= 0:
            # Term already paid
            return priority_order
        
        # Amount to allocate to this term (limited by remaining payment)
        allocation = min(self.remaining_amount, term_due)
        
        # Record allocation
        allocation_record = {
            'term': term,
            'amount': allocation,
            'term_total_due': term_due,
            'type': 'TERM_PAYMENT',
            'priority': priority_order
        }
        
        self.allocations.append(allocation_record)
        
        # Log the action
        self.allocation_log.append(
            f"Allocated ${allocation:.2f} to {term} (due: ${term_due:.2f})"
        )
        
        # Update remaining amount
        self.remaining_amount -= allocation
        
        return priority_order + 1
    
    def _create_credit(self, amount):
        """
        Create a credit balance for excess payment.
        
        Args:
            amount: Credit amount to create
        """
        credit = StudentCredit.objects.create(
            student=self.student,
            amount=amount,
            source='OVERPAYMENT',
            source_payment=self.payment,
            notes=f"Overpayment from payment {self.payment.receipt_number}"
        )
        
        self.allocation_log.append(
            f"Created credit of ${amount:.2f} for future terms (Credit ID: {credit.id})"
        )
        
        self.allocations.append({
            'term': None,
            'amount': amount,
            'term_total_due': None,
            'type': 'CREDIT',
            'priority': 999  # Credit is lowest priority
        })
    
    def _save_allocations(self):
        """Save all allocations to database as PaymentAllocation records"""
        for i, alloc in enumerate(self.allocations):
            # Only save non-credit allocations to PaymentAllocation table
            # Credits are handled separately via StudentCredit model
            if alloc['type'] != 'CREDIT':
                PaymentAllocation.objects.create(
                    payment=self.payment,
                    student=self.student,
                    term=alloc['term'],
                    allocated_amount=alloc['amount'],
                    allocation_type='TERM_PAYMENT',
                    priority_order=i
                )
        
        # Save allocation logs
        for log_entry in self.allocation_log:
            PaymentAllocationLog.objects.create(
                payment=self.payment,
                student=self.student,
                action=log_entry,
                remaining_payment=self.remaining_amount
            )


# Import at bottom to avoid circular imports
from django.db import models
