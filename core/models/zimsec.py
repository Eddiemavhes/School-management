"""
ZIMSEC Grade 7 Examination Management Models
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

class ZimsecResults(models.Model):
    """Store ZIMSEC examination results for Grade 7 students"""
    
    SUBJECT_CHOICES = [
        ('ENGLISH', 'English Language'),
        ('MATHEMATICS', 'Mathematics'),
        ('SCIENCE', 'General Science'),
        ('SOCIAL_STUDIES', 'Social Studies'),
        ('LANGUAGE', 'Indigenous Language'),
        ('AGRICULTURE', 'Agriculture'),
    ]
    
    STATUS_CHOICES = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
    ]
    
    student = models.OneToOneField(
        'Student',
        on_delete=models.PROTECT,
        related_name='zimsec_results'
    )
    academic_year = models.IntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2099)]
    )
    
    # Unit Scores for each subject (1-9, where 1-5 = Pass, 6-9 = Fail)
    english_units = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        null=True,
        blank=True,
        help_text="1-5=Pass, 6-9=Fail"
    )
    mathematics_units = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        null=True,
        blank=True,
        help_text="1-5=Pass, 6-9=Fail"
    )
    science_units = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        null=True,
        blank=True,
        help_text="1-5=Pass, 6-9=Fail"
    )
    social_studies_units = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        null=True,
        blank=True,
        help_text="1-5=Pass, 6-9=Fail"
    )
    indigenous_language_units = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        null=True,
        blank=True,
        help_text="1-5=Pass, 6-9=Fail"
    )
    agriculture_units = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        null=True,
        blank=True,
        help_text="1-5=Pass, 6-9=Fail"
    )
    
    # Calculated fields
    total_aggregate = models.IntegerField(null=True, blank=True)
    overall_status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    
    # Additional exam information
    exam_center = models.CharField(max_length=100, null=True, blank=True)
    candidate_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    result_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'academic_year']
        ordering = ['-academic_year', 'student__surname']
        verbose_name = 'ZIMSEC Result'
        verbose_name_plural = 'ZIMSEC Results'
    
    def __str__(self):
        return f"{self.student} - {self.academic_year} (Aggregate: {self.total_aggregate})"
    
    def save(self, *args, **kwargs):
        # Calculate aggregate
        units = []
        for field in ['english_units', 'mathematics_units', 'science_units', 
                      'social_studies_units', 'indigenous_language_units', 'agriculture_units']:
            value = getattr(self, field, None)
            if value is not None:
                units.append(value)
        
        if len(units) == 6:  # All subjects entered
            self.total_aggregate = sum(units)
            # Check if all subjects are passes (1-5 units)
            self.overall_status = 'PASS' if all(u <= 5 for u in units) else 'FAIL'
        else:
            self.total_aggregate = None
            self.overall_status = None
        
        super().save(*args, **kwargs)
    
    @property
    def english_status(self):
        return 'PASS' if self.english_units and self.english_units <= 5 else 'FAIL'
    
    @property
    def mathematics_status(self):
        return 'PASS' if self.mathematics_units and self.mathematics_units <= 5 else 'FAIL'
    
    @property
    def science_status(self):
        return 'PASS' if self.science_units and self.science_units <= 5 else 'FAIL'
    
    @property
    def social_studies_status(self):
        return 'PASS' if self.social_studies_units and self.social_studies_units <= 5 else 'FAIL'
    
    @property
    def language_status(self):
        return 'PASS' if self.indigenous_language_units and self.indigenous_language_units <= 5 else 'FAIL'
    
    @property
    def agriculture_status(self):
        return 'PASS' if self.agriculture_units and self.agriculture_units <= 5 else 'FAIL'
    
    @property
    def unit_percentage(self):
        """Get percentage equivalent of aggregate (rough estimate)"""
        if not self.total_aggregate:
            return None
        
        # Mapping: 6 units = 95%, 12 units = 80%, 18 units = 65%, 30 units = 40%
        if self.total_aggregate <= 6:
            return 95 - (self.total_aggregate - 6) * 1.67
        elif self.total_aggregate <= 12:
            return 80 - (self.total_aggregate - 12) * 2.5
        elif self.total_aggregate <= 18:
            return 65 - (self.total_aggregate - 18) * 2.5
        else:
            return max(40, 65 - (self.total_aggregate - 18) * 1.67)


class Grade7Statistics(models.Model):
    """Store aggregated statistics for Grade 7 ZIMSEC results"""
    
    academic_year = models.IntegerField(
        primary_key=True,
        validators=[MinValueValidator(2020), MaxValueValidator(2099)]
    )
    
    # Student counts
    total_students = models.IntegerField(default=0)
    students_sat_exams = models.IntegerField(default=0)
    
    # Statistics
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_aggregate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    top_aggregate = models.IntegerField(null=True, blank=True)
    bottom_aggregate = models.IntegerField(null=True, blank=True)
    
    # Subject averages
    english_average = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    mathematics_average = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    science_average = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    social_studies_average = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    language_average = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    agriculture_average = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-academic_year']
        verbose_name = 'Grade 7 Statistics'
        verbose_name_plural = 'Grade 7 Statistics'
    
    def __str__(self):
        return f"Grade 7 Statistics - {self.academic_year}"
    
    @classmethod
    def calculate_for_year(cls, academic_year):
        """Calculate and update statistics for a given academic year"""
        from .student import Student
        
        # Get all Grade 7 students who took exams that year
        results = ZimsecResults.objects.filter(academic_year=academic_year)
        
        if not results.exists():
            return None
        
        # Count students
        total_students = Student.objects.filter(
            current_class__grade=7,
            date_enrolled__year__lte=academic_year
        ).count()
        
        students_sat = results.count()
        passes = results.filter(overall_status='PASS').count()
        pass_rate = (passes / students_sat * 100) if students_sat > 0 else 0
        
        # Calculate averages
        avg_aggregate = results.aggregate(
            avg=models.Avg('total_aggregate')
        )['avg'] or 0
        
        top = results.aggregate(
            top=models.Min('total_aggregate')  # Lower is better
        )['top']
        
        bottom = results.aggregate(
            bottom=models.Max('total_aggregate')
        )['bottom']
        
        # Subject averages
        def get_subject_average(field_name):
            values = results.filter(**{f"{field_name}__isnull": False}).values_list(field_name, flat=True)
            return sum(values) / len(values) if values else 0
        
        # Create or update statistics
        stats, created = cls.objects.get_or_create(academic_year=academic_year)
        stats.total_students = total_students
        stats.students_sat_exams = students_sat
        stats.pass_rate = Decimal(str(round(pass_rate, 2)))
        stats.average_aggregate = Decimal(str(round(avg_aggregate, 2)))
        stats.top_aggregate = top
        stats.bottom_aggregate = bottom
        
        stats.english_average = Decimal(str(round(get_subject_average('english_units'), 2)))
        stats.mathematics_average = Decimal(str(round(get_subject_average('mathematics_units'), 2)))
        stats.science_average = Decimal(str(round(get_subject_average('science_units'), 2)))
        stats.social_studies_average = Decimal(str(round(get_subject_average('social_studies_units'), 2)))
        stats.language_average = Decimal(str(round(get_subject_average('indigenous_language_units'), 2)))
        stats.agriculture_average = Decimal(str(round(get_subject_average('agriculture_units'), 2)))
        
        stats.save()
        return stats
