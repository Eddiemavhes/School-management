import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Class, AcademicYear

print("Setting up classes for 2026...\n")

year_2026 = AcademicYear.objects.filter(year=2026).first()
if not year_2026:
    print("ERROR: Academic Year 2026 not found!")
    exit(1)

# Define the grades and sections that exist in 2025
# Based on what we saw: Grade 1A, 1B, 2A, 2B, 3A, 5A, 6A, 6B, 7B

grades_and_sections = [
    (1, 'A'),
    (1, 'B'),
    (2, 'A'),
    (2, 'B'),
    (3, 'A'),
    (5, 'A'),
    (6, 'A'),
    (6, 'B'),
    (7, 'B'),
]

print("Creating classes for Academic Year 2026:")
print("=" * 50)

created_count = 0
for grade, section in grades_and_sections:
    cls, created = Class.objects.get_or_create(
        grade=grade,
        section=section,
        academic_year=2026
    )
    
    if created:
        print(f"✓ Created: Grade {grade}{section}")
        created_count += 1
    else:
        print(f"  Already exists: Grade {grade}{section}")

print("\n" + "=" * 50)
print(f"Total classes created: {created_count}")

# List all classes in 2026
print("\nAll classes in 2026:")
classes_2026 = Class.objects.filter(academic_year=2026).order_by('grade', 'section')
for cls in classes_2026:
    print(f"  - {cls}")
