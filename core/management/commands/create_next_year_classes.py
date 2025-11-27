from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Class

class Command(BaseCommand):
    help = 'Creates classes for the next academic year based on current year classes'

    def handle(self, *args, **options):
        current_year = timezone.now().year
        next_year = current_year + 1

        # Check if next year classes already exist
        if Class.objects.filter(academic_year=next_year).exists():
            self.stdout.write(self.style.WARNING(f'Classes for {next_year} already exist'))
            return

        created_count = 0
        current_classes = Class.objects.filter(academic_year=current_year)

        for current_class in current_classes:
            # Don't create next class for Grade 7 (final grade)
            if current_class.grade < 7:
                # Create next year's class with same grade and section
                Class.objects.create(
                    grade=current_class.grade,
                    section=current_class.section,
                    academic_year=next_year
                )
                created_count += 1

                # Also create the next grade level class
                Class.objects.get_or_create(
                    grade=current_class.grade + 1,
                    section=current_class.section,
                    academic_year=next_year
                )

        # Always create Grade 1 classes for both sections
        for section in ['A', 'B']:
            Class.objects.get_or_create(
                grade=1,
                section=section,
                academic_year=next_year
            )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} classes for {next_year}')
        )