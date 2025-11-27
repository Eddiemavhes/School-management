from django.db import models
from django.utils import timezone

class TeacherAssignmentHistory(models.Model):
    teacher = models.ForeignKey(
        'Administrator',
        on_delete=models.CASCADE,
        related_name='assignment_history'
    )
    class_assigned = models.ForeignKey(
        'Class',
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    academic_year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Teacher Assignment History'
        verbose_name_plural = 'Teacher Assignment Histories'

    def __str__(self):
        return f"{self.teacher.full_name} - {self.class_assigned.name} ({self.academic_year})"

    def end_assignment(self):
        if self.is_active:
            self.is_active = False
            self.end_date = timezone.now().date()
            self.save()