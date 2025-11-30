#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm, TermFee, StudentBalance, Student, AcademicYear
term_2027_1 = AcademicTerm.objects.filter(academic_year=2027, term=1).first()
print(f"Term 1 2027: {term_2027_1}")
if term_2027_1:
    print(f"  Is current: {term_2027_1.is_current}")
    term_fees = TermFee.objects.filter(term=term_2027_1)
    if term_fees.exists():
        print("  Term fees (flat fee for all grades):")
        for tf in term_fees:
            print(f"    ${tf.amount}")
    else:
        print("  NO FEES SET UP <<<<<<<<")
    
    balances = StudentBalance.objects.filter(term=term_2027_1)
    print(f"\nStudent balances for Term 1 2027:")
    if balances.exists():
        for balance in balances:
            print(f"  {balance.student.name}: ${balance.current_balance}")
    else:
        print("  NO BALANCES CREATED <<<<<<")
else:
    print("Term 1 2027 not found")
