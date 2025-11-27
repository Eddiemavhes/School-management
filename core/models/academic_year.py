from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum, F
from .student import Student
from .academic import AcademicTerm
from .fee import StudentBalance, TermFee
from .class_model import Class

class AcademicYear(models.Model):
    """Model to manage academic years and handle rollovers"""
    year = models.IntegerField(help_text="Academic year (e.g., 2025)")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)  # Track if year has been completed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year']
        verbose_name = 'Academic Year'
        verbose_name_plural = 'Academic Years'

    def __str__(self):
        return f"Academic Year {self.year}"

    def clean(self):
        """Validate academic year data"""
        if self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date")
        
        # Ensure no overlapping academic years
        overlapping = AcademicYear.objects.exclude(id=self.id).filter(
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        )
        if overlapping.exists():
            raise ValidationError("Academic year dates overlap with existing academic year")
        
        if self.is_active:
            # Ensure only one active academic year
            AcademicYear.objects.exclude(id=self.id).update(is_active=False)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_current_year(cls):
        """Get the current academic year"""
        try:
            return cls.objects.get(is_active=True)
        except cls.DoesNotExist:
            return cls.objects.order_by('-year').first()

    def get_terms(self):
        """Get all terms in this academic year"""
        return AcademicTerm.objects.filter(academic_year=self.year).order_by('term')

    def get_current_term(self):
        """Get the current active term for this year"""
        return AcademicTerm.objects.filter(academic_year=self.year, is_current=True).first()

    def is_on_final_term(self):
        """Check if currently on Term 3 (final term)"""
        current_term = self.get_current_term()
        return current_term and current_term.term == 3

    def can_move_to_next_year(self):
        """Check if can move to next academic year"""
        if self.is_completed:
            return False  # Already completed
        
        if not self.is_active:
            return False  # Year is not active
        
        # Must be on Term 3 to advance to next year
        return self.is_on_final_term()

    def get_next_year(self):
        """Get the next academic year"""
        next_year_obj = AcademicYear.objects.filter(year=self.year + 1).first()
        return next_year_obj

    def create_terms(self, term_dates):
        """
        Create the three terms for this academic year
        
        Args:
            term_dates: List of dictionaries containing start_date, end_date, and fee_amount for each term
        """
        for term_num, dates in enumerate(term_dates, 1):
            term = AcademicTerm.objects.create(
                academic_year=self.year,
                term=term_num,
                start_date=dates['start_date'],
                end_date=dates['end_date'],
                is_current=False
            )
            # Create term fee
            if 'fee_amount' in dates:
                TermFee.objects.create(
                    term=term,
                    amount=dates['fee_amount']
                )

    def _validate_rollover(self):
        """Validate that rollover can proceed safely"""
        from django.core.exceptions import ValidationError
        
        new_year = self.year + 1
        
        # Validation 1: New year must not already exist
        self._validate_new_year_not_exists(new_year)
        
        # Validation 2: New year must be exactly current + 1
        self._validate_new_year_sequential(new_year)
        
        # Validation 3: All target classes must exist (checked via students with class assignments)
        # Already validated: Student class assignment required
        
        # Validation 4: All target classes must exist in new year
        self._validate_target_classes_exist(new_year)
        
        # Validation 5: New year must have all 3 terms configured with fees
        # This will be validated during new year creation, but check requirements
        self._validate_new_year_ready(new_year)
    
    def _validate_new_year_not_exists(self, new_year):
        """Validation 1: New year must not exist already"""
        from django.core.exceptions import ValidationError
        
        if AcademicYear.objects.filter(year=new_year).exists():
            raise ValidationError(
                f"Academic year {new_year} already exists. "
                f"Cannot rollover to an existing year."
            )
    
    def _validate_new_year_sequential(self, new_year):
        """Validation 2: New year must be exactly current + 1"""
        from django.core.exceptions import ValidationError
        
        expected_year = self.year + 1
        if new_year != expected_year:
            raise ValidationError(
                f"New academic year must be {expected_year}, not {new_year}. "
                f"Years must be sequential."
            )
    
    def _validate_target_classes_exist(self, new_year):
        """Validation 4: All target promotion classes must exist in new year"""
        from django.core.exceptions import ValidationError
        
        # Get all active students with class assignments
        students_to_promote = Student.objects.filter(
            is_active=True,
            current_class__isnull=False
        )
        
        missing_classes = []
        for student in students_to_promote:
            current_grade = student.current_class.grade
            current_section = student.current_class.section
            
            # Check if student will be promoted (grade < 7)
            if current_grade < 7:
                next_grade = current_grade + 1
                
                # Check if target class exists
                target_class = Class.objects.filter(
                    grade=next_grade,
                    section=current_section,
                    academic_year=new_year
                ).exists()
                
                if not target_class:
                    # Check if ANY class exists in that grade (fallback)
                    any_grade_class = Class.objects.filter(
                        grade=next_grade,
                        academic_year=new_year
                    ).exists()
                    
                    if not any_grade_class:
                        class_key = f"Grade {next_grade} (for {next_grade-1}{current_section})"
                        if class_key not in missing_classes:
                            missing_classes.append(class_key)
        
        if missing_classes:
            raise ValidationError(
                f"Cannot rollover: The following classes must exist in {new_year} "
                f"for student promotion: {', '.join(missing_classes)}. "
                f"Please create these classes before rolling over."
            )
    
    def _validate_new_year_ready(self, new_year):
        """Validation 5: Check if new year setup prerequisites are met"""
        from django.core.exceptions import ValidationError
        
        # This validation checks the NEW year has the basic structure
        # Actual term creation will happen during rollover
        # This is more of a pre-check to guide the user
        
        # For now, we just validate the new year doesn't exist (done in validation 1)
        # The terms and fees will be created from the current year's structure
        pass

    def rollover_to_new_year(self):
        """
        Handle year rollover process including:
        - Creating new academic year
        - Promoting students
        - Preserving arrears
        """
        from django.db import transaction
        from django.core.exceptions import ValidationError

        # Validate rollover before proceeding
        self._validate_rollover()

        # Calculate new year dates (assuming standard academic calendar)
        new_year = self.year + 1
        new_start_date = self.end_date.replace(year=self.end_date.year + 1)
        new_end_date = self.start_date.replace(year=self.start_date.year + 2)

        with transaction.atomic():
            # Create new academic year
            new_academic_year = AcademicYear.objects.create(
                year=new_year,
                start_date=new_start_date,
                end_date=new_end_date,
                is_active=False  # Don't automatically activate
            )

            # Get all current year's terms for fee structure
            current_terms = self.get_terms()
            
            # Create new terms with same fee structure
            new_term_dates = []
            for term in current_terms:
                term_fee = TermFee.objects.get(term=term)
                new_term_dates.append({
                    'start_date': term.start_date.replace(year=new_start_date.year),
                    'end_date': term.end_date.replace(year=new_start_date.year),
                    'fee_amount': term_fee.amount
                })
            
            # Create terms for new year
            new_academic_year.create_terms(new_term_dates)

            # Handle student promotions - move students to next grade classes in new year
            students = Student.objects.filter(is_active=True)
            for student in students:
                # Calculate total arrears for current year
                total_arrears = StudentBalance.objects.filter(
                    student=student,
                    term__academic_year=self.year
                ).aggregate(
                    total=Sum(F('term_fee') + F('previous_arrears') - F('amount_paid'))
                )['total'] or 0

                # If student has a current class, handle promotion
                if student.current_class:
                    current_grade = student.current_class.grade
                    current_section = student.current_class.section
                    
                    # Only promote if not in final grade (7 is the highest)
                    if current_grade < 7:
                        next_grade = current_grade + 1
                        
                        # Find the EXISTING next grade class in the new academic year
                        # (These classes should already be created and waiting for students)
                        next_class = Class.objects.filter(
                            grade=next_grade,
                            section=current_section,
                            academic_year=new_year,
                        ).first()
                        
                        # If the same-section class doesn't exist, find any class in that grade
                        if not next_class:
                            next_class = Class.objects.filter(
                                grade=next_grade,
                                academic_year=new_year,
                            ).first()
                        
                        # If a class exists in the new year, promote student
                        if next_class:
                            student.current_class = next_class
                        else:
                            print(f"Warning: No Grade {next_grade} class exists in {new_year} for student {student.full_name}. Student not promoted.")
                    else:
                        # Student is graduating
                        student.is_active = False
                    
                    student.save()

                # Store arrears for first term of new year using initialize_term_balance
                # This ensures proper calculation of what carries over from previous year
                first_term = AcademicTerm.objects.get(academic_year=new_year, term=1)
                try:
                    StudentBalance.initialize_term_balance(student, first_term)
                except Exception as e:
                    print(f"Warning: Could not initialize balance for {student.full_name} in {new_year}: {e}")

            return new_academic_year

    def activate(self):
        """Activate this academic year and deactivate others"""
        AcademicYear.objects.all().update(is_active=False)
        self.is_active = True
        self.save()

    def get_financial_summary(self):
        """Get financial summary for the academic year"""
        terms = self.get_terms()
        summary = {
            'total_expected': 0,
            'total_collected': 0,
            'total_arrears': 0,
            'terms': []
        }

        for term in terms:
            term_summary = {
                'term': term.get_term_display(),
                'expected': 0,
                'collected': 0,
                'arrears': 0
            }

            balances = StudentBalance.objects.filter(term=term)
            term_summary['expected'] = balances.aggregate(
                total=Sum(F('term_fee') + F('previous_arrears')))['total'] or 0
            term_summary['collected'] = balances.aggregate(
                total=Sum('amount_paid'))['total'] or 0
            term_summary['arrears'] = term_summary['expected'] - term_summary['collected']

            summary['terms'].append(term_summary)
            summary['total_expected'] += term_summary['expected']
            summary['total_collected'] += term_summary['collected']
            summary['total_arrears'] += term_summary['arrears']

        summary['collection_rate'] = (
            (summary['total_collected'] / summary['total_expected'] * 100)
            if summary['total_expected'] else 0
        )

        return summary