#!/usr/bin/env python
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, Payment, Administrator
from django.utils import timezone

print("="*80)
print("TEST: PAYMENT RECORDING SYSTEM")
print("="*80)

# Get an admin to record the payment
admin = Administrator.objects.first()
if not admin:
    print("ERROR: No administrator found")
    exit(1)

david = Student.all_students.get(first_name='David')
current_term = StudentBalance.objects.filter(student=david).order_by('-term__academic_year', '-term__term').first()

if current_term:
    print(f"\nStudent: {david.first_name}")
    print(f"Current Term: {current_term.term}")
    print(f"Balance Before: ${current_term.current_balance:.2f}")
    
    # Create a payment
    print(f"\n>>> Recording payment of $100...")
    
    payment = Payment.objects.create(
        student=david,
        term=current_term.term,
        amount=Decimal('100'),
        payment_date=timezone.now().date(),
        reference_number=f"TEST-{timezone.now().timestamp()}",
        recorded_by=admin,
        payment_method='CASH'
    )
    
    print(f"Payment created: {payment.id}")
    
    # Refresh balance
    current_term.refresh_from_db()
    
    print(f"\nBalance After: ${current_term.current_balance:.2f}")
    print(f"Amount Paid: ${current_term.amount_paid:.2f}")
    
    # Verify
    print(f"\nVerification:")
    print(f"  Expected balance after $100 payment: 500")
    print(f"  Actual balance: ${current_term.current_balance:.2f}")
    
    if current_term.current_balance == 500:
        print("  Status: PAYMENT RECORDED CORRECTLY")
    else:
        print("  Status: PAYMENT NOT RECORDED CORRECTLY")
        
    # Check all payments
    all_payments = Payment.objects.filter(student=david)
    print(f"\nTotal payments for David: {all_payments.count()}")
else:
    print("ERROR: No balance found for David")
