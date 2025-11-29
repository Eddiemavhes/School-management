#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm, Payment

print("=" * 80)
print("ANALYZING ANNAH'S TERM 2 SITUATION")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()

print(f"Student: {annah.first_name} {annah.surname}")
print()

# Check current term
current_term = AcademicTerm.objects.filter(is_current=True).first()
print(f"Current Term: {current_term}")
print(f"Current Term is_current: {current_term.is_current}")
print()

# Show all balances
balances = StudentBalance.objects.filter(student=annah).order_by('term__academic_year', 'term__term')
print(f"ALL BALANCES: {balances.count()} records")
print()

for b in balances:
    print(f"  Term: {b.term} (academic_year={b.term.academic_year}, term={b.term.term}, is_current={b.term.is_current})")
    print(f"    Term Fee: ${b.term_fee}")
    print(f"    Amount Paid: ${b.amount_paid}")
    print(f"    Previous Arrears: ${b.previous_arrears}")
    print(f"    Current Balance: ${b.current_balance}")
    print()

# Show overall balance
print(f"Overall Balance: ${annah.overall_balance}")
print()

# Show payments
payments = Payment.objects.filter(student=annah).order_by('payment_date')
print(f"PAYMENTS: {payments.count()} records")
for p in payments:
    print(f"  {p.payment_date}: ${p.amount} for {p.term}")
print()

# Analysis
print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print()

term1 = StudentBalance.objects.filter(student=annah, term__academic_year=2026, term__term=1).first()
term2 = StudentBalance.objects.filter(student=annah, term__academic_year=2026, term__term=2).first()

if term1:
    print(f"Term 1 Final Balance: ${term1.current_balance}")
    if term1.current_balance < 0:
        print(f"  → This is a CREDIT (overpayment)")

if term2:
    print(f"Term 2 Exists: YES")
    print(f"  Term 2 Fee: ${term2.term_fee}")
    print(f"  Term 2 Previous Arrears: ${term2.previous_arrears}")
    print(f"  Term 2 Current Balance: ${term2.current_balance}")
    print()
    print(f"EXPECTED CALCULATION:")
    print(f"  Term 1 Credit: -$20 (from previous balance)")
    print(f"  Term 2 Fee: $100")
    print(f"  Expected Outstanding: $100 - $20 = $80")
    print()
    if term2.current_balance == 80:
        print(f"  ✓ CORRECT")
    else:
        print(f"  ❌ WRONG: Shows ${term2.current_balance} instead of $80")
else:
    print(f"Term 2 Exists: NO (not yet created)")
