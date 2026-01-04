from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from core.models import (
    ArrearsImportBatch,
    ArrearsImportEntry,
    StudentArrearsRecord,
    StudentBalance,
    Student,
    AcademicTerm,
    Payment
)
from django.db.models import Sum, Q
import logging

logger = logging.getLogger(__name__)


class ArrearsImportService:
    """Service to handle arrears import operations"""
    
    @staticmethod
    def create_import_batch(academic_year, import_method, user, starting_term=None):
        """Create a new arrears import batch"""
        from ..models.academic import AcademicTerm
        
        # Get the starting term for this academic year
        if not starting_term and academic_year:
            year_value = academic_year.year if hasattr(academic_year, 'year') else academic_year
            starting_term = AcademicTerm.objects.filter(academic_year=year_value, term=1).first()
        
        batch = ArrearsImportBatch.objects.create(
            academic_year=academic_year,
            import_method=import_method,
            created_by=user,
            starting_term=starting_term
        )
        logger.info(f"Created arrears import batch {batch.batch_id} by {getattr(user, 'username', str(user))}")
        return batch
    
    @staticmethod
    def add_arrears_entry(batch, student, amount, description='', date_incurred=None, user=None):
        """Add a student arrears entry to batch"""
        if amount < 0:
            raise ValidationError('Arrears amount cannot be negative')
        
        entry, created = ArrearsImportEntry.objects.update_or_create(
            batch=batch,
            student=student,
            defaults={
                'arrears_amount': amount,
                'arrears_description': description,
                'date_incurred': date_incurred,
                'created_by': user,
            }
        )
        
        logger.info(
            f"{'Created' if created else 'Updated'} arrears entry: "
            f"{student.full_name} - ${amount}"
        )
        
        batch.update_statistics()
        return entry
    
    @staticmethod
    def validate_batch(batch):
        """Validate all entries in batch before import"""
        errors = []
        warnings = []
        
        entries = batch.entries.all()
        
        if not entries.exists():
            errors.append('No students in import batch')
            return errors, warnings
        
        for entry in entries:
            try:
                # Validate student exists and is active
                if entry.student.is_deleted:
                    errors.append(f'{entry.student.full_name}: Student is deleted')
                    continue
                
                # Validate amount
                if entry.arrears_amount < 0:
                    errors.append(f'{entry.student.full_name}: Invalid negative amount')
                
                if entry.arrears_amount > 10000:  # Sanity check
                    warnings.append(f'{entry.student.full_name}: Large amount (${entry.arrears_amount}) - please verify')
                
                # Check if student already has arrears
                if hasattr(entry.student, 'arrears_record'):
                    warnings.append(f'{entry.student.full_name}: Already has arrears record on file')
                    
            except Exception as e:
                errors.append(f'{entry.student.full_name}: {str(e)}')
        
        return errors, warnings
    
    @staticmethod
    def apply_arrears_to_balance(batch):
        """Apply all validated arrears to student balances"""
        if batch.status != 'READY':
            raise ValidationError('Only READY batches can be imported')
        
        imported_count = 0
        failed_entries = []
        
        with transaction.atomic():
            batch.status = 'IMPORTED'
            
            for entry in batch.entries.filter(is_imported=False):
                try:
                    # Use verified amount if verified, otherwise original
                    final_amount = entry.verified_amount if entry.is_verified else entry.arrears_amount
                    
                    if final_amount <= 0:
                        entry.is_imported = True
                        entry.imported_at = timezone.now()
                        entry.save()
                        imported_count += 1
                        continue
                    
                    # Create or update StudentArrearsRecord
                    record, created = StudentArrearsRecord.objects.get_or_create(
                        student=entry.student,
                        defaults={
                            'total_arrears': final_amount,
                            'import_batch': batch,
                            'notes': entry.arrears_description
                        }
                    )
                    
                    if not created:
                        record.total_arrears += final_amount
                        record.save()
                    
                    # Apply to current term balance
                    starting_term = batch.starting_term or batch.academic_year.terms.filter(term=1).first()
                    
                    # Initialize or get StudentBalance for starting term using model helper
                    balance = StudentBalance.initialize_term_balance(entry.student, starting_term)

                    if balance is None:
                        raise ValidationError(f"Cannot create or initialize balance for {entry.student.full_name}")

                    # Add this imported arrears amount to previous_arrears
                    balance.previous_arrears = (balance.previous_arrears or Decimal('0')) + final_amount
                    balance.save(update_fields=['previous_arrears'])
                    
                    # Mark entry as imported
                    entry.is_imported = True
                    entry.imported_at = timezone.now()
                    entry.save()
                    
                    # Update record
                    record.is_applied_to_balance = True
                    record.applied_to_term = starting_term
                    record.applied_at = timezone.now()
                    record.save()
                    
                    imported_count += 1
                    logger.info(f"Applied arrears for {entry.student.full_name}: ${final_amount}")
                    
                except Exception as e:
                    entry.error_message = str(e)
                    entry.save()
                    failed_entries.append((entry.student.full_name, str(e)))
                    logger.error(f"Failed to import arrears for {entry.student.full_name}: {str(e)}")
            
            # Update batch status
            batch.imported_at = timezone.now()
            batch.save()
        
        return {
            'imported_count': imported_count,
            'failed_count': len(failed_entries),
            'failed_entries': failed_entries
        }
    
    @staticmethod
    def generate_import_summary_report(batch):
        """Generate summary statistics for import batch"""
        entries = batch.entries.all()
        
        summary = {
            'batch_id': str(batch.batch_id),
            'academic_year': str(batch.academic_year),
            'import_method': batch.get_import_method_display(),
            'total_students': entries.count(),
            'students_with_arrears': entries.filter(arrears_amount__gt=0).count(),
            'students_zero_arrears': entries.filter(arrears_amount=0).count(),
            'total_arrears': entries.filter(arrears_amount__gt=0).aggregate(
                Sum('arrears_amount')
            )['arrears_amount__sum'] or Decimal('0'),
            'status': batch.get_status_display(),
            'created_by': getattr(batch.created_by, 'full_name', None) or getattr(batch.created_by, 'username', str(batch.created_by)),
            'created_at': batch.created_at,
        }
        
        # Categories breakdown
        entries_with_arrears = entries.filter(arrears_amount__gt=0).order_by('-arrears_amount')
        
        summary['categories'] = {
            'no_arrears': entries.filter(arrears_amount=0).count(),
            'minor_under_100': entries.filter(arrears_amount__gt=0, arrears_amount__lte=100).count(),
            'moderate_100_300': entries.filter(arrears_amount__gt=100, arrears_amount__lte=300).count(),
            'significant_over_300': entries.filter(arrears_amount__gt=300).count(),
        }
        
        # Top arrears
        summary['top_5_arrears'] = [
            {
                'student_name': entry.student.full_name,
                'amount': float(entry.arrears_amount),
                'description': entry.arrears_description or 'N/A'
            }
            for entry in entries_with_arrears[:5]
        ]
        
        return summary
    
    @staticmethod
    def get_student_statement_after_import(student, batch):
        """Generate student fee statement after arrears import"""
        try:
            arrears_record = student.arrears_record
        except StudentArrearsRecord.DoesNotExist:
            arrears_record = None
        
        starting_term = batch.starting_term or batch.academic_year.terms.filter(term=1).first()
        
        try:
            balance = StudentBalance.objects.get(
                student=student,
                term=starting_term
            )
        except StudentBalance.DoesNotExist:
            balance = None
        
        statement = {
            'student_name': student.full_name,
            'student_id': student.id,
            'academic_year': str(batch.academic_year),
            'previous_arrears': float(arrears_record.total_arrears) if arrears_record else 0,
            'current_term': str(starting_term),
            'term_fee': float(balance.term_fee) if balance else 0,
            'opening_balance': float(balance.total_due) if balance else 0,
            'payments_made': float(balance.amount_paid) if balance else 0,
            'current_balance': float(balance.current_balance) if balance else 0,
            'status': 'Arrears Imported' if arrears_record else 'No Arrears'
        }
        
        return statement
    
    @staticmethod
    def cancel_batch(batch, reason=''):
        """Cancel an import batch (only for draft/validating batches)"""
        if not batch.is_editable:
            raise ValidationError('Cannot cancel batch that has already been imported or failed')
        
        batch.status = 'CANCELLED'
        batch.processing_notes = f'Cancelled: {reason}'
        batch.save()
        
        logger.info(f"Cancelled arrears import batch {batch.batch_id}: {reason}")
        return batch
