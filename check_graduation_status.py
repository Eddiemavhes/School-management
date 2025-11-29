#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentMovement, StudentBalance, AcademicTerm

print("=" * 80)
print("CHECKING FOR INCORRECTLY GRADUATED STUDENTS")
print("=" * 80)
print()

# Check all graduated students
graduated = Student.objects.filter(status='GRADUATED')
print(f"Total Graduated Students: {graduated.count()}\n")

for student in graduated:
    print(f"{student.full_name}:")
    print(f"  Status: {student.get_status_display()}")
    print(f"  Is Archived: {student.is_archived}")
    print(f"  Current Class: {student.current_class}")
    print()
    
    # Check their last movement
    movements = StudentMovement.objects.filter(student=student).order_by('-movement_date')
    if movements.exists():
        last_movement = movements.first()
        print(f"  Last Movement: {last_movement.movement_type} on {last_movement.movement_date}")
        print(f"    Reason: {last_movement.reason}")
    
    # Check their balances
    balances = StudentBalance.objects.filter(student=student).order_by('-term__academic_year', '-term__term')
    print(f"  Balances: {balances.count()} terms")
    for b in balances[:3]:  # Show last 3
        print(f"    {b.term}: ${b.current_balance}")
    
    print()

print("=" * 80)
print("CHECKING CURRENT ACTIVE STUDENTS")
print("=" * 80)
print()

active = Student.objects.filter(is_active=True, is_deleted=False)
print(f"Active Students: {active.count()}\n")

for student in active:
    if student.current_class and int(student.current_class.grade) == 7:
        print(f"✓ {student.full_name} - Grade 7 (Active - Correct)")
        print(f"  Balance: ${student.overall_balance}")
        print()
