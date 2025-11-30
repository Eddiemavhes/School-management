#!/usr/bin/env python
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentMovement
from datetime import datetime

print("=" * 80)
print("GRADUATING STUDENTS WHO HAVE PAID ALL ARREARS")
print("=" * 80)

students_to_graduate = ['Cathrine', 'David']

for name in students_to_graduate:
    student = Student.objects.get(first_name=name)
    balance = student.overall_balance
    
    if balance <= 0 and int(student.current_class.grade) >= 7:
        print(f"\n{student.first_name}:")
        print(f"  Balance: ${balance:.2f}")
        print(f"  Grade: {student.current_class.grade}")
        
        # Mark as graduated
        student.status = 'GRADUATED'
        student.is_active = False
        student.is_archived = True
        student.save()
        
        # Create movement record
        movement = StudentMovement.objects.create(
            student=student,
            from_class=student.current_class,
            to_class=None,
            movement_type='GRADUATION',
            reason=f'Graduated: Paid off all arrears (final balance ${balance:.2f})'
        )
        
        print(f"  ✓ Marked as GRADUATED")
        print(f"  ✓ Set to INACTIVE")
        print(f"  ✓ Archived in Alumni")
        print(f"  ✓ Movement record created")
    else:
        print(f"\n{name}: Balance ${balance:.2f} - NOT eligible (must be $0 or less)")

print("\n" + "=" * 80)
print("GRADUATION COMPLETE")
print("=" * 80)
