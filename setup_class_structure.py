import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Class, AcademicYear

print("Setting up class structure for both 2025 and 2026...\n")

# Get or create both years
year_2025, _ = AcademicYear.objects.get_or_create(
    year=2025,
    defaults={'start_date': '2025-01-01', 'end_date': '2025-12-31', 'is_active': True}
)
year_2026, _ = AcademicYear.objects.get_or_create(
    year=2026,
    defaults={'start_date': '2026-01-01', 'end_date': '2026-12-31', 'is_active': False}
)

# Same structure for both years: Grade 1-7, Sections A and B
grades_and_sections = [
    (1, 'A'),
    (1, 'B'),
    (2, 'A'),
    (2, 'B'),
    (3, 'A'),
    (3, 'B'),
    (4, 'A'),
    (4, 'B'),
    (5, 'A'),
    (5, 'B'),
    (6, 'A'),
    (6, 'B'),
    (7, 'A'),
    (7, 'B'),
]

print("Creating class structure for 2025:")
print("=" * 50)
for grade, section in grades_and_sections:
    cls, created = Class.objects.get_or_create(
        grade=grade,
        section=section,
        academic_year=2025
    )
    if created:
        print(f"✓ Created: Grade {grade}{section} (2025)")

print("\nCreating class structure for 2026:")
print("=" * 50)
for grade, section in grades_and_sections:
    cls, created = Class.objects.get_or_create(
        grade=grade,
        section=section,
        academic_year=2026
    )
    if created:
        print(f"✓ Created: Grade {grade}{section} (2026)")

print("\n" + "=" * 60)
print("Class structure setup complete!")
print("\nNow students will move through:\n")
print("2025 structure → 2026 structure")
print("Grade 1A (2025) students → Grade 2A (2026)")
print("Grade 2A (2025) students → Grade 3A (2026)")
print("... and so on ...")
print("Grade 7A (2025) students → Graduated (no Grade 8)")
print("Grade 1A (2026) → Empty (for new students)")
