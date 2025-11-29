#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, Payment

print("=" * 80)
print("COMPLETE SYSTEM VERIFICATION")
print("=" * 80)
print()

# Key students to verify
students_to_check = [
    ('Brandon', 'B', '$0'),
    ('Cathrine', 'C', '$40'),
    ('David', 'D', '$100'),
    ('Annah', 'A', '-$20'),
    ('Edwin', 'E', '$0 (Alumni)'),
]

for first, last, expected in students_to_check:
    student = Student.objects.filter(first_name=first).first()
    if not student:
        continue
    
    print(f"\n{first} {last}:")
    print("-" * 80)
    
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    payments = Payment.objects.filter(student=student).order_by('payment_date')
    
    print(f"  Status: {student.get_status_display()}")
    if student.current_class:
        print(f"  Class: {student.current_class}")
    print(f"  Balances: {balances.count()} records")
    
    for b in balances:
        print(f"    {b.term.academic_year} T{b.term.term}: Fee ${b.term_fee}, Paid ${b.amount_paid}, Balance ${b.current_balance}")
    
    print(f"  Payments: {payments.count()} records")
    for p in payments:
        print(f"    {p.payment_date}: ${p.amount} for {p.term}")
    
    print(f"  Overall Balance: {student.overall_balance}")
    print(f"  Expected: {expected}")
    
    if str(student.overall_balance) == expected.replace('$', '').replace(' (Alumni)', '').replace(' ', ''):
        print(f"  ✓ CORRECT")
    else:
        print(f"  ❌ MISMATCH")

print()
print("=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
