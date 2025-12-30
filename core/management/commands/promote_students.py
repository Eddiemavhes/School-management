"""
Management command to promote students to the next class.

Usage:
    python manage.py promote_students [options]

Options:
    --from-grade: Only promote students from specific grade (e.g., "7" or "ECDB")
    --to-year: Target academic year for promotion
    --dry-run: Preview promotions without saving
    --confirm: Auto-confirm without asking
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import Student, Class, AcademicYear


class Command(BaseCommand):
    help = 'Promote students to the next class for the following academic year'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-grade',
            type=str,
            help='Only promote students from this grade (e.g., "7", "ECDB")',
        )
        parser.add_argument(
            '--to-year',
            type=int,
            help='Target academic year for promotion',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview promotions without saving',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Auto-confirm without prompting',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        confirm = options.get('confirm')
        from_grade = options.get('from_grade')
        to_year = options.get('to_year')

        # Get active students
        students = Student.objects.filter(is_active=True, is_deleted=False)

        # Filter by grade if specified
        if from_grade:
            students = students.filter(current_class__grade=from_grade)

        # Determine target year
        if not to_year:
            try:
                current_year = AcademicYear.objects.filter(is_active=True).first()
                if current_year:
                    to_year = current_year.year + 1
                else:
                    raise CommandError("No active academic year found. Specify --to-year")
            except:
                raise CommandError("Cannot determine target year. Specify --to-year")

        # Check target year exists
        try:
            AcademicYear.objects.get(year=to_year)
        except AcademicYear.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f'Academic year {to_year} does not exist. Creating it now...'
                )
            )
            AcademicYear.objects.create(year=to_year, is_active=False)

        # Prepare promotions
        promotions = []
        skipped = []

        for student in students:
            next_class = student.get_next_class()

            if not next_class:
                skipped.append((student, "No next class available (likely Grade 7)"))
                continue

            promotions.append({
                'student': student,
                'from_class': student.current_class,
                'to_class': next_class,
            })

        # Display summary
        self.stdout.write(self.style.SUCCESS(f'\n📊 PROMOTION SUMMARY\n'))
        self.stdout.write(f'Target Academic Year: {to_year}')
        self.stdout.write(f'Students to promote: {len(promotions)}')
        self.stdout.write(f'Students skipped: {len(skipped)}\n')

        if promotions:
            self.stdout.write(self.style.SUCCESS('✅ Promotions:'))
            for promo in promotions:
                student = promo['student']
                from_cls = promo['from_class']
                to_cls = promo['to_class']
                self.stdout.write(
                    f'  {student.full_name}: {from_cls} → {to_cls}'
                )

        if skipped:
            self.stdout.write(self.style.WARNING('\n⚠️  Skipped:'))
            for student, reason in skipped:
                self.stdout.write(f'  {student.full_name}: {reason}')

        # Confirm and execute
        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN - No changes made'))
            return

        if not confirm:
            response = input('\n⚡ Proceed with promotions? (yes/no): ')
            if response.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.WARNING('Promotion cancelled'))
                return

        # Execute promotions
        with transaction.atomic():
            promoted_count = 0
            failed_count = 0

            for promo in promotions:
                student = promo['student']
                try:
                    student.current_class = promo['to_class']
                    student.save()
                    promoted_count += 1
                except Exception as e:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ❌ {student.full_name}: {str(e)}'
                        )
                    )

        self.stdout.write(self.style.SUCCESS(f'\n✅ Promotion complete!'))
        self.stdout.write(f'  Successfully promoted: {promoted_count}')
        if failed_count:
            self.stdout.write(
                self.style.ERROR(f'  Failed: {failed_count}')
            )
