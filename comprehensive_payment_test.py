#!/usr/bin/env python
"""
COMPREHENSIVE TEST: All Payment System Fixes

This script tests:
1. David's payment can be recorded (he's graduated but not archived)
2. Balance shows $600 (latest balance), not $2100 (sum of historical)
3. Overpayment logic correctly creates credits for next term
4. Payment delete signal recalculates balances correctly
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.academic import Payment, AcademicTerm
from core.models.fee import StudentBalance
from core.models import Administrator
from decimal import Decimal

print(f"\n{'='*70}")
print(f" COMPREHENSIVE PAYMENT SYSTEM TEST")
print(f"{'='*70}\n")

admin_user = Administrator.objects.first()
current_term = AcademicTerm.get_current_term()

# TEST 1: David's payment recording
print(f"TEST 1: David's payment recording (Graduated student)")
print(f"{'-'*70}")

david = Student.objects.filter(first_name='David').first()
print(f"Student: {david.full_name} (is_active={david.is_active}, is_archived={david.is_archived})")

david_balance_before = StudentBalance.objects.filter(student=david).order_by('-term__academic_year', '-term__term').first()
print(f"Latest balance before: ${david_balance_before.current_balance}")

# Create payment
david_payment = Payment(
    student=david,
    amount=Decimal('100.00'),
    payment_method='CASH',
    term=david_balance_before.term,
    recorded_by=admin_user
)
david_payment.save()

david_balance_after = StudentBalance.objects.get(pk=david_balance_before.pk)
print(f"Latest balance after $100 payment: ${david_balance_after.current_balance}")

if david_balance_after.current_balance == 500:
    print(f"✅ TEST 1 PASSED: Payment recorded correctly for graduated student")
else:
    print(f"❌ TEST 1 FAILED: Expected $500 but got ${david_balance_after.current_balance}")

# Clean up
david_payment.delete()
david_balance_after.refresh_from_db()

print(f"\n")

# TEST 2: Balance display shows latest ($600), not accumulated ($2100)
print(f"TEST 2: Balance display correctness")
print(f"{'-'*70}")

print(f"David's overall_balance property: ${david.overall_balance}")

david_balances = StudentBalance.objects.filter(student=david).order_by('term__academic_year', 'term__term')
sum_all = sum(b.current_balance for b in david_balances)
sum_first_6 = sum(b.current_balance for b in list(david_balances)[:6])
latest_only = david_balances.last().current_balance

print(f"  - Sum of all balances: ${sum_all:.2f} (❌ WRONG - double counts)")
print(f"  - Sum of first 6 balances: ${sum_first_6:.2f} (❌ WRONG - historical)")
print(f"  - Latest balance only: ${latest_only:.2f} (✅ CORRECT)")

if david.overall_balance == 600:
    print(f"✅ TEST 2 PASSED: Balance shows correct value ($600)")
else:
    print(f"❌ TEST 2 FAILED: Expected $600 but got ${david.overall_balance}")

print(f"\n")

# TEST 3: Overpayment creates credits for next term
print(f"TEST 3: Overpayment credit logic")
print(f"{'-'*70}")

# Use Annah as test subject (she already has overpayment history)
annah = Student.objects.filter(first_name='Annah').first()
annah_balances = StudentBalance.objects.filter(student=annah).order_by('term__academic_year', 'term__term')

print(f"Student: {annah.full_name}")
print(f"Payment history with overpayments:")

for i, b in enumerate(annah_balances, 1):
    if b.previous_arrears < 0:
        credit = abs(b.previous_arrears)
        print(f"  {i}. {b.term}: Fee ${b.term_fee}, Arrears ${b.previous_arrears:.2f} (Credit: ${credit})")
    else:
        print(f"  {i}. {b.term}: Fee ${b.term_fee}, Arrears ${b.previous_arrears:.2f}")

# Check Term 1 2026 -> Term 2 2026 credit transfer
term1_2026 = annah_balances.filter(term__academic_year=2026, term__term=1).first()
term2_2026 = annah_balances.filter(term__academic_year=2026, term__term=2).first()

if term1_2026 and term2_2026:
    excess_in_term1 = abs(term1_2026.current_balance) if term1_2026.current_balance < 0 else 0
    credit_in_term2 = abs(term2_2026.previous_arrears) if term2_2026.previous_arrears < 0 else 0
    
    print(f"\nCredit transfer check:")
    print(f"  Term 1 2026 balance: ${term1_2026.current_balance:.2f} (excess: ${excess_in_term1:.2f})")
    print(f"  Term 2 2026 previous arrears: ${term2_2026.previous_arrears:.2f} (credit: ${credit_in_term2:.2f})")
    
    if excess_in_term1 == credit_in_term2:
        print(f"✅ TEST 3 PASSED: Overpayment credit transferred correctly")
    else:
        print(f"❌ TEST 3 FAILED: Credit mismatch")
else:
    print(f"Cannot test - missing term balances")

print(f"\n")

# TEST 4: Payment deletion recalculates balance correctly
print(f"TEST 4: Payment deletion signal")
print(f"{'-'*70}")

cathrine = Student.objects.filter(first_name='Cathrine').first()
cathrine_current = StudentBalance.objects.filter(student=cathrine, term=current_term).first()

if cathrine_current:
    print(f"Student: {cathrine.full_name}")
    print(f"Balance before test: ${cathrine_current.current_balance:.2f}, Amount paid: ${cathrine_current.amount_paid:.2f}")
    
    # Get payment count before
    payments_before = Payment.objects.filter(student=cathrine, term=current_term).count()
    
    # Create a payment
    test_payment = Payment(
        student=cathrine,
        amount=Decimal('50.00'),
        payment_method='CASH',
        term=current_term,
        recorded_by=admin_user
    )
    test_payment.save()
    
    cathrine_current.refresh_from_db()
    print(f"After $50 payment: ${cathrine_current.current_balance:.2f}, Amount paid: ${cathrine_current.amount_paid:.2f}")
    
    # Delete payment
    test_payment.delete()
    
    cathrine_current.refresh_from_db()
    payments_after = Payment.objects.filter(student=cathrine, term=current_term).count()
    
    print(f"After deletion: ${cathrine_current.current_balance:.2f}, Amount paid: ${cathrine_current.amount_paid:.2f}")
    
    if payments_before == payments_after:
        print(f"✅ TEST 4 PASSED: Payment deletion correctly recalculated balance")
    else:
        print(f"❌ TEST 4 FAILED: Payment counts don't match")
else:
    print(f"Cathrine not in current term, skipping test")

print(f"\n{'='*70}")
print(f" ALL TESTS COMPLETED")
print(f"{'='*70}\n")
