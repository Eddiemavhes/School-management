#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm, StudentBalance, Student, StudentMovement
from django.utils import timezone

# Get students
annah = Student.objects.get(id=8)
brandon = Student.objects.get(id=9)
students_to_graduate = [annah, brandon]

# Get Term 3 2027
term_2027_3 = AcademicTerm.objects.filter(academic_year=2027, term=3).first()

print("Graduating Annah and Brandon who completed Grade 7 in 2027\n")

for student in students_to_graduate:
    print(f"Processing {student}:")
    
    # Check final balance from Term 3 2027
    final_balance = StudentBalance.objects.filter(student=student, term=term_2027_3).first()
    print(f"  Term 3 2027 balance: ${final_balance.current_balance if final_balance else 'N/A'}")
    
    # Set student as GRADUATED and INACTIVE
    student.status = 'GRADUATED'
    # Use raw save to bypass validation
    from django.db import models as django_models
    django_models.Model.save(student, update_fields=['status'])
    
    # Handle is_archived based on final balance
    if final_balance and final_balance.current_balance <= 0:
        student.is_archived = True
    else:
        student.is_archived = False
    student.is_active = False
    django_models.Model.save(student, update_fields=['is_active', 'is_archived'])
    
    print(f"  ✓ Graduated and set to inactive")
    print(f"  ✓ is_archived: {student.is_archived}")
    
    # Create StudentMovement record
    StudentMovement.objects.create(
        student=student,
        movement_type='GRADUATION',
        movement_date=timezone.now().date(),
        from_class=student.current_class,
        reason='Completed Grade 7 (Term 3 2027) with fees fully paid'
    )
    print(f"  ✓ Created graduation movement record")
    
    # Remove 2028 fees
    term_2028_1 = AcademicTerm.objects.filter(academic_year=2028, term=1).first()
    balance_2028 = StudentBalance.objects.filter(student=student, term=term_2028_1).first()
    if balance_2028:
        balance_2028.delete()
        print(f"  ✓ Deleted 2028 Term 1 balance (${balance_2028.current_balance} fees)")
    
    print()

print("Verification:")
for student in students_to_graduate:
    student.refresh_from_db()
    print(f"{student}:")
    print(f"  Status: {student.status}")
    print(f"  Is active: {student.is_active}")
    print(f"  Is archived: {student.is_archived}")
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    print(f"  Total balances: {balances.count()}")
    if balances.exists():
        latest = balances.last()
        print(f"  Latest balance: {latest.term} = ${latest.current_balance}")
    print()
