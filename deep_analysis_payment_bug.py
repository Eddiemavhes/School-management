#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm, StudentBalance, Payment
from decimal import Decimal

student = Student.objects.get(first_name='Edwin', surname='Mavhe')
current_term = AcademicTerm.objects.filter(is_current=True).first()

print("=" * 80)
print("DEEP ANALYSIS - PAYMENT PROCESSING BUG")
print("=" * 80)
print()

print(f"Current Term: {current_term}")
print(f"Student: {student.first_name} {student.surname}")
print(f"Overall Balance Displayed: ${student.overall_balance}")
print()

# Get all payments
payments = Payment.objects.filter(student=student).order_by('payment_date')
print("ALL PAYMENTS:")
print("-" * 80)
total_paid = Decimal('0')
for p in payments:
    total_paid += p.amount
    print(f"  {p.payment_date}: ${p.amount} for {p.term} (Total so far: ${total_paid})")

if not payments.exists():
    print("  No payments found")

print()

# Get all balances
print("ALL BALANCES:")
print("-" * 80)
balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
for b in balances:
    print(f"  {b.term}:")
    print(f"    Term Fee: ${b.term_fee}")
    print(f"    Previous Arrears: ${b.previous_arrears}")
    print(f"    Total Due: ${b.total_due}")
    print(f"    Amount Paid: ${b.amount_paid}")
    print(f"    Current Balance: ${b.current_balance}")
    print()

print("=" * 80)
print("ANALYSIS:")
print("=" * 80)

# Check the 2028 T1 balance specifically
b_2028_t1 = balances.filter(term__academic_year=2028, term__term=1).first()
if b_2028_t1:
    print(f"2028 T1 Analysis:")
    print(f"  Total Due: ${b_2028_t1.total_due}")
    print(f"  Amount Paid: ${b_2028_t1.amount_paid}")
    print(f"  Current Balance: ${b_2028_t1.current_balance}")
    print(f"  Expected after $600 payment: $0 (paid entire 2027 arrears)")
    print(f"  Actual: ${b_2028_t1.current_balance}")
    
    if b_2028_t1.current_balance != 0:
        print(f"  ❌ BUG FOUND: Payment not properly credited to this balance")
        print(f"     Difference: ${b_2028_t1.current_balance} still owed")

print()
print("POTENTIAL ISSUES:")
print("-" * 80)

# Issue 1: Payment might not be recorded for 2028 T1
payments_2028_t1 = Payment.objects.filter(student=student, term__academic_year=2028, term__term=1)
print(f"1. Payments specifically for 2028 T1: {payments_2028_t1.count()}")
for p in payments_2028_t1:
    print(f"   - ${p.amount}")

# Issue 2: Check if payment was for 2027 T3 instead
payments_2027_t3 = Payment.objects.filter(student=student, term__academic_year=2027, term__term=3)
print(f"2. Payments specifically for 2027 T3: {payments_2027_t3.count()}")
for p in payments_2027_t3:
    print(f"   - ${p.amount} (2027 T3 balance was ${StudentBalance.objects.get(student=student, term__academic_year=2027, term__term=3).total_due})")

# Issue 3: Check overall_balance property
print(f"3. Overall Balance Calculation:")
print(f"   Returns: {student.overall_balance}")
b_latest = balances.last()
if b_latest:
    print(f"   Latest balance object: {b_latest.term} = ${b_latest.current_balance}")
    print(f"   Should be same: {student.overall_balance == b_latest.current_balance}")
