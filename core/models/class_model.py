from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

class Class(models.Model):
    # Grade choices: ECD (Early Childhood Development) + Grades 1-7
    GRADE_CHOICES = [
        ('ECD', 'ECD (Early Childhood Development)'),
    ] + [(i, f'Grade {i}') for i in range(1, 8)]
    SECTION_CHOICES = [('A', 'A'), ('B', 'B')]
    
    grade = models.CharField(max_length=4, choices=GRADE_CHOICES)
    section = models.CharField(max_length=1, choices=SECTION_CHOICES)
    academic_year = models.IntegerField(
        validators=[MinValueValidator(2020)],
        help_text="Academic year (e.g., 2025)"
    )
    teacher = models.ForeignKey(
        'Administrator',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_class'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Classes"
        unique_together = ['grade', 'section', 'academic_year']
        ordering = ['grade', 'section']

    def __str__(self):
        return f"{self.get_grade_display()}{self.section}"

    def clean(self):
        """Validate class data"""
        # Validation 1: Teacher can only teach one class per year
        if self.teacher:
            existing_class = Class.objects.filter(
                teacher=self.teacher,
                academic_year=self.academic_year
            ).exclude(pk=self.pk).first()
            
            if existing_class:
                raise ValidationError(
                    f"Teacher {self.teacher.full_name} is already assigned to "
                    f"{existing_class.get_grade_display()}{existing_class.section} in {self.academic_year}. "
                    f"A teacher can only teach one class per academic year."
                )
        
        # Validation 2: Academic year must exist
        self._validate_academic_year_exists()

    def _validate_academic_year_exists(self):
        """Validation 2: Academic year must exist in AcademicYear table"""
        from .academic_year import AcademicYear
        
        try:
            AcademicYear.objects.get(year=self.academic_year)
        except AcademicYear.DoesNotExist:
            raise ValidationError(
                f"Academic year {self.academic_year} does not exist. "
                f"Please create the academic year before assigning classes to it."
            )

    @property
    def student_count(self):
        return self.students.count()

    @property
    def teacher_initials(self):
        if not self.teacher:
            return "NT"  # No Teacher
        names = self.teacher.full_name.split()
        return "".join(name[0].upper() for name in names if name)

    @property
    def male_students_count(self):
        """Count of male students in the class"""
        return self.students.filter(sex='M').count()
    
    @property
    def female_students_count(self):
        """Count of female students in the class"""
        return self.students.filter(sex='F').count()
    
    @property
    def average_age(self):
        """Calculate average age of students in the class"""
        from django.utils import timezone
        from datetime import date
        import statistics
        
        students = self.students.all()
        if not students:
            return 0
        
        today = date.today()
        ages = []
        for student in students:
            if student.date_of_birth:
                age = today.year - student.date_of_birth.year - (
                    (today.month, today.day) < (student.date_of_birth.month, student.date_of_birth.day)
                )
                ages.append(age)
        
        return statistics.mean(ages) if ages else 0

    def can_be_deleted(self):
        return self.student_count == 0
    
    def save(self, *args, **kwargs):
        """Call clean() before saving to validate teacher assignment"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_available_teachers(cls, academic_year, exclude_class_id=None):
        """Get teachers not already assigned in this academic year"""
        from .administrator import Administrator
        from django.db.models import Q
        
        # Get all teachers
        all_teachers = Administrator.objects.filter(is_teacher=True, is_active=True)
        
        # Get teachers already assigned to a class this year
        assigned_teachers = cls.objects.filter(
            academic_year=academic_year,
            teacher__isnull=False
        )
        
        # If we're editing a class, exclude its current teacher from the "assigned" list
        if exclude_class_id:
            assigned_teachers = assigned_teachers.exclude(pk=exclude_class_id)
        
        assigned_teacher_ids = assigned_teachers.values_list('teacher_id', flat=True)
        
        # Return available teachers (those not yet assigned)
        return all_teachers.exclude(id__in=assigned_teacher_ids)