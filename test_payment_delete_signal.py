#!/usr/bin/env python
"""Test that the payment delete signal works correctly"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.academic import Payment
from core.models.fee import StudentBalance
from core.models import Administrator
from decimal import Decimal

# Find David
david = Student.objects.filter(first_name='David').first()
admin_user = Administrator.objects.first()

# Get David's latest balance
latest_balance = StudentBalance.objects.filter(student=david).order_by('-term__academic_year', '-term__term').first()

print(f"{'='*60}")
print(f"TEST: Payment Delete Signal")
print(f"{'='*60}")
print(f"\nBEFORE creating payment:")
print(f"  Amount Paid: ${latest_balance.amount_paid}")
print(f"  Current Balance: ${latest_balance.current_balance}")
print(f"  Payments for this term: {Payment.objects.filter(student=david, term=latest_balance.term).count()}")

# Create a test payment
payment = Payment(
    student=david,
    amount=Decimal('100.00'),
    payment_method='CASH',
    term=latest_balance.term,
    recorded_by=admin_user
)
payment.save()

# Refresh balance
latest_balance.refresh_from_db()

print(f"\nAFTER creating $100 payment:")
print(f"  Amount Paid: ${latest_balance.amount_paid}")
print(f"  Current Balance: ${latest_balance.current_balance}")
print(f"  Payments for this term: {Payment.objects.filter(student=david, term=latest_balance.term).count()}")

# Delete the payment
payment.delete()

# Refresh balance again
latest_balance.refresh_from_db()

print(f"\nAFTER deleting payment:")
print(f"  Amount Paid: ${latest_balance.amount_paid}")
print(f"  Current Balance: ${latest_balance.current_balance}")
print(f"  Payments for this term: {Payment.objects.filter(student=david, term=latest_balance.term).count()}")

if latest_balance.amount_paid == 0:
    print(f"\n✅ Payment delete signal working correctly!")
else:
    print(f"\n❌ BUG: Amount paid should be $0, but is ${latest_balance.amount_paid}")
