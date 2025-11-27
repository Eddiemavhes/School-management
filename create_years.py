import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicYear

print("Creating Academic Years...")

# Create 2025 Academic Year (currently active)
year_2025, created = AcademicYear.objects.get_or_create(
    year=2025,
    defaults={
        'start_date': date(2025, 1, 1),
        'end_date': date(2025, 12, 31),
        'is_active': True
    }
)
if created:
    print(f"✓ Created Academic Year 2025 (Active: {year_2025.is_active})")
else:
    print(f"✓ Academic Year 2025 already exists (Active: {year_2025.is_active})")

# Create 2026 Academic Year (for rollover)
year_2026, created = AcademicYear.objects.get_or_create(
    year=2026,
    defaults={
        'start_date': date(2026, 1, 1),
        'end_date': date(2026, 12, 31),
        'is_active': False
    }
)
if created:
    print(f"✓ Created Academic Year 2026 (Active: {year_2026.is_active})")
else:
    print(f"✓ Academic Year 2026 already exists (Active: {year_2026.is_active})")

# List all years
print("\nAcademic Years in Database:")
for year in AcademicYear.objects.all():
    print(f"  - {year.year}: Active={year.is_active}")
