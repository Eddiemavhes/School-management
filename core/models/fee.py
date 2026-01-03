from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, Q
from django.core.exceptions import ValidationError

class TermFee(models.Model):
    """Model to store the base fee amount for each term, separated by grade level"""
    # Grade level choices: ECD is separate from primary (Grade 1-7)
    GRADE_LEVEL_CHOICES = [
        ('ECD', 'Early Childhood Development (ECD)'),
        ('PRIMARY', 'Primary (Grades 1-7)'),
    ]
    
    term = models.ForeignKey('AcademicTerm', on_delete=models.PROTECT)
    grade_level = models.CharField(max_length=10, choices=GRADE_LEVEL_CHOICES, default='PRIMARY')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['term', 'grade_level']
        ordering = ['-term__academic_year', '-term__term', 'grade_level']

    def __str__(self):
        return f"{self.term} ({self.get_grade_level_display()}) - ${self.amount}"

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
    term_fee_record = models.ForeignKey('TermFee', on_delete=models.PROTECT, help_text="Link to the term fee configuration")
    previous_arrears = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Balance from previous term (positive=owe, negative=credit)"
    )
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
        # Auto-assign correct TermFee based on student's grade if not already set
        if not self.term_fee_record and self.student.current_class:
            self.term_fee_record = self.get_appropriate_term_fee()
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_appropriate_term_fee(self):
        """Get the correct TermFee for this student based on their class grade.
        
        Returns:
            TermFee: ECD fees for ECD students, PRIMARY fees for Grade 1-7 students
        """
        if not self.student.current_class:
            raise ValidationError("Student must have a current class to determine appropriate fee")
        
        # Determine grade level from student's current class
        student_grade = self.student.current_class.grade
        if student_grade == 'ECD':
            grade_level = 'ECD'
        else:
            grade_level = 'PRIMARY'  # Grades 1-7 all use PRIMARY fees
        
        try:
            return TermFee.objects.get(term=self.term, grade_level=grade_level)
        except TermFee.DoesNotExist:
            raise ValidationError(
                f"No fee configured for {grade_level} students in {self.term}. "
                f"Please create a TermFee record in admin."
            )
    
    @property
    def term_fee(self):
        """Dynamically get current term fee from TermFee record"""
        base = self.term_fee_record.amount

        # If the student is in an ECD class, include any per-class ECD fees for this term
        try:
            if self.student and self.student.current_class and self.student.current_class.grade == 'ECD':
                # Sum any ECDClassFee records for this class and term
                from .ecd import ECDClassFee
                extras = ECDClassFee.objects.filter(cls=self.student.current_class, term=self.term).aggregate(total=models.Sum('amount'))['total']
                if extras:
                    from decimal import Decimal
                    base = base + Decimal(str(extras))
        except Exception:
            # If anything goes wrong here, fall back to base fee to avoid blocking billing
            pass

        return base
    
    @property
    def total_due(self):
        """Calculate total amount due including arrears and credits
        
        Formula: term_fee + previous_arrears
        Where:
        - term_fee = original charge for this term
        - previous_arrears = balance from previous term (+ owe, - credit)
        - If previous_arrears is negative (credit), it reduces the total due
        """
        return self.term_fee + self.previous_arrears

    @property
    def current_balance(self):
        """Calculate current balance (what student still owes or has as credit)
        
        Formula: total_due - amount_paid
        - If positive: student owes this amount
        - If negative: student has credit (school owes student)
        """
        return self.total_due - self.amount_paid

    @property
    def current_outstanding(self):
        """Show only positive outstanding (amount student owes)
        
        Returns 0 if student has paid in full or has credit
        """
        return max(Decimal('0'), self.current_balance)

    @property
    def current_credit(self):
        """Show only credit balance (amount school owes student)
        
        Returns 0 if student has outstanding or no credit
        """
        return max(Decimal('0'), -self.current_balance)

    @property
    def payment_status(self):
        """Return the payment status for display in UI
        
        Returns:
        - 'PAID': Student has paid in full (amount_paid >= total_due)
        - 'PARTIAL': Student has made partial payment (0 < amount_paid < total_due)
        - 'UNPAID': Student has not made any payment (amount_paid == 0)
        """
        total_due = self.term_fee + self.previous_arrears
        
        if total_due <= 0:
            # If no amount due (credit or zero), mark as paid
            return 'PAID'
        
        if self.amount_paid >= total_due:
            return 'PAID'
        elif self.amount_paid > 0:
            return 'PARTIAL'
        else:
            return 'UNPAID'

    @property
    def arrears_remaining(self):
        """Return how much of previous arrears/credits still needs to be handled
        
        - If positive: amount of arrears still owed (must pay this first)
        - If negative: amount of credit available (reduces current term fee)
        
        For compatibility with legacy code
        """
        if self.previous_arrears > 0:
            # Positive arrears: they're paid first
            return max(Decimal('0'), self.previous_arrears - self.amount_paid)
        else:
            # Negative arrears (credit) or zero - no arrears owed
            return Decimal('0')

    @property
    def term_fee_remaining(self):
        """Return how much of current term fee still needs to be paid
        
        For compatibility with legacy code that needs to understand payment breakdown
        """
        if self.previous_arrears > 0:
            # Positive arrears: payment goes to arrears first, then term fee
            amount_to_current_fee = max(Decimal('0'), self.amount_paid - self.previous_arrears)
            return max(Decimal('0'), self.term_fee - amount_to_current_fee)
        else:
            # Negative arrears (credit): reduces term fee, then remaining payment applies
            # For example: term_fee=$120, previous_arrears=-$30, amount_paid=$0
            # Effective fee = $120 + (-$30) = $90
            effective_fee = self.term_fee + self.previous_arrears
            return max(Decimal('0'), effective_fee - self.amount_paid)

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
                balance = cls.objects.get(student=student, term=term)
                
                # IMPORTANT: Even for inactive students, recalculate arrears in case previous term changed
                # This ensures credits/arrears carry forward correctly
                recalculated_arrears = cls.calculate_arrears(student, term)
                if balance.previous_arrears != recalculated_arrears:
                    balance.previous_arrears = recalculated_arrears
                    balance.save()
                
                return balance
            except cls.DoesNotExist:
                # Don't create new balance for graduated students in current term
                return None
        
        # GRADE 7 CHECK FOR NEW ACADEMIC YEAR:
        # Grade 7 students who enter a new academic year without paying their previous year's balance
        # should NOT get new term fees. They only carry forward their arrears.
        # This is to prevent Grade 7 students from accumulating unlimited fees if they don't pay.
        if term.term == 1 and student.current_class:  # First term of new year
            # Only numeric grades are considered for the Grade 7 rule; skip for ECD
            try:
                grade_int = int(student.current_class.grade)
            except Exception:
                grade_int = None

            if grade_int and grade_int >= 7:  # Grade 7 or higher
                # Check if there's a balance from the previous academic year
                previous_year_last_balance = cls.objects.filter(
                    student=student,
                    term__academic_year=term.academic_year - 1
                ).order_by('-term__term').first()
                
                if previous_year_last_balance and previous_year_last_balance.current_balance > 0:
                    # Grade 7 student with outstanding balance from previous year
                    # Get the term fee but still create balance (for tracking)
                    try:
                        term_fee = TermFee.objects.get(term=term)
                    except TermFee.DoesNotExist:
                        raise ValidationError("Term fee has not been set for this term")
                    
                    # Do NOT charge new fee - only carry forward the arrears
                    balance, created = cls.objects.get_or_create(
                        student=student,
                        term=term,
                        defaults={
                            'term_fee_record': term_fee,
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

        # Include any arrears records that were imported and applied to this term
        try:
            from core.models.arrears_import import StudentArrearsRecord
            from django.db.models import Sum
            applied_sum = StudentArrearsRecord.objects.filter(
                student=student,
                is_applied_to_balance=True,
                applied_to_term=term
            ).aggregate(total=Sum('total_arrears'))['total'] or Decimal('0')
        except Exception:
            applied_sum = Decimal('0')

        previous_arrears = (previous_arrears or Decimal('0')) + (applied_sum or Decimal('0'))
        
        # CRITICAL FIX: Always charge the full term fee
        # The 'previous_arrears' field handles credits (negative values)
        # 
        # ALWAYS set term_fee to the actual fee amount
        # Do NOT set it to 0 even if credit covers it - we need to track the original fee
        # 
        # Example (CORRECT logic):
        #   Term 2: Fee=$100, Payment=$120 → current_balance=$20 (credit)
        #   Term 3: term_fee=$100, previous_arrears=-$20 (credit)
        #   Total Due = $100 + (-$20) = $80
        #   This shows the student owes $80 after credit is applied
        # 
        # Example (WRONG logic - what was happening):
        #   Term 2: Fee=$100, Payment=$120 → current_balance=$20 (credit)
        #   Term 3: term_fee=$0 (WRONG!), previous_arrears=-$20
        #   Total Due = $0 + (-$20) = -$20 (loses track that fee was $100)
        new_term_fee = term_fee.amount

        
        balance, created = cls.objects.get_or_create(
            student=student,
            term=term,
            defaults={
                'term_fee_record': term_fee,
                'previous_arrears': previous_arrears,
                'amount_paid': Decimal('0')
            }
        )
        
        # PERMANENT FIX: Always verify and recalculate previous_arrears
        # This ensures credits carry forward correctly from previous terms
        # 
        # ISSUE: When Term 3 becomes current, Term 2's payment may not be processed yet
        # causing calculate_arrears() to return wrong value during initial creation.
        # SOLUTION: Always recalculate and verify after get_or_create
        # Recalculate arrears including any applied/imported arrears for this term
        try:
            from core.models.arrears_import import StudentArrearsRecord
            from django.db.models import Sum
            applied_sum = StudentArrearsRecord.objects.filter(
                student=student,
                is_applied_to_balance=True,
                applied_to_term=term
            ).aggregate(total=Sum('total_arrears'))['total'] or Decimal('0')
        except Exception:
            applied_sum = Decimal('0')

        recalculated_arrears = (cls.calculate_arrears(student, term) or Decimal('0')) + (applied_sum or Decimal('0'))

        # Only increase previous_arrears automatically — do not overwrite a larger imported value
        current_prev = balance.previous_arrears or Decimal('0')
        if recalculated_arrears > current_prev:
            balance.previous_arrears = recalculated_arrears
            balance.save(update_fields=['previous_arrears'])
            
        return balance