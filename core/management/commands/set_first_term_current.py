from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime

from core.models.academic import AcademicTerm


class Command(BaseCommand):
    help = (
        "Create or mark First Term as current for a given academic year (for testing)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--year', type=int, help='Academic year to set (defaults to current or calendar year)'
        )

    def handle(self, *args, **options):
        year = options.get('year')
        current = AcademicTerm.get_current_term()
        if not year:
            year = current.academic_year if current else timezone.now().year

        # Use safe default start/end dates for term 1
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 4, 30)

        term1, created = AcademicTerm.objects.get_or_create(
            academic_year=year,
            term=1,
            defaults={
                'start_date': start_date,
                'end_date': end_date,
                'is_current': True,
            },
        )

        updated = False
        # Ensure dates and is_current are set
        if term1.start_date != start_date:
            term1.start_date = start_date
            updated = True
        if term1.end_date != end_date:
            term1.end_date = end_date
            updated = True
        if not term1.is_current:
            term1.is_current = True
            updated = True

        if updated:
            term1.save()

        # Unset any other term marked as current
        AcademicTerm.objects.filter(is_current=True).exclude(id=term1.id).update(is_current=False)

        self.stdout.write(self.style.SUCCESS(f"Set current term: {term1} (created={created})"))