from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, Q
from django.core.exceptions import ValidationError

class TermFee(models.Model):
    """Model to store the base fee amount for each term"""
    term = models.ForeignKey('AcademicTerm', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['term']
        ordering = ['-term__academic_year', '-term__term']

    def __str__(self):
        return f"{self.term} - {self.amount}"

    def clean(self):
        """Comprehensive TermFee validation"""
        # Validation: Cannot modify fee if payments have been recorded
        self._validate_no_modification_after_payments()
    
    def _validate_no_modification_after_payments(self):
        """Validation: Cannot modify fee after payments recorded"""
        # Only check if this is an existing record (has primary key)
        if self.pk:
            # Check if any payments exist for this term
            from .academic import Payment
            payment_count = Payment.objects.filter(term=self.term).count()
            
            if payment_count > 0:
                # Get original values to see if anything changed
                original = TermFee.objects.get(pk=self.pk)
                if original.amount != self.amount:
                    raise ValidationError(
                        f"Cannot modify term fee after payments have been recorded. "
                        f"{payment_count} payment(s) exist for {self.term}. "
                        f"Original fee: ${original.amount}"
                    )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class StudentBalance(models.Model):
    """Model to track student balances and arrears"""
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='balances')
    term = models.ForeignKey('AcademicTerm', on_delete=models.PROTECT)
    term_fee = models.DecimalField(max_digits=10, decimal_places=2)
    previous_arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_payment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'term']
        ordering = ['-term__academic_year', '-term__term']

    def __str__(self):
        return f"{self.student} - {self.term}"

    def clean(self):
        """Validate student balance"""
        # Validation 1: Student must be enrolled before billing
        self._validate_enrollment_status()
    
    def _validate_enrollment_status(self):
        """Validation: Student must be enrolled (not withdrawn) before creating balance"""
        # A student with date_enrolled but no current_class is considered not properly enrolled
        if not self.student.current_class:
            raise ValidationError(
                f"Cannot create balance for {self.student.full_name}. "
                f"Student must be enrolled in a class before billing."
            )
        
        # Allow mid-term enrollment: if student enrolled after term started, but term is current/ongoing
        # Only reject if the term has already ended (historical records)
        if self.student.date_enrolled > self.term.start_date:
            from django.utils import timezone
            today = timezone.now().date()
            
            # If the term has already ended and student enrolled after it started, reject it (historical/impossible case)
            if today > self.term.end_date:
                raise ValidationError(
                    f"Cannot create balance for {self.student.full_name}. "
                    f"Student was enrolled on {self.student.date_enrolled} but term started on {self.term.start_date} and ended {self.term.end_date}. "
                    f"Cannot create fees for past terms."
                )
            # Otherwise allow it - student enrolled mid-term but term is still active/ongoing
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    @property
    def total_due(self):
        """Calculate total amount due including arrears"""
        return self.term_fee + self.previous_arrears

    @property
    def current_balance(self):
        """Calculate current balance"""
        return self.total_due - self.amount_paid

    @property
    def payment_status(self):
        """Determine payment status with color coding"""
        if self.current_balance <= 0:
            return 'PAID'  # Green
        elif self.amount_paid > 0:
            return 'PARTIAL'  # Yellow
        return 'UNPAID'  # Red

    @property
    def arrears_remaining(self):
        """Return how much of previous arrears/credits still needs to be handled
        
        - If positive: amount of arrears still owed (must pay this first)
        - If negative: amount of credit available (reduces current term fee)
        """
        if self.previous_arrears > 0:
            # Positive arrears: they're paid first, so cleared only if amount_paid >= previous_arrears
            arrears_paid = min(self.amount_paid, self.previous_arrears)
            return self.previous_arrears - arrears_paid
        else:
            # Negative arrears (credit) or zero - no arrears owed
            return 0

    @property
    def term_fee_remaining(self):
        """Return how much of current term fee still needs to be paid
        
        Calculation:
        1. If previous_arrears is positive (debt): payment goes there first
        2. After clearing arrears, remaining payment goes to term fee
        3. If previous_arrears is negative (credit): reduces the term fee directly
        """
        if self.previous_arrears > 0:
            # Positive arrears: payment goes to arrears first, then term fee
            amount_to_current_fee = max(0, self.amount_paid - self.previous_arrears)
            return max(0, self.term_fee - amount_to_current_fee)
        else:
            # Negative arrears (credit): reduces term fee, then remaining payment applies
            # For example: term_fee=$120, previous_arrears=-$30, amount_paid=$0
            # Effective fee = $120 + (-$30) = $90
            effective_fee = self.term_fee + self.previous_arrears
            return max(0, effective_fee - self.amount_paid)

    @property
    def payment_priority(self):
        """Return payment priority text"""
        if self.arrears_remaining > 0:
            return f"Must pay ${self.arrears_remaining:.2f} in ARREARS first"
        elif self.term_fee_remaining > 0:
            return f"${self.term_fee_remaining:.2f} remaining for current term fee"
        else:
            return "Fully paid up"

    def update_balance(self, payment_amount=None):
        """Update balance - recalculates amount_paid from actual Payment records"""
        from .academic import Payment
        
        # Recalculate amount_paid from actual Payment records for this term
        total_paid = Payment.objects.filter(
            student=self.student,
            term=self.term
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        self.amount_paid = Decimal(str(total_paid))
        self.last_payment_date = timezone.now().date()
        self.save()

    @classmethod
    def calculate_arrears(cls, student, term):
        """Calculate total arrears/credits from all previous terms
        
        - Positive value = arrears (student owes money from previous term)
        - Negative value = credit (student overpaid previous term, to be applied now)
        - Zero = fully paid previous term
        """
        # Get the previous term in the same year
        try:
            if term.term > 1:
                # Previous term is in the same year
                previous_term = cls.objects.get(
                    student=student,
                    term__academic_year=term.academic_year,
                    term__term=term.term - 1
                )
                # Return the balance AS-IS (can be positive for arrears, negative for credit)
                return previous_term.current_balance
            else:
                # This is Term 1, check if there's a balance from previous year
                previous_year_last_term = cls.objects.filter(
                    student=student,
                    term__academic_year=term.academic_year - 1
                ).order_by('-term__term').first()
                
                if previous_year_last_term:
                    # Return the balance AS-IS (can be positive for arrears, negative for credit)
                    return previous_year_last_term.current_balance
                else:
                    return Decimal('0')
        except cls.DoesNotExist:
            return Decimal('0')

    @classmethod
    def initialize_term_balance(cls, student, term):
        """Initialize or get a student's balance for a term"""
        # IMPORTANT: Graduated/Inactive students should NOT have new term fees
        if not student.is_active:
            # Only return balance for previous terms (arrears), not current term
            try:
                # Try to get existing balance
                return cls.objects.get(student=student, term=term)
            except cls.DoesNotExist:
                # Don't create new balance for graduated students in current term
                return None
        
        # GRADE 7 CHECK FOR NEW ACADEMIC YEAR:
        # Grade 7 students who enter a new academic year without paying their previous year's balance
        # should NOT get new term fees. They only carry forward their arrears.
        # This is to prevent Grade 7 students from accumulating unlimited fees if they don't pay.
        if term.term == 1 and student.current_class:  # First term of new year
            if int(student.current_class.grade) >= 7:  # Grade 7 or higher
                # Check if there's a balance from the previous academic year
                previous_year_last_balance = cls.objects.filter(
                    student=student,
                    term__academic_year=term.academic_year - 1
                ).order_by('-term__term').first()
                
                if previous_year_last_balance and previous_year_last_balance.current_balance > 0:
                    # Grade 7 student with outstanding balance from previous year
                    # Do NOT charge new fee - only carry forward the arrears
                    balance, created = cls.objects.get_or_create(
                        student=student,
                        term=term,
                        defaults={
                            'term_fee': Decimal('0'),  # NO new fee for Grade 7 with arrears
                            'previous_arrears': previous_year_last_balance.current_balance,
                            'amount_paid': Decimal('0')
                        }
                    )
                    return balance
        
        try:
            term_fee = TermFee.objects.get(term=term)
        except TermFee.DoesNotExist:
            raise ValidationError("Term fee has not been set for this term")

        previous_arrears = cls.calculate_arrears(student, term)
        
        balance, created = cls.objects.get_or_create(
            student=student,
            term=term,
            defaults={
                'term_fee': term_fee.amount,
                'previous_arrears': previous_arrears,
                'amount_paid': Decimal('0')  # New balances always start at 0 paid
            }
        )
        
        if not created:
            # Balance already exists - update term_fee and recalculate arrears
            # Arrears might change if previous term's balance was updated
            updates_needed = False
            
            if balance.term_fee != term_fee.amount:
                balance.term_fee = term_fee.amount
                updates_needed = True
            
            # IMPORTANT: Always recalculate arrears in case previous term changed
            # This ensures credits/arrears carry forward correctly
            recalculated_arrears = cls.calculate_arrears(student, term)
            if balance.previous_arrears != recalculated_arrears:
                balance.previous_arrears = recalculated_arrears
                updates_needed = True
            
            if updates_needed:
                balance.save()
            
        return balance