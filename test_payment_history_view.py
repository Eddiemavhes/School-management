#!/usr/bin/env python
"""
Test the updated StudentPaymentHistoryView logic
Simulates what the view will show on Audrey's payment history page
"""

import os
import django
from decimal import Decimal
from django.db.models import Sum

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm
from core.models.fee import StudentBalance
from core.models.academic import Payment

audrey = Student.objects.get(id=61)
current_term = AcademicTerm.get_current_term()

print("\n" + "="*80)
print("SIMULATING PAYMENT HISTORY VIEW FOR AUDREY")
print("="*80)

print(f"\nCurrent Term: {current_term.academic_year} Term {current_term.term}")

# Simulate the view logic
all_balances = StudentBalance.objects.filter(student=audrey).select_related('term').order_by('term__academic_year', 'term__term')

# Filter: Only show terms up to current term
if current_term:
    all_balances = [
        b for b in all_balances 
        if (b.term.academic_year < current_term.academic_year or 
            (b.term.academic_year == current_term.academic_year and b.term.term <= current_term.term))
    ]

all_payments = Payment.objects.filter(student=audrey).select_related('term').order_by('term__academic_year', 'term__term', 'payment_date')

print(f"\n\nBuilding Payment History Table (like in the template):")
print("="*80)

payment_history = []
running_total_due = Decimal('0')
running_total_paid = Decimal('0')
running_credits = Decimal('0')

for balance in all_balances:
    term_payments = all_payments.filter(term=balance.term)
    
    running_total_due += balance.term_fee
    running_total_paid += balance.amount_paid
    
    term_due = balance.term_fee + balance.previous_arrears
    if balance.amount_paid > term_due:
        credit = balance.amount_paid - term_due
        running_credits += credit
    
    balance_owed = running_total_due - running_total_paid
    if balance_owed < 0:
        balance_owed = Decimal('0')
    
    payment_history.append({
        'term': balance.term,
        'term_fee': balance.term_fee,
        'previous_arrears': balance.previous_arrears,
        'total_due': term_due,
        'amount_paid': balance.amount_paid,
        'balance': balance_owed,
        'running_credits': running_credits if running_credits > 0 else Decimal('0'),
    })

# Display like HTML table
print(f"{'Year':<6} {'T':<2} {'Fee':<10} {'Arrears':<10} {'Total Due':<12} {'Paid':<10} {'Balance':<10}")
print("-" * 80)

for item in payment_history:
    year = item['term'].academic_year
    term = item['term'].term
    fee = float(item['term_fee'])
    arrears = float(item['previous_arrears'])
    total_due = float(item['total_due'])
    paid = float(item['amount_paid'])
    balance = float(item['balance'])
    
    print(f"{year:<6} {term:<2} ${fee:<9.2f} ${arrears:<9.2f} ${total_due:<11.2f} ${paid:<9.2f} ${balance:<9.2f}")

# Summary statistics
print("\n" + "="*80)
print("SUMMARY CARDS (Dashboard)")
print("="*80)

total_ever_due = sum([Decimal(str(b['term_fee'])) for b in payment_history]) if payment_history else Decimal('0')

all_payments_raw = Payment.objects.filter(student=audrey)
total_ever_paid = all_payments_raw.aggregate(total=Sum('amount'))['total'] or Decimal('0')

overall_balance = total_ever_due - total_ever_paid
if overall_balance < 0:
    overall_balance = Decimal('0')

collection_rate = Decimal('0')
if total_ever_due > 0:
    collection_rate = (total_ever_paid / total_ever_due) * 100

print(f"\nTotal Ever Due:      ${total_ever_due}")
print(f"Total Paid:          ${total_ever_paid}")
print(f"Overall Balance:     ${overall_balance}")
print(f"Collection Rate:     {collection_rate:.1f}%")
print(f"Running Credits:     ${running_credits}")

print(f"\n\nTEMS DISPLAYED:")
term_count = len(set([b.term.academic_year for b in all_balances]))
print(f"Years shown: {term_count} years")
print(f"Terms shown: {len(all_balances)} terms")
print(f"Includes current term? {'Yes' if all_balances else 'No'}")

print(f"\n\nKEY VERIFICATIONS:")
print("-" * 80)

# Check 2028 Term 3
term_3_items = [b for b in payment_history if b['term'].academic_year == 2028 and b['term'].term == 3]
if term_3_items:
    t3 = term_3_items[0]
    print(f"2028 Term 3 arrears: ${t3['previous_arrears']} (should be $780.00) ✓" if t3['previous_arrears'] == 780 else f"2028 Term 3 arrears: ${t3['previous_arrears']} (WRONG, should be $780)")
    print(f"2028 Term 3 balance: ${t3['balance']} (should be $780.00) ✓" if t3['balance'] == 780 else f"2028 Term 3 balance: ${t3['balance']} (WRONG, should be $780)")

# Check 2030 not showing
has_2030 = any([b for b in payment_history if b['term'].academic_year == 2030])
print(f"2030 showing? {has_2030} (should be False) ✓" if not has_2030 else f"2030 showing? {has_2030} (WRONG, should not show)")

# Check final totals
expected_total_due = 1180
expected_total_paid = 300
expected_balance = 880
print(f"Total due: ${total_ever_due} (expected $1180) ✓" if total_ever_due == expected_total_due else f"Total due: ${total_ever_due} (WRONG)")
print(f"Total paid: ${total_ever_paid} (expected $300) ✓" if total_ever_paid == expected_total_paid else f"Total paid: ${total_ever_paid} (WRONG)")
print(f"Overall balance: ${overall_balance} (expected $880) ✓" if overall_balance == expected_balance else f"Overall balance: ${overall_balance} (WRONG)")

print("\n" + "="*80)
