"""
Management command to populate ArrearsVault from existing GRADUATED_WITH_ARREARS students
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from core.models import Student, StudentBalance, ArrearsVault


class Command(BaseCommand):
    help = 'Populate ArrearsVault from existing GRADUATED students with outstanding balances'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be transferred without actually transferring',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Find all GRADUATED students
        graduated_students = Student.objects.filter(
            status='GRADUATED',
            is_active=False,
            is_archived=False  # These are the ones with arrears
        ).order_by('first_name')
        
        self.stdout.write(
            self.style.SUCCESS(f'\nFound {graduated_students.count()} GRADUATED students with arrears')
        )
        
        transferred_count = 0
        skipped_count = 0
        already_exists_count = 0
        
        for student in graduated_students:
            # Get final balance from previous academic year
            # Assuming students graduated from Grade 7 in 2026, now in 2027
            final_balance = StudentBalance.objects.filter(
                student=student,
                term__academic_year=2026
            ).order_by('-term__term').first()
            
            if not final_balance or final_balance.current_balance <= 0:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⊘ {student.full_name}: No outstanding balance - skipped'
                        )
                    )
                skipped_count += 1
                continue
            
            # Check if already in vault
            existing = ArrearsVault.objects.filter(student_id=student.id).first()
            if existing:
                if dry_run:
                    self.stdout.write(
                        f'  ✓ {student.full_name}: Already in vault (${existing.fixed_balance})'
                    )
                already_exists_count += 1
                continue
            
            # Create vault record
            if not dry_run:
                ArrearsVault.objects.create(
                    student_id=student.id,
                    student_full_name=student.full_name,
                    student_birth_entry=student.birth_entry_number,
                    graduation_year=2026,
                    graduation_grade='7',
                    final_aggregate=f'Grade 7, Status: {student.status}',
                    fixed_balance=final_balance.current_balance,
                    required_payment=final_balance.current_balance,
                    parent_name=getattr(student, 'parent_name', 'Parent/Guardian'),
                    parent_phone=getattr(student, 'parent_phone', 'Unknown'),
                    parent_email=getattr(student, 'parent_email', 'unknown@example.com'),
                )
                transferred_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ {student.full_name}: Transferred to vault (${final_balance.current_balance})'
                    )
                )
            else:
                transferred_count += 1
                self.stdout.write(
                    f'  ✓ {student.full_name}: Would transfer to vault (${final_balance.current_balance})'
                )
        
        # Summary
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('TRANSFER SUMMARY'))
        self.stdout.write('='*80)
        self.stdout.write(f'Transferred: {transferred_count}')
        self.stdout.write(f'Already in vault: {already_exists_count}')
        self.stdout.write(f'No outstanding balance: {skipped_count}')
        self.stdout.write(f'TOTAL: {graduated_students.count()}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n(DRY RUN - No actual changes made)')
            )
        else:
            # Show vault status
            in_vault = ArrearsVault.objects.filter(status='GRADUATED_WITH_ARREARS').count()
            total_arrears = ArrearsVault.objects.filter(
                status='GRADUATED_WITH_ARREARS'
            ).aggregate(models.Sum('fixed_balance'))['fixed_balance__sum'] or Decimal('0')
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ ArrearsVault now contains {in_vault} students')
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Total outstanding arrears: ${total_arrears}')
            )
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  REMINDER: System requires 100% payment for alumni transition'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  No partial payments, waivers, or payment plans accepted'
                )
            )
