#!/usr/bin/env python
"""Test overpayment logic"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.academic import Payment, AcademicTerm
from core.models.fee import StudentBalance, TermFee
from core.models import Administrator
from decimal import Decimal

# Create a test student (use an existing one to avoid conflicts)
test_student = Student.objects.filter(first_name='Annah').first()
admin_user = Administrator.objects.first()

print(f"{'='*60}")
print(f"TEST: Overpayment Credit Logic")
print(f"{'='*60}")
print(f"Test Student: {test_student.full_name}")

# Get current term and next term
current_term = AcademicTerm.get_current_term()
print(f"\nCurrent Term: {current_term}")

# Get this student's balances
balances = StudentBalance.objects.filter(student=test_student).order_by('term__academic_year', 'term__term')
print(f"\n{test_student.full_name}'s current balance situation:")
for bal in balances:
    print(f"  {bal.term}: Fee ${bal.term_fee}, Arrears ${bal.previous_arrears}, Paid ${bal.amount_paid}, Balance ${bal.current_balance}")

# Let's test overpayment on the current term
current_balance = StudentBalance.objects.filter(student=test_student, term=current_term).first()
if current_balance:
    print(f"\nTesting overpayment in current term ({current_term}):")
    print(f"  Current balance: ${current_balance.current_balance}")
    print(f"  Overpayment amount needed to test: ${current_balance.current_balance + 100}")
    
    # Create an overpayment
    overpayment = Payment(
        student=test_student,
        amount=Decimal(str(current_balance.current_balance + 100)),
        payment_method='CASH',
        term=current_term,
        recorded_by=admin_user
    )
    overpayment.save()
    
    # Refresh balances
    current_balance.refresh_from_db()
    
    print(f"\n  After overpayment:")
    print(f"    Current balance: ${current_balance.current_balance}")
    print(f"    Amount paid: ${current_balance.amount_paid}")
    
    if current_balance.current_balance < 0:
        print(f"    ✅ Overpayment detected (balance is negative)")
        excess = abs(current_balance.current_balance)
        print(f"    Excess amount: ${excess}")
    else:
        print(f"    ❌ No overpayment (balance should be negative)")
    
    # Check if next term has been created with credit
    next_terms = AcademicTerm.objects.filter(
        academic_year=current_term.academic_year,
        term__gt=current_term.term
    ).order_by('term')
    
    if next_terms.exists():
        next_term = next_terms.first()
        next_balance = StudentBalance.objects.filter(student=test_student, term=next_term).first()
        if next_balance:
            print(f"\n  Next term ({next_term}):")
            print(f"    Previous arrears: ${next_balance.previous_arrears}")
            print(f"    (Should be negative ${-excess} if credit was applied)")
        else:
            print(f"\n  Next term ({next_term}): No balance record created yet")
    
    # Clean up
    overpayment.delete()
    current_balance.refresh_from_db()
    print(f"\n✅ Test payment deleted, balance restored to: ${current_balance.current_balance}")
else:
    print(f"No balance for current term")
