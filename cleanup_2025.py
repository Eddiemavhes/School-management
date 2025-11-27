import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Class

print("Cleaning up 2025 classes...\n")

# Get all classes in 2025
classes_2025 = Class.objects.filter(academic_year=2025)
print(f"Found {classes_2025.count()} classes in 2025")
print("Deleting all 2025 classes...\n")

for cls in classes_2025:
    print(f"✓ Deleted: {cls}")
    cls.delete()

print("\n" + "=" * 60)

# Show what remains
from core.models import Class
classes_remaining = Class.objects.all()
print(f"\nRemaining classes in database: {classes_remaining.count()}")
print("\n2026 CLASSES (Complete structure):")
classes_2026 = Class.objects.filter(academic_year=2026).order_by('grade', 'section')
for cls in classes_2026:
    students = cls.students.all()
    print(f"  {cls}: {students.count()} students")
