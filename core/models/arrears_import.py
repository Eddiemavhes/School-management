from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from decimal import Decimal
import uuid


class ArrearsImportBatch(models.Model):
    """Tracks arrears import batches for audit trail"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft - In Progress'),
        ('VALIDATING', 'Validating Data'),
        ('READY', 'Ready for Import'),
        ('IMPORTED', 'Successfully Imported'),
        ('FAILED', 'Import Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    batch_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Import method
    IMPORT_METHOD_CHOICES = [
        ('MANUAL', 'Manual Entry'),
        ('BULK_UPLOAD', 'Bulk Upload (Excel/CSV)'),
        ('COPY_PREVIOUS', 'Copy from Previous System'),
    ]
    import_method = models.CharField(max_length=20, choices=IMPORT_METHOD_CHOICES)
    
    # Academic year context
    academic_year = models.ForeignKey('AcademicYear', on_delete=models.PROTECT)
    starting_term = models.ForeignKey('AcademicTerm', on_delete=models.PROTECT, null=True, blank=True)
    
    # Tracking information
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='arrears_batches_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    imported_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_students_targeted = models.IntegerField(default=0)
    students_with_arrears = models.IntegerField(default=0)
    total_arrears_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Upload file (if applicable)
    upload_file = models.FileField(
        upload_to='arrears_imports/', 
        null=True, 
        blank=True,
        help_text='Excel or CSV file for bulk import'
    )
    
    # Processing notes
    processing_notes = models.TextField(blank=True, help_text='Notes about validation or processing')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Arrears Import Batch'
        verbose_name_plural = 'Arrears Import Batches'
    
    def __str__(self):
        return f"Arrears Import {self.batch_id.hex[:8]} - {self.get_status_display()}"
    
    @property
    def is_editable(self):
        """Can only edit draft batches"""
        return self.status in ['DRAFT', 'VALIDATING']
    
    @property
    def can_import(self):
        """Can only import ready batches"""
        return self.status == 'READY'
    
    def get_progress_percentage(self):
        """Calculate import progress"""
        if self.status == 'IMPORTED':
            return 100
        elif self.status == 'READY':
            return 75
        elif self.status == 'VALIDATING':
            return 50
        else:
            return 25
    
    def update_statistics(self):
        """Recalculate batch statistics from entries"""
        entries = self.entries.filter(is_imported=False)
        self.total_students_targeted = entries.count()
        self.students_with_arrears = entries.filter(arrears_amount__gt=0).count()
        self.total_arrears_amount = entries.filter(arrears_amount__gt=0).aggregate(
            models.Sum('arrears_amount')
        )['arrears_amount__sum'] or Decimal('0')
        self.save(update_fields=['total_students_targeted', 'students_with_arrears', 'total_arrears_amount'])


class ArrearsImportEntry(models.Model):
    """Individual student arrears entry within a batch"""
    
    batch = models.ForeignKey(ArrearsImportBatch, on_delete=models.CASCADE, related_name='entries')
    student = models.ForeignKey('Student', on_delete=models.PROTECT)
    
    # Arrears details
    arrears_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arrears_description = models.CharField(
        max_length=255, 
        blank=True,
        help_text='e.g., "2026 unpaid fees" or "2025-2026 cumulative"'
    )
    date_incurred = models.DateField(
        null=True, 
        blank=True,
        help_text='When the arrears originated'
    )
    
    # Supporting documentation
    supporting_document = models.FileField(
        upload_to='arrears_documents/', 
        null=True, 
        blank=True,
        help_text='PDF or image of supporting document'
    )
    
    # Verification
    verified_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text='Verified amount after confirmation'
    )
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_arrears_entries')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    is_imported = models.BooleanField(default=False)
    imported_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, help_text='Any validation or import errors')
    
    # Audit trail
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='arrears_entries_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['batch', 'student']
        ordering = ['student__surname', 'student__first_name']
    
    def __str__(self):
        return f"{self.student.full_name} - ${self.arrears_amount}"
    
    def clean(self):
        """Validate entry data"""
        if self.arrears_amount < 0:
            raise ValidationError({'arrears_amount': 'Arrears amount cannot be negative'})
        
        if self.is_verified and self.verified_amount != self.arrears_amount:
            raise ValidationError({
                'verified_amount': 'Verified amount must match original arrears amount after confirmation'
            })
    
    def verify(self, user, confirmed_amount):
        """Verify arrears amount (double-entry confirmation)"""
        if confirmed_amount != self.arrears_amount:
            raise ValidationError('Confirmed amount does not match entered amount')
        
        self.is_verified = True
        self.verified_amount = confirmed_amount
        self.verified_by = user
        self.verified_at = timezone.now()
        self.clean()
        self.save()
    
    @property
    def final_amount(self):
        """Return verified amount if verified, otherwise original amount"""
        return self.verified_amount if self.is_verified else self.arrears_amount
    
    @property
    def is_editable(self):
        """Can only edit unverified entries"""
        return not self.is_verified and not self.is_imported


class ArrearsCategory(models.Model):
    """Categorizes types of arrears for reporting"""
    
    CATEGORY_TYPES = [
        ('TUITION', 'Tuition Fees'),
        ('MISC_FEES', 'Miscellaneous Fees'),
        ('UNIFORM', 'Uniform & Books'),
        ('ACTIVITIES', 'School Activities'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    affects_promotion = models.BooleanField(
        default=False,
        help_text='Whether unpaid arrears in this category prevent promotion/graduation'
    )
    
    class Meta:
        verbose_name_plural = 'Arrears Categories'
    
    def __str__(self):
        return self.name


class StudentArrearsRecord(models.Model):
    """Final record of imported arrears for a student"""
    
    student = models.OneToOneField('Student', on_delete=models.CASCADE, related_name='arrears_record')
    
    # Total arrears
    total_arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Breakdown by category
    tuition_arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    misc_fees_arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timeline
    date_imported = models.DateTimeField(auto_now_add=True)
    import_batch = models.ForeignKey(ArrearsImportBatch, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Application
    is_applied_to_balance = models.BooleanField(
        default=False,
        help_text='Whether arrears have been applied to student balance'
    )
    applied_to_term = models.ForeignKey('AcademicTerm', on_delete=models.SET_NULL, null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_paid_off = models.BooleanField(default=False)
    paid_off_date = models.DateField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Student Arrears Record'
        verbose_name_plural = 'Student Arrears Records'
    
    def __str__(self):
        return f"{self.student.full_name} - ${self.total_arrears} arrears"
    
    @property
    def is_cleared(self):
        """Check if all arrears are paid"""
        return self.total_arrears <= 0
    
    def get_payment_status(self):
        """Return readable payment status"""
        if self.is_paid_off:
            return "Cleared"
        elif self.is_applied_to_balance:
            return "Applied to Balance"
        else:
            return "Not Yet Applied"
