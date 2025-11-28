#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student

student = Student.objects.get(first_name='Edwin', surname='Mavhe')

print("Testing auto-graduation logic...")
print()

print(f"Student: {student.first_name} {student.surname}")
print(f"Current Status: {student.status}")
print(f"Is Active: {student.is_active}")
print(f"Is Archived: {student.is_archived}")
print(f"Current Grade: {student.current_class} (Grade {int(student.current_class.grade)})")
print(f"Overall Balance: ${student.overall_balance}")
print()

print("Checking eligibility...")
print(f"  1. Is active: {student.is_active} (need True)")
print(f"  2. Status is ENROLLED: {student.status == 'ENROLLED'} (need True)")
print(f"  3. Grade >= 7: {int(student.current_class.grade) >= 7} (need True)")
print(f"  4. Balance <= 0: {student.overall_balance <= 0} (need True)")
print()

if student.is_active and student.status == 'ENROLLED' and int(student.current_class.grade) >= 7 and student.overall_balance <= 0:
    print("✓ All conditions met - Attempting auto-graduation...")
    result = student.auto_graduate_if_eligible()
    print(f"Result: {result}")
    print()
    
    # Refresh to see updated values
    student.refresh_from_db()
    print(f"After graduation:")
    print(f"  Status: {student.status}")
    print(f"  Is Active: {student.is_active}")
    print(f"  Is Archived: {student.is_archived}")
else:
    print("✗ Not all conditions met - cannot auto-graduate")
