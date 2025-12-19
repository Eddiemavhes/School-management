from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import ArrearsImportBatch, AcademicYear, AcademicTerm
from core.services.arrears_import_service import ArrearsImportService
from decimal import Decimal


class Command(BaseCommand):
    help = 'Manage arrears import batches - create, validate, and process'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['list', 'validate', 'process'],
            default='list',
            help='Action to perform'
        )
        
        parser.add_argument(
            '--batch-id',
            type=str,
            help='Batch UUID to process'
        )
        
        parser.add_argument(
            '--year',
            type=int,
            help='Academic year for new batch'
        )

    def handle(self, *args, **options):
        action = options.get('action')
        
        if action == 'list':
            self.list_batches()
        elif action == 'validate':
            self.validate_batch(options.get('batch_id'))
        elif action == 'process':
            self.process_batch(options.get('batch_id'))
    
    def list_batches(self):
        """List all arrears import batches"""
        self.stdout.write(self.style.SUCCESS('=== Arrears Import Batches ===\n'))
        
        batches = ArrearsImportBatch.objects.all().order_by('-created_at')
        
        if not batches.exists():
            self.stdout.write(self.style.WARNING('No batches found'))
            return
        
        for batch in batches:
            status_style = {
                'DRAFT': self.style.WARNING,
                'VALIDATING': self.style.HTTP_INFO,
                'READY': self.style.SUCCESS,
                'IMPORTED': self.style.SUCCESS,
                'FAILED': self.style.ERROR,
                'CANCELLED': self.style.HTTP_NOT_MODIFIED,
            }.get(batch.status, lambda x: x)
            
            self.stdout.write(f'\nBatch ID: {batch.batch_id}')
            self.stdout.write(f'  Status: {status_style(batch.get_status_display())}')
            self.stdout.write(f'  Year: {batch.academic_year}')
            self.stdout.write(f'  Method: {batch.get_import_method_display()}')
            self.stdout.write(f'  Students: {batch.total_students_targeted}')
            self.stdout.write(f'  With Arrears: {batch.students_with_arrears}')
            self.stdout.write(f'  Total Amount: ${batch.total_arrears_amount}')
            self.stdout.write(f'  Created: {batch.created_at.strftime("%Y-%m-%d %H:%M")}')
    
    def validate_batch(self, batch_id):
        """Validate a batch before import"""
        if not batch_id:
            self.stdout.write(self.style.ERROR('--batch-id required'))
            return
        
        try:
            batch = ArrearsImportBatch.objects.get(batch_id=batch_id)
        except ArrearsImportBatch.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Batch {batch_id} not found'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Validating batch {batch.batch_id}...\n'))
        
        errors, warnings = ArrearsImportService.validate_batch(batch)
        
        if errors:
            self.stdout.write(self.style.ERROR(f'\n❌ {len(errors)} errors found:'))
            for error in errors:
                self.stdout.write(f'  • {error}')
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ No validation errors'))
        
        if warnings:
            self.stdout.write(self.style.WARNING(f'\n⚠️  {len(warnings)} warnings:'))
            for warning in warnings:
                self.stdout.write(f'  • {warning}')
        
        if not errors:
            batch.status = 'READY'
            batch.save()
            self.stdout.write(self.style.SUCCESS('\n✓ Batch marked as READY for import'))
    
    def process_batch(self, batch_id):
        """Process (import) a ready batch"""
        if not batch_id:
            self.stdout.write(self.style.ERROR('--batch-id required'))
            return
        
        try:
            batch = ArrearsImportBatch.objects.get(batch_id=batch_id)
        except ArrearsImportBatch.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Batch {batch_id} not found'))
            return
        
        if batch.status != 'READY':
            self.stdout.write(self.style.ERROR(f'Batch must be READY (current: {batch.get_status_display()})'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Processing batch {batch.batch_id}...\n'))
        
        result = ArrearsImportService.apply_arrears_to_balance(batch)
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Import complete!'))
        self.stdout.write(f'  Imported: {result["imported_count"]}')
        self.stdout.write(f'  Failed: {result["failed_count"]}')
        
        if result['failed_count'] > 0:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Failed entries:'))
            for student_name, error in result['failed_entries']:
                self.stdout.write(f'  • {student_name}: {error}')
