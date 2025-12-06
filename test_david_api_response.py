#!/usr/bin/env python
"""Test what the student_payment_details_api returns for David"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.academic import AcademicTerm, Payment
from core.models.fee import StudentBalance
from decimal import Decimal
import json

# Find David
david = Student.objects.filter(first_name='David').first()
print(f"Testing student_payment_details_api for David")
print(f"{'='*60}")

current_term = AcademicTerm.get_current_term()
print(f"Current Term: {current_term}")

# Initialize balance for current term
balance = StudentBalance.initialize_term_balance(david, current_term)

print(f"\nDavid's Profile:")
print(f"  is_active: {david.is_active}")
print(f"  is_archived: {david.is_archived}")
print(f"  status: {david.status}")

if balance is None:
    print(f"\nNo balance for current term - David is graduated")
    latest_balance = StudentBalance.objects.filter(student=david).order_by('-term__academic_year', '-term__term').first()
    if latest_balance:
        print(f"Latest balance: {latest_balance}")
        print(f"  Current Balance: ${latest_balance.current_balance}")
        total_outstanding = float(latest_balance.current_balance)
    else:
        total_outstanding = Decimal('0')
    
    # This is what the API returns for graduated students
    response_data = {
        'student_name': david.get_full_name(),
        'is_graduated': True,
        'is_archived': False,
        'message': 'Student has graduated. Can only pay ARREARS from previous terms.',
        'total_arrears': total_outstanding,
        'term_fee': 0.0,
        'previous_arrears': total_outstanding,
        'arrears_remaining': total_outstanding,
        'term_fee_remaining': 0.0,
        'amount_paid': 0.0,
        'current_balance': total_outstanding,
        'total_outstanding': total_outstanding,
        'payment_priority': f'GRADUATED - Must pay ${total_outstanding:.2f} in ARREARS'
    }
else:
    # Active student response
    total_outstanding = float(balance.current_balance) if balance and balance.current_balance > 0 else Decimal('0')
    response_data = {
        'student_name': david.get_full_name(),
        'is_graduated': False,
        'is_archived': False,
        'term_fee': float(balance.term_fee),
        'previous_arrears': float(balance.previous_arrears),
        'arrears_remaining': float(balance.arrears_remaining),
        'term_fee_remaining': float(balance.term_fee_remaining),
        'amount_paid': float(balance.amount_paid),
        'current_balance': float(balance.current_balance),
        'total_outstanding': float(total_outstanding),
    }
    if total_outstanding > 0:
        response_data['payment_priority'] = f"${total_outstanding:.2f} total outstanding"
    else:
        response_data['payment_priority'] = "Fully paid"

print(f"\nAPI Response (what frontend sees):")
print(json.dumps(response_data, indent=2))

print(f"\nKey field - total_outstanding: ${response_data['total_outstanding']:.2f}")
print(f"This is the balance displayed to the user in payment form")
