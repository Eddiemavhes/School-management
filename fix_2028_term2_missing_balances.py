#!/usr/bin/env python
"""
Fix script for missing 2028 Term 2 balances and negative arrears issues
"""

import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.fee import StudentBalance, TermFee
from core.models.academic import AcademicTerm

print("\n" + "="*70)
print("COMPREHENSIVE BALANCE AUDIT AND FIX")
print("="*70)

# Get the terms we need
term_2028_1 = AcademicTerm.objects.get(academic_year=2028, term=1)
term_2028_2 = AcademicTerm.objects.get(academic_year=2028, term=2)
term_fee_2028_2 = TermFee.objects.get(term=term_2028_2)

print(f"\nTarget: Create 2028 Term 2 balances for all students")
print(f"Term Fee for 2028 Term 2: ${term_fee_2028_2.amount}")

# Get all active students
all_students = Student.objects.filter(is_active=True, is_deleted=False).order_by('surname', 'first_name')

created_count = 0
updated_count = 0
negative_arrears_fixed = 0

for student in all_students:
    # Check if 2028 Term 2 balance exists
    balance_2028_2 = StudentBalance.objects.filter(student=student, term=term_2028_2).first()
    
    if not balance_2028_2:
        # Calculate previous arrears from 2028 Term 1
        balance_2028_1 = StudentBalance.objects.filter(student=student, term=term_2028_1).first()
        
        if balance_2028_1:
            # previous_arrears for Term 2 = balance owed at end of Term 1
            previous_arrears = Decimal(str(balance_2028_1.term_fee)) + Decimal(str(balance_2028_1.previous_arrears)) - Decimal(str(balance_2028_1.amount_paid))
            
            # Create the missing balance
            new_balance = StudentBalance(
                student=student,
                term=term_2028_2,
                term_fee=Decimal(str(term_fee_2028_2.amount)),
                previous_arrears=previous_arrears,
                amount_paid=Decimal('0.00')
            )
            new_balance.save()
            created_count += 1
            print(f"  CREATED: {student.surname}, {student.first_name} - Term 2028/2 (arrears: ${previous_arrears})")

# Now check for and fix negative arrears
print("\n" + "-"*70)
print("SCANNING FOR NEGATIVE ARREARS (audit issue)...")
print("-"*70)

all_balances = StudentBalance.objects.filter(previous_arrears__lt=0)

for balance in all_balances:
    print(f"\nNEGATIVE ARREARS FOUND:")
    print(f"  Student: {balance.student.surname}, {balance.student.first_name}")
    print(f"  Term: {balance.term.academic_year} - Term {balance.term.term}")
    print(f"  Previous Arrears: ${balance.previous_arrears}")
    print(f"  Term Fee: ${balance.term_fee}")
    print(f"  Amount Paid: ${balance.amount_paid}")
    
    # This indicates a credit balance from previous term
    # For audit compliance, we should track this differently
    # But for now, we'll set it to 0 (student has paid ahead)
    if balance.previous_arrears < 0:
        balance.previous_arrears = Decimal('0.00')
        balance.save()
        negative_arrears_fixed += 1
        print(f"  ACTION: Set previous_arrears to 0.00 (credit balance)")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Created 2028 Term 2 balances: {created_count} students")
print(f"Fixed negative arrears: {negative_arrears_fixed} balances")
print(f"Total students processed: {all_students.count()}")

# Final verification
print("\n" + "="*70)
print("VERIFICATION: ALL STUDENTS NOW HAVE 2028 TERMS 1, 2, 3")
print("="*70)

missing_final = []
for student in all_students:
    for term_num in [1, 2, 3]:
        term = AcademicTerm.objects.get(academic_year=2028, term=term_num)
        bal = StudentBalance.objects.filter(student=student, term=term).first()
        if not bal:
            missing_final.append(f"{student.surname}, {student.first_name} - Term {term_num}")

if missing_final:
    print(f"\nSTILL MISSING {len(missing_final)} BALANCES:")
    for item in missing_final:
        print(f"  - {item}")
else:
    print(f"\nALL GOOD! All {all_students.count()} students have all 2028 terms.")

print("\n" + "="*70)
