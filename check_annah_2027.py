#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm, StudentBalance, Student, Payment

# Get Annah
annah = Student.objects.filter(surname='A').first()
print(f"Student: {annah}")

# Get all terms for 2027
terms_2027 = AcademicTerm.objects.filter(academic_year=2027).order_by('term')
print(f"\nTerms in 2027:")
for term in terms_2027:
    print(f"  {term} (current: {term.is_current})")

# Check Annah's balances and payments for each term
print(f"\nAnna's balances for 2027:")
for term in terms_2027:
    balance = StudentBalance.objects.filter(student=annah, term=term).first()
    if balance:
        print(f"\n{term}:")
        print(f"  Term fee: ${balance.term_fee}")
        print(f"  Previous arrears: ${balance.previous_arrears}")
        print(f"  Amount paid: ${balance.amount_paid}")
        print(f"  Total due: ${balance.total_due}")
        print(f"  Current balance (outstanding): ${balance.current_balance}")
        
        # Get payments for this term
        payments = Payment.objects.filter(student=annah, term=term)
        if payments.exists():
            print(f"  Payments:")
            for payment in payments:
                print(f"    - ${payment.amount} on {payment.payment_date}")
