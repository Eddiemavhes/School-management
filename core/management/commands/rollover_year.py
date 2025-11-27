from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import AcademicYear
import sys


class Command(BaseCommand):
    help = 'Perform year rollover for the current academic year'

    def handle(self, *args, **options):
        try:
            # Get the current active academic year
            current_year = AcademicYear.objects.filter(is_active=True).first()
            
            if not current_year:
                self.stdout.write(self.style.ERROR('No active academic year found!'))
                sys.exit(1)
            
            self.stdout.write(f'Current Academic Year: {current_year.year}')
            self.stdout.write(f'Starting rollover process...\n')
            
            # Check if next year already exists
            next_year_obj = AcademicYear.objects.filter(year=current_year.year + 1).first()
            if next_year_obj:
                self.stdout.write(self.style.WARNING(f'Academic Year {current_year.year + 1} already exists!'))
                response = input('Do you want to continue with the existing year? (yes/no): ')
                if response.lower() != 'yes':
                    self.stdout.write('Rollover cancelled.')
                    sys.exit(0)
            
            # Perform rollover
            new_year = current_year.rollover_to_new_year()
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully rolled over to Academic Year {new_year.year}'))
            self.stdout.write(f'  - New academic year created')
            self.stdout.write(f'  - Terms created for the new year')
            self.stdout.write(f'  - Students promoted to their new classes')
            self.stdout.write(f'  - Student balances and arrears preserved')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during rollover: {str(e)}'))
            import traceback
            traceback.print_exc()
            sys.exit(1)
