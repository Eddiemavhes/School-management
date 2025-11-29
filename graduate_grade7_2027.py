#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm, StudentMovement

print("=" * 80)
print("GRADUATING GRADE 7 STUDENTS FROM 2027")
print("=" * 80)
print()

# Get all Grade 7 students who completed 2027
grade7_students = Student.objects.filter(
    current_class__grade=7,
    is_active=True,
    is_deleted=False
)

graduated_count = 0

for student in grade7_students:
    # Check if they have Third Term 2027
    last_2027 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2027,
        term__term=3
    ).first()
    
    if not last_2027:
        continue
    
    print(f"Graduating: {student.full_name}")
    print(f"  Final 2027 Balance: ${last_2027.current_balance}")
    
    # Delete 2028 balances
    deleted_count, _ = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2028
    ).delete()
    print(f"  Deleted {deleted_count} 2028 balance records")
    
    # Create graduation movement record
    try:
        movement = StudentMovement(
            student=student,
            from_class=student.current_class,
            to_class=None,
            movement_type='GRADUATION',
            moved_by=None,  # System automatic
            previous_arrears=last_2027.current_balance if last_2027.current_balance > 0 else 0,
            preserved_arrears=last_2027.current_balance if last_2027.current_balance > 0 else 0,
            reason=f'Graduated: Completed Grade 7 in 2027 with balance ${last_2027.current_balance}'
        )
        movement.save()
        print(f"  Created graduation movement record")
    except Exception as e:
        print(f"  Error creating movement: {e}")
    
    # Mark as graduated and archived
    Student.objects.filter(pk=student.pk).update(
        status='GRADUATED',
        is_active=False,
        is_archived=True
    )
    
    print(f"  ✓ Marked as GRADUATED, ARCHIVED, INACTIVE")
    print()
    
    graduated_count += 1

print("=" * 80)
print(f"GRADUATION COMPLETE: {graduated_count} students graduated")
print("=" * 80)
print()

# Verify
print("VERIFICATION:")
print()

alumni = Student.objects.filter(status='GRADUATED', is_archived=True)
print(f"Total Alumni in system: {alumni.count()}")

for student in alumni:
    print(f"  {student.full_name}: {student.get_status_display()}, Archived: {student.is_archived}")

print()
print("Active students (should be empty or non-Grade 7):")

active_grade7 = Student.objects.filter(
    current_class__grade=7,
    is_active=True,
    is_deleted=False
)

if active_grade7.exists():
    print(f"  ❌ Still {active_grade7.count()} Grade 7 active students!")
    for s in active_grade7:
        print(f"    {s.full_name}")
else:
    print(f"  ✓ No Grade 7 students remaining active")
