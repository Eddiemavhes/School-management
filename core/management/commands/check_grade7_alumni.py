from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Student, StudentBalance, AcademicTerm, Class
from core.services.alumni_conversion import AlumniConversionService
from decimal import Decimal


class Command(BaseCommand):
    help = 'Daily batch check for Grade 7 Term 3 students eligible for alumni conversion'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Specific academic year to check',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        year = options.get('year')

        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('GRADE 7 TERM 3 ALUMNI CONVERSION - BATCH CHECK'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

        # Get all active classes in Grade 7
        grade7_classes = Class.objects.filter(grade=7)

        # Get all Grade 7 students NOT already alumni
        grade7_students = Student.objects.filter(
            current_class__grade=7,
            status__in=['ENROLLED', 'ACTIVE']
        ).distinct()

        # Get current/all Term 3s if year specified
        if year:
            term3_list = AcademicTerm.objects.filter(academic_year=year, term=3)
        else:
            term3_list = AcademicTerm.objects.filter(term=3)

        converted_count = 0
        eligible_count = 0

        for term3 in term3_list:
            self.stdout.write(f'\nProcessing Term 3 {term3.academic_year}:')
            self.stdout.write('-' * 80)

            for student in grade7_students:
                # Check if student has balance for this term 3
                try:
                    balance = StudentBalance.objects.get(student=student, term=term3)
                except StudentBalance.DoesNotExist:
                    continue

                # Check if balance is 0 or negative (all fees paid or credit)
                if balance.current_balance <= 0:
                    eligible_count += 1
                    
                    self.stdout.write(
                        f'  ✅ {student.first_name} {student.surname} | '
                        f'Balance: {balance.current_balance} | Eligible: YES'
                    )

                    if not dry_run:
                        if student.status != 'ALUMNI':
                            AlumniConversionService.convert_to_alumni(student)
                            converted_count += 1
                            self.stdout.write(self.style.SUCCESS('     → CONVERTED TO ALUMNI'))
                    else:
                        self.stdout.write('     → [DRY RUN] Would convert to alumni')

        # Summary
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write('='*80)
        self.stdout.write(f'Grade 7 students checked: {grade7_students.count()}')
        self.stdout.write(f'Eligible for alumni: {eligible_count}')
        self.stdout.write(f'Converted to alumni: {converted_count}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY RUN MODE - No changes were made'))

        self.stdout.write(self.style.SUCCESS('\n' + '='*80 + '\n'))
