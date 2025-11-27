#!/usr/bin/env python
"""
CRITICAL FIX: Recalculate all StudentBalance.amount_paid from actual Payment records

The issue: StudentBalance.amount_paid was being set via accumulation in update_balance(),
resulting in corrupted values. E.g., Anert's Term 2 shows amount_paid=$80 when actual 
payments in Term 2 = $0.

This script recalculates amount_paid for ALL students to match actual Payment records.

BEFORE:
  Anert Term 1: amount_paid=$150 (correct - 3 x $50)
  Anert Term 2: amount_paid=$80 (WRONG - should be $0, no payments in Term 2)

AFTER:
  Anert Term 1: amount_paid=$150 (unchanged)
  Anert Term 2: amount_paid=$0 (FIXED)
  Anert Overall Balance: $90 (fixed from showing $40 + $50 artifacts)
"""

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import StudentBalance, Payment, Student
from django.db.models import Sum
from decimal import Decimal

def fix_all_balances():
    """Recalculate amount_paid for all StudentBalance records from Payment records"""
    
    print("="*70)
    print("CRITICAL DATA FIX: Recalculate StudentBalance.amount_paid")
    print("="*70)
    print()
    
    # Get all balances
    all_balances = StudentBalance.objects.all().order_by('student__first_name', 'term__term')
    
    total_balances = all_balances.count()
    balances_fixed = 0
    total_correction = Decimal('0')
    
    print(f"Processing {total_balances} StudentBalance records...\n")
    
    for balance in all_balances:
        # Get actual total paid from Payment records
        actual_paid = Payment.objects.filter(
            student=balance.student,
            term=balance.term
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Compare to what's in the database
        if actual_paid != balance.amount_paid:
            correction = balance.amount_paid - actual_paid
            total_correction += correction
            balances_fixed += 1
            
            print(f"{balance.student.first_name} - Term {balance.term.term}:")
            print(f"  OLD amount_paid: ${balance.amount_paid}")
            print(f"  NEW amount_paid: ${actual_paid}")
            print(f"  Correction: ${correction} ({'overstated' if correction > 0 else 'understated'})")
            print()
            
            # Update the balance
            balance.amount_paid = actual_paid
            balance.save()
    
    print("="*70)
    print(f"SUMMARY:")
    print(f"  Total balances processed: {total_balances}")
    print(f"  Balances corrected: {balances_fixed}")
    print(f"  Total correction amount: ${total_correction}")
    print("="*70)
    print()
    
    if balances_fixed > 0:
        print("✓ Data corrected successfully!")
        print()
        print("Verification - showing all corrected balances:")
        print()
        
        for balance in StudentBalance.objects.all().order_by('student__first_name', 'term__term'):
            actual_paid = Payment.objects.filter(
                student=balance.student,
                term=balance.term
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            if actual_paid == balance.amount_paid:
                print(f"{balance.student.first_name} - Term {balance.term.term}: ${balance.amount_paid} (VERIFIED)")
            else:
                print(f"ERROR: {balance.student.first_name} - Term {balance.term.term}: DB=${balance.amount_paid} but should be ${actual_paid}")
    else:
        print("✓ All balances are already correct!")

if __name__ == '__main__':
    fix_all_balances()
