#!/usr/bin/env python
"""
YEAR-END GRADE 7 GRADUATION PROCESS
Automatically graduates all Grade 7 students when they complete the academic year
"""
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, StudentMovement, Class
from django.utils import timezone

print("="*80)
print("YEAR-END GRADE 7 GRADUATION PROCESS (2027 → 2028)")
print("="*80)

# Find all Grade 7 students
grade7_classes = Class.objects.filter(grade=7)
grade7_students = Student.objects.filter(current_class__in=grade7_classes, is_active=True)

print(f"\nFound {grade7_students.count()} active Grade 7 students\n")

for student in grade7_students:
    # Get their final 2027 balance
    final_balance = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2027
    ).order_by('-term__term').first()
    
    if not final_balance:
        print(f"{student.first_name}: No 2027 balance found - skipping")
        continue
    
    print(f"\n{student.first_name}:")
    print(f"  Final 2027 Balance: ${final_balance.current_balance:.2f}")
    
    # Determine alumni status based on balance
    if final_balance.current_balance <= 0:
        # Fully paid or has credit - becomes Alumni
        alumni_status = True
        status_text = "ALUMNI (fully paid)"
    else:
        # Has arrears - graduated but not alumni yet
        alumni_status = False
        status_text = "GRADUATED (has arrears)"
    
    # Update student status
    student.status = 'GRADUATED'
    student.is_active = False
    student.is_archived = alumni_status
    student.save()
    
    # Create graduation movement record
    movement = StudentMovement.objects.create(
        student=student,
        from_class=student.current_class,
        to_class=None,
        movement_type='GRADUATION',
        reason=f'Completed Grade 7 (2027). Final balance: ${final_balance.current_balance:.2f}. Status: {status_text}'
    )
    
    print(f"  ✓ Graduated → {status_text}")
    print(f"  ✓ Movement record created")

print("\n" + "="*80)
print("GRADUATION PROCESS COMPLETE")
print("="*80)

# Verify results
print("\nVERIFICATION:")
graduated = Student.objects.filter(status='GRADUATED')
print(f"Total graduated students: {graduated.count()}")

for student in graduated:
    alumni_status = "ALUMNI ✓" if student.is_archived else "GRADUATED (not alumni)"
    final_balance = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2027
    ).order_by('-term__term').first()
    
    if final_balance:
        print(f"  {student.first_name}: {alumni_status} (Balance: ${final_balance.current_balance:.2f})")
