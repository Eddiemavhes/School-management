#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.fee import StudentBalance
from core.models.academic import Payment
from decimal import Decimal

s = Student.objects.get(id=64)
print(f"FIXING PAYMENT DISTRIBUTION FOR: {s.full_name}")
print("=" * 70)

# Get the $1080 payment (Payment ID 55)
payment = Payment.objects.get(id=55)
print(f"\nPayment to redistribute: ID {payment.id}, Amount: ${payment.amount}, Term: {payment.term}")

# Get current year balances
current_year = 2029
balances_2029 = StudentBalance.objects.filter(
    student=s,
    term__academic_year=current_year
).order_by('term__term')

print(f"\nCurrent balances for 2029 (before redistribution):")
for b in balances_2029:
    print(f"  T{b.term.term}: Fee=${b.term_fee}, Paid=${b.amount_paid}, Balance=${b.current_balance}")

# Redistribute: Apply $1080 to earliest unpaid terms first
remaining_payment = Decimal(str(payment.amount))
print(f"\nRedistributing ${remaining_payment}...")

for balance in balances_2029:
    if remaining_payment <= 0:
        break
    
    if balance.current_balance > 0:
        # This term needs payment
        amount_to_apply = min(remaining_payment, balance.current_balance)
        balance.amount_paid = Decimal(str(balance.amount_paid)) + amount_to_apply
        balance.save()
        remaining_payment -= amount_to_apply
        print(f"  Applied ${amount_to_apply} to T{balance.term.term}")

print(f"\nRemaining payment to apply to current term (T3): ${remaining_payment}")
current_term_balance = StudentBalance.objects.get(student=s, term__academic_year=2029, term__term=3)
if remaining_payment > 0:
    current_term_balance.amount_paid = Decimal(str(current_term_balance.amount_paid)) + remaining_payment
    current_term_balance.save()
    print(f"  Applied ${remaining_payment} to T3")

print(f"\nNew balances for 2029 (after redistribution):")
for b in StudentBalance.objects.filter(student=s, term__academic_year=current_year).order_by('term__term'):
    print(f"  T{b.term.term}: Fee=${b.term_fee}, Paid=${b.amount_paid}, Balance=${b.current_balance}")

print(f"\nStudent overall_balance: ${s.overall_balance}")
print("DONE!")
