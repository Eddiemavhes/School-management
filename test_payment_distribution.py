#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.fee import StudentBalance
from core.models.academic import Payment, AcademicTerm
from decimal import Decimal

s = Student.objects.get(id=62)
current_term = AcademicTerm.get_current_term()

print("=" * 70)
print(f"TESTING PAYMENT DISTRIBUTION FOR: {s.full_name}")
print("=" * 70)

# Show balances BEFORE payment
print("\nBEFORE PAYMENT:")
all_balances = StudentBalance.objects.filter(student=s).order_by('-term__academic_year', '-term__term')
for b in all_balances[:5]:  # Show first 5
    print(f"  {b.term.academic_year} T{b.term.term}: Fee=${b.term_fee}, Arrears=${b.previous_arrears}, Paid=${b.amount_paid}, Balance=${b.current_balance}")

outstanding_before = sum([float(b.current_balance) for b in all_balances if b.current_balance > 0])
print(f"\nTotal outstanding BEFORE: ${outstanding_before}")

# Record a $100 payment
print(f"\n🟦 Recording $100 payment...")
from core.models.administrator import Administrator
admin = Administrator.objects.first()
payment = Payment(
    student=s,
    amount=Decimal('100'),
    payment_method='CASH',
    term=current_term,
    recorded_by=admin
)
payment.save()

# Show balances AFTER payment
print("\nAFTER PAYMENT:")
all_balances_after = StudentBalance.objects.filter(student=s).order_by('-term__academic_year', '-term__term')
for b in all_balances_after[:5]:  # Show first 5
    print(f"  {b.term.academic_year} T{b.term.term}: Fee=${b.term_fee}, Arrears=${b.previous_arrears}, Paid=${b.amount_paid}, Balance=${b.current_balance}")

outstanding_after = sum([float(b.current_balance) for b in all_balances_after if b.current_balance > 0])
print(f"\nTotal outstanding AFTER: ${outstanding_after}")
print(f"Reduction: ${outstanding_before - outstanding_after} (should be $100)")

# Find which terms got the payment
print("\nPAYMENT DISTRIBUTION:")
print("(showing only terms that changed)")
for before, after in zip(all_balances, all_balances_after):
    if before.amount_paid != after.amount_paid:
        paid_increase = float(after.amount_paid) - float(before.amount_paid)
        print(f"  {after.term.academic_year} T{after.term.term}: +${paid_increase} payment")
