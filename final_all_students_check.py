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
print("FINAL SYSTEM VERIFICATION - ALL STUDENTS")
print("=" * 80)
print()

students = Student.objects.filter(first_name__in=['Brandon', 'Cathrine', 'David', 'Annah']).order_by('first_name')

for student in students:
    print(f"{student.first_name} {student.surname}:")
    print(f"  Status: {student.get_status_display()}")
    
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    print(f"  Balances ({balances.count()} terms):")
    
    for b in balances:
        print(f"    {b.term}: Fee ${b.term_fee}, Paid ${b.amount_paid}, Balance ${b.current_balance}")
    
    print(f"  Overall Balance: ${student.overall_balance}")
    print()

print("=" * 80)
print("EXPECTED VS ACTUAL")
print("=" * 80)
print()

expectations = {
    'Brandon': ('$0', 'Paid $100 for $100 fee'),
    'Cathrine': ('$40', 'Paid $60 for $100 fee'),
    'David': ('$100', 'No payment for $100 fee'),
    'Annah': ('$80', 'Credit of $20 applied to $100 fee in Term 2'),
}

for name, (expected, reason) in expectations.items():
    student = Student.objects.filter(first_name=name).first()
    if student:
        actual = f"${student.overall_balance}"
        status = "✓" if str(student.overall_balance) == expected.replace('$', '') else "❌"
        print(f"{status} {name}: Expected {expected}, Got {actual} ({reason})")

print()
