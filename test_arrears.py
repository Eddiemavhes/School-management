#!/usr/bin/env python
"""
Test script to verify arrears logic
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.academic import AcademicTerm
from core.models.fee import StudentBalance

print("=" * 80)
print("ARREARS CALCULATION TEST")
print("=" * 80)
print()

# Get all students
students = Student.objects.all()

# Get current term
current_term = AcademicTerm.get_current_term()

print(f"Current Term: {current_term}")
print()

for student in students:
    print(f"Student: {student.surname}, {student.first_name}")
    print("-" * 80)
    
    # Get current balance
    current_balance = StudentBalance.objects.filter(
        student=student,
        term=current_term
    ).first()
    
    if current_balance:
        print(f"  Current Term: {current_term}")
        print(f"    - Term Fee: ${current_balance.term_fee:.2f}")
        print(f"    - Previous Arrears: ${current_balance.previous_arrears:.2f}")
        print(f"    - Amount Paid (This Term): ${current_balance.amount_paid:.2f}")
        print(f"    - Arrears Remaining: ${current_balance.arrears_remaining:.2f}")
        print(f"    - Term Fee Remaining: ${current_balance.term_fee_remaining:.2f}")
        print(f"    - Current Balance: ${current_balance.current_balance:.2f}")
        print(f"    - Payment Priority: {current_balance.payment_priority}")
    else:
        print(f"  No balance for current term!")
    
    # Show all balances for this student
    all_balances = StudentBalance.objects.filter(student=student).order_by('-term__academic_year', '-term__term')
    
    if all_balances.count() > 1:
        print()
        print(f"  All Balances for {student.surname}:")
        for balance in all_balances:
            status = "✓ PAID" if balance.current_balance <= 0 else f"✗ OWES ${balance.current_balance:.2f}"
            print(f"    - {balance.term}: {status}")
    
    print()

print("=" * 80)
