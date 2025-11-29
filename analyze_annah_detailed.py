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
print("ANNAH - DETAILED ANALYSIS (WITH PAYMENTS)")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()
current_term = AcademicTerm.objects.filter(is_current=True).first()

print(f"Current Term: {current_term}\n")

balances = StudentBalance.objects.filter(student=annah).order_by('term__academic_year', 'term__term')

print(f"TERM-BY-TERM BREAKDOWN:")
for b in balances:
    is_current = "← CURRENT" if b.term == current_term else ""
    
    print(f"\n{b.term} {is_current}")
    print(f"  Fee: ${b.term_fee}")
    print(f"  Arrears: ${b.previous_arrears}")
    print(f"  Paid: ${b.amount_paid}")
    print(f"  Balance: ${b.current_balance}")
    
    # Show payments for this term
    payments = Payment.objects.filter(student=annah, term=b.term)
    if payments.exists():
        print(f"  Payments:")
        for p in payments:
            print(f"    ${p.amount}")

print()
print("=" * 80)
print("EXPECTED CALCULATION FOR CURRENT TERM (Term 2 2027)")
print("=" * 80)
print()

term1_2027 = StudentBalance.objects.filter(student=annah, term__academic_year=2027, term__term=1).first()
term2_2027 = StudentBalance.objects.filter(student=annah, term__academic_year=2027, term__term=2).first()

if term1_2027:
    print(f"Term 1 2027 Final Balance: ${term1_2027.current_balance}")
    print(f"Term 2 2027 Previous Arrears: ${term2_2027.previous_arrears if term2_2027 else 'N/A'}")
    print()
    
    if term2_2027:
        print(f"Term 2 2027:")
        print(f"  Should have previous arrears = Term 1 balance = ${term1_2027.current_balance}")
        print(f"  Fee = $100")
        print(f"  Total Due = ${term1_2027.current_balance} + $100 = ${term1_2027.current_balance + 100}")
        print()
        print(f"If user says should be $80:")
        print(f"  That matches IF Term 1 balance was -$20!")
        print(f"  But Term 1 shows: ${term1_2027.current_balance}")
        
        print()
        print(f"Overall Balance (what's shown): ${annah.overall_balance}")
