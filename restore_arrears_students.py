#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, StudentMovement

print("=" * 80)
print("CORRECTING GRADUATION - RESTORING STUDENTS WITH ARREARS")
print("=" * 80)
print()

# Students to restore (those with arrears in 2027)
students_to_restore = {
    'Cathrine': 10,   # Has $10 arrears
    'David': 600,     # Has $600 arrears
}

for name, expected_arrears in students_to_restore.items():
    student = Student.objects.filter(first_name=name).first()
    
    print(f"Restoring: {name}")
    print(f"  Current Status: {student.get_status_display()}")
    print(f"  Is Active: {student.is_active}")
    print(f"  Is Archived: {student.is_archived}")
    
    # Check their 2027 balance
    final_2027 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2027,
        term__term=3
    ).first()
    
    if final_2027:
        print(f"  2027 Final Balance: ${final_2027.current_balance}")
    
    # Restore to ENROLLED and ACTIVE (but NOT archived)
    Student.objects.filter(pk=student.pk).update(
        status='ENROLLED',
        is_active=True,
        is_archived=False
    )
    
    print(f"  ✓ Restored to ENROLLED and ACTIVE")
    
    # Delete the erroneous graduation movement
    movements_deleted, _ = StudentMovement.objects.filter(
        student=student,
        movement_type='GRADUATION'
    ).delete()
    
    print(f"  ✓ Deleted {movements_deleted} graduation record(s)")
    print()

print("=" * 80)
print("VERIFICATION")
print("=" * 80)
print()

# Check current state
cathrine = Student.objects.filter(first_name='Cathrine').first()
david = Student.objects.filter(first_name='David').first()

print(f"Cathrine:")
print(f"  Status: {cathrine.get_status_display()}")
print(f"  Is Active: {cathrine.is_active}")
print(f"  Is Archived: {cathrine.is_archived}")

final_2027 = StudentBalance.objects.filter(
    student=cathrine,
    term__academic_year=2027,
    term__term=3
).first()
if final_2027:
    print(f"  2027 Final Balance (Arrears): ${final_2027.current_balance}")
    if final_2027.current_balance > 0:
        print(f"  ⚠️ Has arrears - should NOT be Alumni until paid")
print()

print(f"David:")
print(f"  Status: {david.get_status_display()}")
print(f"  Is Active: {david.is_active}")
print(f"  Is Archived: {david.is_archived}")

final_2027 = StudentBalance.objects.filter(
    student=david,
    term__academic_year=2027,
    term__term=3
).first()
if final_2027:
    print(f"  2027 Final Balance (Arrears): ${final_2027.current_balance}")
    if final_2027.current_balance > 0:
        print(f"  ⚠️ Has arrears - should NOT be Alumni until paid")
