#!/usr/bin/env python
"""Test if David can now make a payment"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.academic import Payment, AcademicTerm
from core.models.fee import StudentBalance
from core.models import Administrator
from decimal import Decimal

# Find David
david = Student.objects.filter(first_name='David').first()
current_term = AcademicTerm.get_current_term()
admin_user = Administrator.objects.first()  # Get any admin user

print(f"{'='*60}")
print(f"TEST 1: Create a payment for David (graduated student)")
print(f"{'='*60}")
print(f"David is_active: {david.is_active}")
print(f"David is_archived: {david.is_archived}")
print(f"David status: {david.status}")

# Find David's latest balance
latest_balance = StudentBalance.objects.filter(student=david).order_by('-term__academic_year', '-term__term').first()
print(f"\nDavid's latest balance:")
print(f"  Term: {latest_balance.term}")
print(f"  Current Balance: ${latest_balance.current_balance}")

# Try to create a payment for David
try:
    print(f"\nCreating payment of $100 for David...")
    payment = Payment(
        student=david,
        amount=Decimal('100.00'),
        payment_method='CASH',
        term=latest_balance.term,  # Use his latest balance term
        recorded_by=admin_user
    )
    payment.save()
    print(f"✅ Payment created successfully!")
    print(f"  Payment ID: {payment.pk}")
    print(f"  Payment Amount: ${payment.amount}")
    print(f"  Payment Term: {payment.term}")
    
    # Check if balance updated
    updated_balance = StudentBalance.objects.get(student=david, term=latest_balance.term)
    print(f"\n✅ Balance updated:")
    print(f"  Amount Paid: ${updated_balance.amount_paid}")
    print(f"  Current Balance: ${updated_balance.current_balance}")
    print(f"  Outstanding: ${updated_balance.current_balance:.2f}")
    
    # Verify payment is in database
    saved_payment = Payment.objects.get(pk=payment.pk)
    print(f"\n✅ Payment verified in database:")
    print(f"  Found: {saved_payment}")
    print(f"  Amount: ${saved_payment.amount}")
    
    # Clean up test payment
    payment.delete()
    print(f"\n✅ Test payment deleted")
    
    # Refresh balance after deletion
    refreshed_balance = StudentBalance.objects.get(student=david, term=latest_balance.term)
    print(f"\n✅ Balance after payment deletion:")
    print(f"  Amount Paid: ${refreshed_balance.amount_paid}")
    print(f"  Current Balance: ${refreshed_balance.current_balance}")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
