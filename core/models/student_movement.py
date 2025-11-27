from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from .class_model import Class
from .student import Student
from .administrator import Administrator

class StudentMovement(models.Model):
    MOVEMENT_TYPES = [
        ('PROMOTION', 'Promotion'),
        ('DEMOTION', 'Demotion'),
        ('TRANSFER', 'Transfer'),
        ('GRADUATION', 'Graduation')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='movements')
    from_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, related_name='student_departures')
    to_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, related_name='student_arrivals')
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    movement_date = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True, null=True)
    moved_by = models.ForeignKey(Administrator, on_delete=models.SET_NULL, null=True)
    previous_arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preserved_arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_bulk_operation = models.BooleanField(default=False)
    bulk_operation_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-movement_date']
        indexes = [
            models.Index(fields=['movement_date']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['bulk_operation_id']),
        ]

    def __str__(self):
        return f"{self.student} - {self.movement_type} - {self.movement_date.date()}"
    
    def clean(self):
        """Validate student movement based on movement type"""
        # Validation 1: Student prerequisites - must be active, not graduated, have class
        self._validate_student_prerequisites()
        
        # Validation 2: Promotion validation - grade must increase
        if self.movement_type == 'PROMOTION':
            self._validate_promotion()
        
        # Validation 3: Demotion validation - grade must decrease, reason required
        elif self.movement_type == 'DEMOTION':
            self._validate_demotion()
        
        # Validation 4: Transfer validation - same grade, same year, different class
        elif self.movement_type == 'TRANSFER':
            self._validate_transfer()
    
    def _validate_student_prerequisites(self):
        """Validation: Student must be active, not graduated, have class assignment"""
        if not self.student.is_active:
            raise ValidationError(f"Cannot move inactive student {self.student.full_name}. Student must be active.")
        
        if not self.student.current_class:
            raise ValidationError(f"Cannot move student {self.student.full_name}. Student must be assigned to a class.")
        
        # Check if student is already graduated
        if hasattr(self.student, 'status') and self.student.status == 'GRADUATED':
            raise ValidationError(f"Cannot move graduated student {self.student.full_name}. Graduated students cannot be moved.")
    
    def _validate_promotion(self):
        """Validation: New grade must be higher than current grade"""
        if not self.from_class or not self.to_class:
            raise ValidationError("Both from_class and to_class are required for promotion")
        
        if self.to_class.grade <= self.from_class.grade:
            raise ValidationError(
                f"Invalid promotion: New grade must be higher than current grade. "
                f"Current: Grade {self.from_class.grade}, Target: Grade {self.to_class.grade}"
            )
    
    def _validate_demotion(self):
        """Validation: New grade must be lower than current grade, reason required"""
        if not self.from_class or not self.to_class:
            raise ValidationError("Both from_class and to_class are required for demotion")
        
        if self.to_class.grade >= self.from_class.grade:
            raise ValidationError(
                f"Invalid demotion: New grade must be lower than current grade. "
                f"Current: Grade {self.from_class.grade}, Target: Grade {self.to_class.grade}"
            )
        
        if not self.reason or self.reason.strip() == '':
            raise ValidationError("Reason is required for demotion")
    
    def _validate_transfer(self):
        """Validation: Must be same grade, same academic year, different class"""
        if not self.from_class or not self.to_class:
            raise ValidationError("Both from_class and to_class are required for transfer")
        
        # Must be same grade
        if self.to_class.grade != self.from_class.grade:
            raise ValidationError(
                f"Invalid transfer: Must be within the same grade. "
                f"Current: Grade {self.from_class.grade}, Target: Grade {self.to_class.grade}"
            )
        
        # Must be same academic year
        if self.to_class.academic_year != self.from_class.academic_year:
            raise ValidationError(
                f"Invalid transfer: Must be within the same academic year. "
                f"Current: {self.from_class.academic_year}, Target: {self.to_class.academic_year}"
            )
        
        # Must be different class
        if self.to_class.id == self.from_class.id:
            raise ValidationError("Cannot transfer to the same class student is already in")
        
    def save(self, *args, **kwargs):
        # Validate before saving
        self.full_clean()
        # Capture arrears before movement
        if not self.pk:  # Only on creation
            self.previous_arrears = self.student.previous_term_arrears + self.student.current_term_balance
            self.preserved_arrears = self.previous_arrears
        super().save(*args, **kwargs)

class BulkMovement(models.Model):
    MOVEMENT_TYPES = [
        ('PROMOTION', 'End of Year Promotion'),
        ('CLASS_TRANSFER', 'Class Transfer')
    ]

    movement_type = models.CharField(max_length=15, choices=MOVEMENT_TYPES)
    from_academic_year = models.IntegerField()
    to_academic_year = models.IntegerField()
    execution_date = models.DateTimeField(default=timezone.now)
    executed_by = models.ForeignKey(Administrator, on_delete=models.SET_NULL, null=True)
    total_students = models.IntegerField(default=0)
    successful_moves = models.IntegerField(default=0)
    failed_moves = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-execution_date']
        indexes = [
            models.Index(fields=['execution_date']),
            models.Index(fields=['movement_type']),
        ]

    def __str__(self):
        return f"{self.movement_type} - {self.execution_date.date()}"

    @property
    def success_rate(self):
        if self.total_students == 0:
            return 0
        return (self.successful_moves / self.total_students) * 100