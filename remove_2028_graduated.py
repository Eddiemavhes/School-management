#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance

print("="*80)
print("DELETING 2028 BALANCES FOR GRADUATED STUDENTS")
print("="*80)

for name in ['Cathrine', 'David']:
    student = Student.all_students.get(first_name=name)
    balances_2028 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2028
    )
    
    print(f"\n{name}:")
    print(f"  Current Status: {student.status}")
    print(f"  2028 Balances Found: {balances_2028.count()}")
    
    for balance in balances_2028:
        print(f"    - {balance.term}: ${balance.current_balance:.2f}")
        balance.delete()
    
    print(f"  ✓ All 2028 balances deleted")

print("\n" + "="*80)
print("VERIFICATION:")
print("="*80)

for name in ['Cathrine', 'David']:
    student = Student.all_students.get(first_name=name)
    has_2028 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2028
    ).exists()
    print(f"\n{name}:")
    print(f"  Status: {student.status}")
    print(f"  Is Active: {student.is_active}")
    print(f"  Is Archived: {student.is_archived}")
    print(f"  Has 2028 balance: {'❌ YES (ERROR!)' if has_2028 else '✓ NO (Correct)'}")
