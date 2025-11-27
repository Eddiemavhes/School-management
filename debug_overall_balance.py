#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.fee import StudentBalance
from decimal import Decimal

s = Student.objects.get(id=64)
print(f"Student: {s.full_name}")
print("=" * 60)

# Get all balances
balances = StudentBalance.objects.filter(student=s)
print(f"\nAll {balances.count()} StudentBalance records:")
for b in balances:
    print(f"  {b.term.academic_year} T{b.term.term}: Fee={Decimal(b.term_fee)}, Paid={Decimal(b.amount_paid)}, Balance={Decimal(b.current_balance)}")

# Calculate overall_balance the current way
total_fees = sum([Decimal(b.term_fee) for b in balances])
print(f"\nTotal term_fees (all records): {total_fees}")

all_payments = sum([Decimal(p.amount) for p in s.payments.all()])
print(f"Total payments (all): {all_payments}")

calculated_balance = total_fees - all_payments
print(f"Calculated overall_balance: {total_fees} - {all_payments} = {calculated_balance}")

# What the property returns
actual_balance = s.overall_balance
print(f"\nActual s.overall_balance: {actual_balance}")
print(f"Match: {calculated_balance == Decimal(str(actual_balance))}")

# What should it be? (current year only)
print("\n" + "=" * 60)
print("SHOULD IT BE CURRENT YEAR ONLY?")
current_year_balances = StudentBalance.objects.filter(student=s, term__academic_year=2029)
print(f"\n2029 balances only:")
for b in current_year_balances:
    print(f"  {b.term.academic_year} T{b.term.term}: Balance={Decimal(b.current_balance)}")

# Outstanding for current year
outstanding_current_year = sum([Decimal(b.current_balance) for b in current_year_balances if Decimal(b.current_balance) > 0])
print(f"\nCurrent year outstanding (> 0): {outstanding_current_year}")
