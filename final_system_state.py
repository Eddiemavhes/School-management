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
print("FINAL SYSTEM STATE VERIFICATION")
print("=" * 80)
print()

current_term = AcademicTerm.objects.filter(is_current=True).first()
print(f"Current Term: {current_term}")
print()

students = Student.objects.filter(first_name__in=['Annah', 'Brandon', 'Cathrine', 'David']).order_by('first_name')

for student in students:
    print(f"\n{student.first_name} {student.surname}:")
    print("-" * 80)
    print(f"  Status: {student.get_status_display()}")
    print(f"  Class: {student.current_class}")
    print()
    
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    
    print(f"  Term Breakdown:")
    for b in balances:
        status = "CURRENT" if b.term == current_term else "PREVIOUS"
        print(f"    {b.term} [{status}]:")
        print(f"      Fee: ${b.term_fee}")
        print(f"      Arrears: ${b.previous_arrears}")
        print(f"      Paid: ${b.amount_paid}")
        print(f"      Balance: ${b.current_balance}")
    
    print()
    print(f"  Overall Outstanding: ${student.overall_balance}")
    print()

print("=" * 80)
print("SUMMARY & VERIFICATION")
print("=" * 80)
print()

tests = [
    ("Annah", 80, "Paid \$120 for \$100 Term 1 fee → \$20 credit applied to \$100 Term 2 fee = \$80"),
    ("Brandon", 100, "Paid \$100 for \$100 Term 1 fee → New \$100 Term 2 fee = \$100"),
    ("Cathrine", 140, "Paid \$60 for \$100 Term 1 fee → \$40 arrears + \$100 Term 2 fee = \$140"),
    ("David", 200, "Paid \$0 for \$100 Term 1 fee → \$100 arrears + \$100 Term 2 fee = \$200"),
]

all_pass = True
for name, expected, explanation in tests:
    student = Student.objects.filter(first_name=name).first()
    actual = float(student.overall_balance)
    passed = actual == expected
    all_pass = all_pass and passed
    
    status = "✓" if passed else "❌"
    print(f"{status} {name}: Expected \${expected}, Got \${actual}")
    print(f"   {explanation}")
    print()

print("=" * 80)
if all_pass:
    print("✓ ALL TESTS PASSED - System is working correctly!")
else:
    print("❌ Some tests failed")
print("=" * 80)
