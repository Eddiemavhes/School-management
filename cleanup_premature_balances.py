#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance

print("=" * 80)
print("CLEANUP - REMOVE PREMATURELY CREATED TERM 2 & 3 BALANCES")
print("=" * 80)
print()

students_to_fix = ['Brandon', 'Cathrine', 'David']

for student_name in students_to_fix:
    student = Student.objects.filter(first_name=student_name).first()
    if not student:
        continue
    
    print(f"\nFIXING: {student.first_name} {student.surname}")
    print("-" * 80)
    
    # Show before
    print(f"BEFORE:")
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    print(f"  Total balance records: {balances.count()}")
    for b in balances:
        print(f"    {b.term}: Balance ${b.current_balance}")
    
    # Delete Term 2 & 3 for 2026 (premature creation)
    deleted = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2026,
        term__term__in=[2, 3]
    ).delete()
    
    print(f"\nDELETED: {deleted[0]} records")
    
    # Show after
    print(f"\nAFTER:")
    student.refresh_from_db()
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    print(f"  Total balance records: {balances.count()}")
    for b in balances:
        print(f"    {b.term}: Balance ${b.current_balance}")
    print(f"  Overall Balance: ${student.overall_balance}")
    print()

print()
print("=" * 80)
print("VERIFICATION:")
print("=" * 80)
print()

brandon = Student.objects.filter(first_name='Brandon').first()
cathrine = Student.objects.filter(first_name='Cathrine').first()
david = Student.objects.filter(first_name='David').first()

print(f"Brandon: ${brandon.overall_balance} (should be $0 - paid $100 for $100 fee)")
print(f"Cathrine: ${cathrine.overall_balance} (should be $40 - paid $60 for $100 fee)")
print(f"David: ${david.overall_balance} (should be $100 - paid $0 for $100 fee)")
