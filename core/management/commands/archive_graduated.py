"""
Management command to archive graduated students with paid fees.
This fixes the issue where students who graduated before the fix wasn't applied.
"""

from django.core.management.base import BaseCommand
from core.models.student import Student


class Command(BaseCommand):
    help = 'Archive graduated students who have paid all their fees (is_active=False, balance<=0)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be archived without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        # Find all graduated, inactive students who haven't been archived yet
        graduated_students = Student.objects.filter(
            status='GRADUATED',
            is_active=False,
            is_archived=False
        )
        
        archived_count = 0
        outstanding_students = []
        message_parts = []
        
        for student in graduated_students:
            # Check if they have paid all fees (overall_balance <= 0)
            if student.overall_balance <= 0:
                message_parts.append(
                    f"✓ {student.full_name} - Balance: ${student.overall_balance:.2f}"
                )
                
                if not dry_run:
                    student.is_archived = True
                    student.save()
                
                archived_count += 1
            else:
                outstanding_students.append((student.full_name, student.overall_balance))
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would archive {archived_count} students:')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully archived {archived_count} students:')
            )
        
        for msg in message_parts:
            self.stdout.write(msg)
        
        # Show students who graduated but still have outstanding fees
        if outstanding_students:
            self.stdout.write(
                self.style.WARNING(f'\n⚠ {len(outstanding_students)} graduated students still owe fees:')
            )
            for name, balance in outstanding_students:
                self.stdout.write(
                    self.style.WARNING(f"  • {name} - Owes: ${balance:.2f}")
                )
        
        if archived_count == 0 and not outstanding_students:
            self.stdout.write(self.style.SUCCESS('No graduated students found to process.'))

