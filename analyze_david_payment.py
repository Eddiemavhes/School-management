#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, Payment
from core.models.academic import AcademicTerm

print("="*80)
print("DAVID'S PAYMENT AND BALANCE ANALYSIS")
print("="*80)

david = Student.all_students.get(first_name='David')

print(f"\nStudent: {david.first_name}")
print(f"Status: {david.status}")
print(f"Active: {david.is_active}")

# Get all payments
print("\n" + "="*80)
print("PAYMENTS RECORDED")
print("="*80)

payments = Payment.objects.filter(student=david).order_by('created_at')
print(f"\nTotal payments: {payments.count()}")

for payment in payments:
    print(f"  {payment.created_at.date()}: ${payment.amount:.2f} for {payment.term}")

# Get all balances
print("\n" + "="*80)
print("BALANCE HISTORY")
print("="*80)

balances = StudentBalance.objects.filter(student=david).order_by('term__academic_year', 'term__term')
print(f"\nTotal balances: {balances.count()}\n")

for balance in balances:
    print(f"{balance.term.academic_year} T{balance.term.term}:")
    print(f"  Fee: ${balance.term_fee:.2f}")
    print(f"  Paid: ${balance.amount_paid:.2f}")
    print(f"  Arrears: ${balance.previous_arrears:.2f}")
    print(f"  Current Balance: ${balance.current_balance:.2f}")

# Final balance
final = balances.order_by('-term__academic_year', '-term__term').first()
if final:
    print(f"\n" + "="*80)
    print(f"FINAL BALANCE: ${final.current_balance:.2f}")
    print("="*80)
    
    print(f"\nExpected: 600 (6 terms x 100 unpaid)")
    print(f"Actual: ${final.current_balance:.2f}")
    
    if final.current_balance == 600:
        print("Status: CORRECT")
    else:
        print("Status: INCORRECT")
