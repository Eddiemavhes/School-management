#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, Payment

print("=" * 80)
print("ANALYZING ANNAH - DETAILED BREAKDOWN")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()

print(f"Student: {annah.first_name} {annah.surname}\n")

# Show all balances
balances = StudentBalance.objects.filter(student=annah).order_by('term__academic_year', 'term__term')
print(f"BALANCES ({balances.count()} terms):")
for b in balances:
    print(f"  {b.term}:")
    print(f"    term_fee: ${b.term_fee}")
    print(f"    previous_arrears: ${b.previous_arrears}")
    print(f"    amount_paid: ${b.amount_paid}")
    print(f"    current_balance: ${b.current_balance}")
print()

# Show all payments
payments = Payment.objects.filter(student=annah).order_by('payment_date')
print(f"PAYMENTS ({payments.count()} records):")
for p in payments:
    print(f"  {p.payment_date}: ${p.amount} for {p.term}")
print()

# Show overall balance
print(f"Overall Balance (latest term): ${annah.overall_balance}")
print()

# Analysis
print("=" * 80)
print("EXPECTED vs ACTUAL")
print("=" * 80)
print()

term1 = balances.filter(term__term=1).first()
term2 = balances.filter(term__term=2).first()

print(f"Term 1 (First Term 2026):")
print(f"  Fee: ${term1.term_fee}")
print(f"  Paid: ${term1.amount_paid}")
print(f"  Balance: ${term1.current_balance}")
print(f"  → Credit: -${abs(term1.current_balance)} (overpaid)")
print()

print(f"Term 2 (Second Term 2026):")
print(f"  Fee: ${term2.term_fee}")
print(f"  Paid So Far: ${term2.amount_paid}")
print(f"  Previous Arrears (Term 1 credit): ${term2.previous_arrears}")
print(f"  Current Balance: ${term2.current_balance}")
print()

print(f"EXPECTED (if Annah paid $100 for Term 2):")
print(f"  Term 2 Fee: $100")
print(f"  Term 2 Paid: $100")
print(f"  Term 2 Balance: $0")
print(f"  Plus Term 1 Credit: -$20")
print(f"  Overall: $0 + (-$20) = -$20")
print()

print(f"ACTUAL:")
print(f"  Overall Balance shown: ${annah.overall_balance}")
print()

if term2.amount_paid >= 100:
    print(f"✓ Annah HAS paid $100 for Term 2")
else:
    print(f"❌ Annah has only paid ${term2.amount_paid} for Term 2 (not $100)")

if annah.overall_balance == -20:
    print(f"✓ Overall balance is CORRECT: -$20")
else:
    print(f"❌ Overall balance is WRONG: shows ${annah.overall_balance}, should be -$20")
