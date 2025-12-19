"""
Student Term History Model

Tracks which students were in which classes during which terms.
Essential for determining ZIMSEC entry eligibility and historical records.
"""

from django.db import models
from core.models.student import Student
from core.models.academic import AcademicTerm
from core.models.class_model import Class


class StudentTermHistory(models.Model):
    """
    Tracks student enrollment and attendance for each term.
    
    This is critical for:
    1. Determining ZIMSEC eligibility (did student reach Term 3?)
    2. Academic history tracking
    3. Attendance records
    4. Preventing duplicate enrollments
    """
    
    ATTENDANCE_CHOICES = [
        ('PRESENT', 'Present - Attended and wrote exams'),
        ('ABSENT', 'Absent - Did not attend'),
        ('DROPPED', 'Dropped - Left during term'),
        ('TRANSFERRED', 'Transferred - Moved to another school'),
    ]
    
    EXAM_ELIGIBILITY_CHOICES = [
        ('ELIGIBLE', 'Eligible - Attended, can sit exams'),
        ('NOT_ELIGIBLE', 'Not Eligible - Missed classes/requirements'),
        ('PENDING', 'Pending - Awaiting determination'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='term_history'
    )
    academic_year = models.IntegerField(
        help_text="e.g., 2027 for academic year 2027"
    )
    academic_term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.PROTECT,
        related_name='student_enrollments'
    )
    class_enrolled = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        related_name='term_enrollments',
        help_text="The class student was in during this term"
    )
    
    # Attendance tracking
    attendance_status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_CHOICES,
        default='PRESENT',
        help_text="Was the student present/absent/dropped during this term?"
    )
    
    # Exam eligibility
    exam_eligibility = models.CharField(
        max_length=20,
        choices=EXAM_ELIGIBILITY_CHOICES,
        default='PENDING',
        help_text="Is the student eligible to sit for exams?"
    )
    
    # ZIMSEC specific (for Grade 7 Term 3)
    zimsec_eligible = models.BooleanField(
        default=False,
        help_text="For Grade 7 Term 3: Did student sit ZIMSEC exams?"
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-academic_year', '-academic_term__term', 'student__surname']
        unique_together = [['student', 'academic_year', 'academic_term']]
        verbose_name = 'Student Term History'
        verbose_name_plural = 'Student Term Histories'
        indexes = [
            models.Index(fields=['academic_year', 'academic_term']),
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['class_enrolled', 'academic_year']),
        ]
    
    def __str__(self):
        return f"{self.student.first_name} - {self.academic_term} {self.academic_year}"
    
    @classmethod
    def get_zimsec_candidates(cls, academic_year, grade7_class=None):
        """
        Get all Grade 7 students who reached Term 3 in the given year.
        
        Args:
            academic_year (int): Academic year (e.g., 2027)
            grade7_class (Class, optional): Filter by specific Grade 7 class
            
        Returns:
            QuerySet: Students eligible for ZIMSEC entry
        """
        # Get Term 3 of the specified year
        term3 = AcademicTerm.objects.filter(
            academic_year=academic_year,
            term=3
        ).first()
        
        if not term3:
            return cls.objects.none()
        
        # Query students who:
        # 1. Have term history for this year's Term 3
        # 2. Were present or at least attended exam
        # 3. Optionally filtered by Grade 7 class
        query = cls.objects.filter(
            academic_year=academic_year,
            academic_term=term3,
            class_enrolled__grade=7,
            attendance_status__in=['PRESENT', 'ABSENT'],  # They took exam or were expected
            student__is_deleted=False
        ).select_related('student', 'class_enrolled')
        
        if grade7_class:
            query = query.filter(class_enrolled=grade7_class)
        
        # Return distinct students (not the history records)
        return query.values_list('student_id', flat=True).distinct()
    
    @classmethod
    def mark_term3_attendance(cls, students, academic_year, class_obj, attendance_status='PRESENT'):
        """
        Bulk create/update term history records for students.
        
        Args:
            students: QuerySet or list of Student objects
            academic_year (int): Academic year
            class_obj (Class): The class they're in
            attendance_status (str): PRESENT, ABSENT, DROPPED, TRANSFERRED
        """
        term3 = AcademicTerm.objects.filter(
            academic_year=academic_year,
            term=3
        ).first()
        
        if not term3:
            return 0
        
        created_count = 0
        for student in students:
            _, created = cls.objects.update_or_create(
                student=student,
                academic_year=academic_year,
                academic_term=term3,
                defaults={
                    'class_enrolled': class_obj,
                    'attendance_status': attendance_status,
                    'exam_eligibility': 'ELIGIBLE' if attendance_status == 'PRESENT' else 'NOT_ELIGIBLE',
                    'zimsec_eligible': attendance_status == 'PRESENT' and class_obj.grade == 7,
                }
            )
            if created:
                created_count += 1
        
        return created_count
