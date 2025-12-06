#!/usr/bin/env python
"""Verify the payment signal is working correctly"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.academic import Payment
from core.models.fee import StudentBalance

# Find David
david = Student.objects.filter(first_name='David').first()

# Get David's latest balance
latest_balance = StudentBalance.objects.filter(student=david).order_by('-term__academic_year', '-term__term').first()
print(f"David's latest balance before any changes:")
print(f"  Term: {latest_balance.term}")
print(f"  Amount Paid (in DB): ${latest_balance.amount_paid}")
print(f"  Current Balance: ${latest_balance.current_balance}")

# Count payments for this balance
payment_count = Payment.objects.filter(student=david, term=latest_balance.term).count()
total_paid_from_payments = sum(p.amount for p in Payment.objects.filter(student=david, term=latest_balance.term))

print(f"\nPayments for this term:")
print(f"  Count: {payment_count}")
print(f"  Total from payments: ${total_paid_from_payments}")

if payment_count > 0:
    for p in Payment.objects.filter(student=david, term=latest_balance.term):
        print(f"  - Payment {p.pk}: ${p.amount} on {p.payment_date}")
