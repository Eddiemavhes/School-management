#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm

print("=" * 80)
print("FINAL SYSTEM VERIFICATION - 2027 TERM 2")
print("=" * 80)
print()

current_term = AcademicTerm.objects.filter(is_current=True).first()
print(f"Current Term: {current_term}\n")

students = Student.objects.filter(first_name__in=['Annah', 'Brandon', 'Cathrine', 'David']).order_by('first_name')

for student in students:
    current_balance = StudentBalance.objects.filter(
        student=student,
        term=current_term
    ).first()
    
    print(f"{student.first_name}:")
    print(f"  Status: {student.get_status_display()}")
    print(f"  Class: {student.current_class}")
    if current_balance:
        print(f"  Current Term Balance: ${current_balance.current_balance}")
        print(f"  (Fee: ${current_balance.term_fee}, Arrears: ${current_balance.previous_arrears}, Paid: ${current_balance.amount_paid})")
    print(f"  Overall Balance: ${student.overall_balance}")
    print()

print("=" * 80)
print("VALIDATION")
print("=" * 80)
print()

test_cases = [
    ('Annah', 80, 'Term 1: Paid $100 for $80 due (fee $100 - credit $20) → -$20 balance'),
    ('Brandon', 100, 'Entered 2027 with $0 balance → New $100 fee for Term 2'),
    ('Cathrine', 110, 'Entered 2027 with $10 balance → Previous arrears $10 + new fee $100'),
    ('David', 500, 'Entered 2027 with $300 balance → Previous arrears $300 + new fee $100 + new fee $100'),
]

print(f"Expected Balances:\n")
all_pass = True
for name, expected, explanation in test_cases:
    student = Student.objects.filter(first_name=name).first()
    actual = float(student.overall_balance)
    passed = actual == expected
    all_pass = all_pass and passed
    
    status = "✓" if passed else "❌"
    print(f"{status} {name}: ${actual} (expected ${expected})")
    print(f"   {explanation}\n")

print("=" * 80)
if all_pass:
    print("✓✓✓ ALL BALANCES CORRECT!")
else:
    print("❌ Some balances still need attention")
print("=" * 80)
