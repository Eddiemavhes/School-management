#!/usr/bin/env python
"""Diagnose why David's payment is not being recorded"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.academic import Payment, AcademicTerm
from core.models.fee import StudentBalance
from decimal import Decimal

# Find David
david = Student.objects.filter(first_name='David').first()
if not david:
    print("David not found!")
    exit(1)

print(f"{'='*60}")
print(f"DAVID'S PROFILE")
print(f"{'='*60}")
print(f"Name: {david.full_name}")
print(f"Grade: {david.current_class.grade if david.current_class else 'N/A'}")
print(f"is_active: {david.is_active}")
print(f"is_archived: {david.is_archived}")
print(f"Status: {david.status}")

print(f"\n{'='*60}")
print(f"DAVID'S BALANCE RECORDS")
print(f"{'='*60}")

balances = StudentBalance.objects.filter(student=david).order_by('term__academic_year', 'term__term')
total_due = Decimal('0')
total_paid = Decimal('0')

for balance in balances:
    print(f"\n{balance.term}:")
    print(f"  Term Fee: ${balance.term_fee}")
    print(f"  Previous Arrears: ${balance.previous_arrears}")
    print(f"  Amount Paid: ${balance.amount_paid}")
    print(f"  Total Due: ${balance.total_due}")
    print(f"  Current Balance: ${balance.current_balance}")
    total_due += balance.total_due
    total_paid += balance.amount_paid

print(f"\n{'='*60}")
print(f"TOTALS")
print(f"{'='*60}")
print(f"Total Due (all terms): ${total_due}")
print(f"Total Paid (all terms): ${total_paid}")
print(f"Sum of current_balances: ${sum(b.current_balance for b in balances)}")
print(f"Latest balance current_balance: ${balances.last().current_balance if balances.exists() else 'N/A'}")

print(f"\n{'='*60}")
print(f"DAVID'S PAYMENTS")
print(f"{'='*60}")

payments = Payment.objects.filter(student=david).order_by('payment_date')
if not payments.exists():
    print("NO PAYMENTS RECORDED")
else:
    for payment in payments:
        print(f"{payment.payment_date} | {payment.term}: ${payment.amount}")

print(f"\n{'='*60}")
print(f"CURRENT TERM INFO")
print(f"{'='*60}")

current_term = AcademicTerm.get_current_term()
if current_term:
    print(f"Current Term: {current_term}")
    print(f"is_current: {current_term.is_current}")
    current_balance = StudentBalance.objects.filter(student=david, term=current_term).first()
    if current_balance:
        print(f"David's balance in current term: ${current_balance.current_balance}")
else:
    print("No current term set!")

print(f"\n{'='*60}")
print(f"CREATING TEST PAYMENT (checking if it saves)")
print(f"{'='*60}")

if current_term and david.is_active:
    try:
        # Try to create and save a payment
        test_payment = Payment(
            student=david,
            amount=Decimal('100.00'),
            payment_method='CASH',
            term=current_term,
            recorded_by=None  # No user recorded
        )
        
        print(f"Before save:")
        print(f"  Payment object exists in DB: {test_payment.pk is not None}")
        
        test_payment.save()
        
        print(f"\nAfter save:")
        print(f"  Payment ID: {test_payment.pk}")
        print(f"  Payment amount: ${test_payment.amount}")
        print(f"  Receipt number: {test_payment.receipt_number}")
        
        # Check if it appears in database
        saved_payment = Payment.objects.get(pk=test_payment.pk)
        print(f"\nVerification from DB:")
        print(f"  Found payment: {saved_payment}")
        print(f"  Amount: ${saved_payment.amount}")
        
        # Check if balance updated
        updated_balance = StudentBalance.objects.get(student=david, term=current_term)
        print(f"\nBalance after payment:")
        print(f"  Amount Paid: ${updated_balance.amount_paid}")
        print(f"  Current Balance: ${updated_balance.current_balance}")
        
        # Delete the test payment
        test_payment.delete()
        print(f"\nTest payment deleted.")
        
    except Exception as e:
        import traceback
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
else:
    print(f"Cannot create test payment: current_term={current_term}, is_active={david.is_active}")
