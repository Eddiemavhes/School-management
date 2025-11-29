#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, Payment, AcademicTerm

print("=" * 80)
print("FINAL VERIFICATION - ANNAH")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()
current_term = AcademicTerm.objects.filter(is_current=True).first()

print(f"Student: {annah.first_name} {annah.surname}")
print(f"Current Term: {current_term}")
print()

balances = StudentBalance.objects.filter(student=annah).order_by('term__term')
print(f"TERM BREAKDOWN:")
for b in balances:
    is_current = "✓ CURRENT" if b.term == current_term else "  PAST/FUTURE"
    print(f"  {b.term} [{is_current}]:")
    print(f"    Fee: ${b.term_fee}, Arrears: ${b.previous_arrears}, Paid: ${b.amount_paid}")
    print(f"    Balance: ${b.current_balance}")
print()

payments = Payment.objects.filter(student=annah).order_by('payment_date')
print(f"PAYMENTS:")
total_paid = 0
for p in payments:
    print(f"  {p.payment_date}: ${p.amount} for {p.term}")
    total_paid += p.amount
print(f"  Total Paid: ${total_paid}")
print()

total_fees = sum(b.term_fee for b in balances)
print(f"SUMMARY:")
print(f"  Total Fees Charged: ${total_fees}")
print(f"  Total Paid: ${total_paid}")
print(f"  Credit/Arrears: ${total_paid - total_fees}")
print()

print(f"OVERALL BALANCE SHOWN: ${annah.overall_balance}")
print()

print("=" * 80)
print("EXPECTED vs ACTUAL")
print("=" * 80)
print()

# Current term calculation
current_term_balance = StudentBalance.objects.filter(student=annah, term=current_term).first()
if current_term_balance:
    print(f"✓ Current Term ({current_term}):")
    print(f"    Fee: ${current_term_balance.term_fee}")
    print(f"    Arrears from T1: ${current_term_balance.previous_arrears}")
    print(f"    Paid: ${current_term_balance.amount_paid}")
    print(f"    Balance: ${current_term_balance.current_balance}")
    print()
    
    if current_term_balance.current_balance == -20:
        print(f"✓✓✓ CORRECT! Annah's current term balance is -$20 (credit)")
    else:
        print(f"❌ WRONG! Current term balance should be -$20, got ${current_term_balance.current_balance}")
else:
    print(f"❌ No balance found for current term!")

print()
print(f"Overall Balance: ${annah.overall_balance}")
if annah.overall_balance == -20:
    print(f"✓✓✓ PERFECT! Overall balance matches current term (-$20 credit)")
else:
    print(f"❌ Overall balance mismatch!")
