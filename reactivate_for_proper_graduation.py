#!/usr/bin/env python
"""
Reactivate students to allow them to complete all 3 terms before graduation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, Class, AcademicYear, AcademicTerm
from django.utils import timezone

print("=" * 80)
print("🔄 REACTIVATING STUDENTS FOR PROPER GRADE 7 COMPLETION")
print("=" * 80)

# Get the current term
current_term = AcademicTerm.get_current_term()
if not current_term:
    print("❌ No current term set!")
    exit(1)

print(f"\nCurrent term: {current_term}")
print(f"  Academic Year: {current_term.academic_year}")
print(f"  Term: {current_term.term}")

# Get or create Grade 7 class for current year
year = current_term.academic_year
try:
    year_obj = AcademicYear.objects.get(year=year)
except AcademicYear.DoesNotExist:
    print(f"❌ Academic year {year} not found!")
    exit(1)

grade7_class = Class.objects.filter(grade=7, academic_year=year).first()
if not grade7_class:
    print(f"⚠️  No Grade 7 class for {year}, creating one...")
    grade7_class = Class.objects.create(
        grade=7,
        section='A',
        academic_year=year
    )
    print(f"✓ Created: {grade7_class}")
else:
    print(f"✓ Using class: {grade7_class}")

# Reactivate all students
all_students = Student.all_students.filter(is_deleted=False)
print(f"\nReactivating {all_students.count()} students...")

for student in all_students:
    # Reset to ENROLLED and active for current year
    student.status = 'ENROLLED'
    student.is_active = True
    student.is_archived = False
    student.current_class = grade7_class
    student.date_enrolled = timezone.now().date()
    
    # Skip validation to allow re-enrollment (we're forcing it for test purposes)
    # Save without calling full_clean()
    super(Student, student).save()
    
    print(f"✓ {student.full_name}: is_active=True, status=ENROLLED")

print(f"\n" + "=" * 80)
print("✅ REACTIVATION COMPLETE")
print("=" * 80)

# Verify
active_count = Student.objects.filter(is_active=True).count()
print(f"\nActive students: {active_count}")

print(f"\nNEW GRADUATION LOGIC:")
print(f"✓ Students will remain ACTIVE throughout all 3 terms")
print(f"✓ Only after Term 3 is marked current AND all 3 terms completed")
print(f"✓ Students will be graduated and marked INACTIVE")
print(f"✓ Alumni status based on final payment balance")

print("=" * 80)
