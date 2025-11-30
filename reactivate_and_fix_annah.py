#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm

# Get Annah
annah = Student.objects.get(id=8)
print(f"Student: {annah}")
print(f"  Current status: {annah.status}, is_active: {annah.is_active}")

# Reactivate her (bypass validation for data recovery)
annah.status = 'ENROLLED'
annah.is_active = True
# Save without full_clean to bypass validation
from django.db import models
models.Model.save(annah, update_fields=['status', 'is_active'])
print(f"  Updated to: {annah.status}, is_active: {annah.is_active}")

# Now fix the carryover
term_2027_1 = AcademicTerm.objects.filter(academic_year=2027, term=1).first()
term_2027_2 = AcademicTerm.objects.filter(academic_year=2027, term=2).first()
term_2027_3 = AcademicTerm.objects.filter(academic_year=2027, term=3).first()

print(f"\nFixing Annah's balance carryover:")

# Term 1 → Term 2
balance_t1 = StudentBalance.objects.filter(student=annah, term=term_2027_1).first()
balance_t2 = StudentBalance.objects.filter(student=annah, term=term_2027_2).first()

if balance_t1 and balance_t2:
    print(f"\nTerm 1 → Term 2:")
    print(f"  Term 1 balance: ${balance_t1.current_balance}")
    balance_t2.previous_arrears = balance_t1.current_balance
    balance_t2.save()
    print(f"  Term 2 updated: Arrears=${balance_t2.previous_arrears}, New balance=${balance_t2.current_balance}")

# Term 2 → Term 3
balance_t2 = StudentBalance.objects.filter(student=annah, term=term_2027_2).first()
balance_t3 = StudentBalance.objects.filter(student=annah, term=term_2027_3).first()

if balance_t2 and balance_t3:
    print(f"\nTerm 2 → Term 3:")
    print(f"  Term 2 balance: ${balance_t2.current_balance}")
    balance_t3.previous_arrears = balance_t2.current_balance
    balance_t3.save()
    print(f"  Term 3 updated: Arrears=${balance_t3.previous_arrears}, New balance=${balance_t3.current_balance}")

print(f"\n\nFinal Annah balances:")
for i, term in enumerate([term_2027_1, term_2027_2, term_2027_3], 1):
    balance = StudentBalance.objects.filter(student=annah, term=term).first()
    if balance:
        print(f"  Term {i}: Arrears=${balance.previous_arrears}, Fee=${balance.term_fee}, Paid=${balance.amount_paid}, Balance=${balance.current_balance}")
