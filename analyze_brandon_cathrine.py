#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, Payment
from decimal import Decimal

print("=" * 80)
print("DEEP ANALYSIS - BRANDON AND CATHRINE PAYMENT LOGIC")
print("=" * 80)
print()

# BRANDON
print("BRANDON:")
print("-" * 80)
brandon = Student.objects.filter(first_name='Brandon').first()
if brandon:
    print(f"Name: {brandon.first_name} {brandon.surname}")
    print()
    
    # Payments
    payments = Payment.objects.filter(student=brandon).order_by('payment_date')
    print(f"Payments recorded:")
    total_paid = Decimal('0')
    for p in payments:
        total_paid += p.amount
        print(f"  {p.payment_date}: ${p.amount} for {p.term}")
    print(f"  TOTAL PAID: ${total_paid}")
    print()
    
    # Balances
    balances = StudentBalance.objects.filter(student=brandon).order_by('term__academic_year', 'term__term')
    print(f"Balance Records:")
    for b in balances:
        print(f"  {b.term}:")
        print(f"    Fee: ${b.term_fee}")
        print(f"    Arrears: ${b.previous_arrears}")
        print(f"    Total Due: ${b.total_due}")
        print(f"    Amount Paid: ${b.amount_paid}")
        print(f"    Balance: ${b.current_balance}")
        print()
    
    print(f"Overall Balance Shown: ${brandon.overall_balance}")
    print()
    print(f"ANALYSIS:")
    print(f"  You said: Brandon paid $100")
    print(f"  Term 1 fee: $100")
    print(f"  Expected: Balance should be $0")
    print(f"  Actual: Balance shows ${brandon.overall_balance}")
    
    if brandon.overall_balance == 0:
        print(f"  ✅ CORRECT")
    else:
        print(f"  ❌ WRONG - Why ${brandon.overall_balance}?")
    print()

print()
print()

# CATHRINE
print("CATHRINE:")
print("-" * 80)
cathrine = Student.objects.filter(first_name='Cathrine').first()
if cathrine:
    print(f"Name: {cathrine.first_name} {cathrine.surname}")
    print()
    
    # Payments
    payments = Payment.objects.filter(student=cathrine).order_by('payment_date')
    print(f"Payments recorded:")
    total_paid = Decimal('0')
    for p in payments:
        total_paid += p.amount
        print(f"  {p.payment_date}: ${p.amount} for {p.term}")
    print(f"  TOTAL PAID: ${total_paid}")
    print()
    
    # Balances
    balances = StudentBalance.objects.filter(student=cathrine).order_by('term__academic_year', 'term__term')
    print(f"Balance Records:")
    for b in balances:
        print(f"  {b.term}:")
        print(f"    Fee: ${b.term_fee}")
        print(f"    Arrears: ${b.previous_arrears}")
        print(f"    Total Due: ${b.total_due}")
        print(f"    Amount Paid: ${b.amount_paid}")
        print(f"    Balance: ${b.current_balance}")
        print()
    
    print(f"Overall Balance Shown: ${cathrine.overall_balance}")
    print()
    print(f"ANALYSIS:")
    print(f"  You said: Cathrine paid $60")
    print(f"  Term 1 fee: $100")
    print(f"  Expected: Balance should be $40 (still owes $40)")
    print(f"  Actual: Balance shows ${cathrine.overall_balance}")
    
    if cathrine.overall_balance == 40:
        print(f"  ✅ CORRECT")
    else:
        print(f"  ❌ WRONG - Why ${cathrine.overall_balance}?")
