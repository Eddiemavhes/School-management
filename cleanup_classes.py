import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Class, AcademicYear

print("Cleaning up classes from 2026 academic year...\n")

# Get 2026 academic year
year_2026 = AcademicYear.objects.filter(year=2026).first()

if not year_2026:
    print("Academic Year 2026 not found!")
    exit(1)

# Get all classes in 2026
classes_2026 = Class.objects.filter(academic_year=2026)
print(f"Found {classes_2026.count()} classes in 2026:")
for cls in classes_2026:
    print(f"  - {cls}")

# Delete them
if classes_2026.count() > 0:
    count = classes_2026.count()
    classes_2026.delete()
    print(f"\n✓ Deleted {count} classes from 2026")
else:
    print("\nNo classes to delete")

print("\nRemaining classes in 2025:")
classes_2025 = Class.objects.filter(academic_year=2025)
for cls in classes_2025:
    print(f"  - {cls}")
