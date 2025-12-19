"""
Management command to fill ZIMSEC results with sample data
Usage: python manage.py fill_zimsec_results [--year YEAR] [--force]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import random
from core.models import Student, AcademicTerm
from core.models.zimsec import ZimsecResults, Grade7Statistics


class Command(BaseCommand):
    help = 'Fill ZIMSEC results with random sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=2026,
            help='Academic year to fill results for (default: 2026)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing results'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        year = options['year']
        force = options['force']

        # Get all Grade 7 students - be flexible with status
        grade7_students = Student.objects.filter(
            current_class__grade=7,
            is_deleted=False
        ).distinct()

        # If no students, try getting any Grade 7 students regardless of deletion status
        if not grade7_students.exists():
            grade7_students = Student.objects.filter(
                current_class__grade=7
            ).distinct()

        if not grade7_students.exists():
            raise CommandError(f'No Grade 7 students found')

        self.stdout.write(f'Found {grade7_students.count()} Grade 7 students')

        count = 0
        updated = 0
        skipped = 0

        for student in grade7_students:
            # Check if result already exists
            exists = ZimsecResults.objects.filter(
                student=student,
                academic_year=year
            ).exists()

            if exists and not force:
                skipped += 1
                continue

            # Generate random units (1-9 scale)
            # Distribution: More 1s-3s (better grades), fewer 6-9s (lower grades)
            units = [
                random.choices([1, 2, 3, 4, 5, 6, 7, 8, 9], weights=[20, 20, 15, 15, 10, 10, 5, 3, 2])[0]
                for _ in range(6)
            ]

            result, created = ZimsecResults.objects.update_or_create(
                student=student,
                academic_year=year,
                defaults={
                    'english_units': units[0],
                    'mathematics_units': units[1],
                    'science_units': units[2],
                    'social_studies_units': units[3],
                    'indigenous_language_units': units[4],
                    'agriculture_units': units[5],
                }
            )
            
            if created:
                count += 1
            else:
                updated += 1

        # Recalculate statistics
        Grade7Statistics.calculate_for_year(year)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully filled ZIMSEC results: {count} created, {updated} updated, {skipped} skipped'
            )
        )
