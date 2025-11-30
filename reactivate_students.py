#!/usr/bin/env python
"""
Re-activate students for payment testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, Class, AcademicYear
from django.utils import timezone

print("=" * 80)
print("🔄 RE-ACTIVATING STUDENTS")
print("=" * 80)

# Check available years
years = AcademicYear.objects.all().order_by('year')
print(f"\nAvailable academic years: {', '.join([str(y.year) for y in years])}")

if not years.exists():
    print("❌ No academic years created!")
    print("You need to create at least one academic year first")
    exit(1)

# Use the latest year
latest_year = years.last()
print(f"✓ Using year: {latest_year.year}")

# Get or create a class for that year
test_class = Class.objects.filter(academic_year=latest_year.year).first()
if not test_class:
    print(f"⚠️  No class found for {latest_year.year}, creating one...")
    test_class = Class.objects.create(
        grade=1,
        section='A',
        academic_year=latest_year.year
    )
    print(f"✓ Created: {test_class}")
else:
    print(f"✓ Using class: {test_class}")

# Reactivate students
students = Student.all_students.filter(is_deleted=False)
print(f"\nRe-activating {students.count()} students...")

for student in students:
    student.is_active = True
    student.status = 'ENROLLED'
    student.current_class = test_class
    student.date_enrolled = timezone.now().date()
    student.save()
    print(f"✓ {student.full_name}: is_active=True")

print("\n" + "=" * 80)
print("✅ VERIFICATION")
print("=" * 80)

active = Student.objects.filter(is_active=True).count()
print(f"\nActive students: {active}")

if active > 0:
    print(f"✅ Students are ready for payment recording!")
    print(f"\nYou can now:")
    print(f"1. Go to Payments → Record Payment")
    print(f"2. Select a student from the dropdown")
    print(f"3. Enter payment amount")
    print(f"4. Click Submit")
    print(f"\nPayments should now be recorded successfully!")
else:
    print("❌ Still no active students")

print("=" * 80)
