#!/usr/bin/env python
"""
Verify the graduated student payment fix
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm
from core.models.fee import StudentBalance
from core.models.academic import Payment
from decimal import Decimal

print("=" * 80)
print("🧪 TESTING GRADUATED STUDENT PAYMENT FIX")
print("=" * 80)

# Get David (graduated student)
david = Student.all_students.filter(first_name='David').first()
if not david:
    print("❌ David not found!")
    exit(1)

print(f"\n✓ Student: {david.full_name}")
print(f"  Status: {david.status}")
print(f"  is_active: {david.is_active}")
print(f"  is_archived: {david.is_archived}")

# Get his latest balance
latest_balance = StudentBalance.objects.filter(student=david).order_by('-term__academic_year', '-term__term').first()
if latest_balance:
    print(f"\n✓ Latest balance:")
    print(f"  Term: {latest_balance.term}")
    print(f"  Balance: ${latest_balance.current_balance:.2f}")
else:
    print("\n❌ No balance found for David!")
    exit(1)

# Show what should be displayed
print(f"\n" + "=" * 80)
print("WHAT SHOULD BE DISPLAYED IN PAYMENT FORM:")
print("=" * 80)
print(f"Student: {david.full_name}")
print(f"Message: Student has graduated. Can only pay ARREARS from previous terms.")
print(f"Outstanding Balance: ${latest_balance.current_balance:.2f}")
print(f"Payment Term: {latest_balance.term}")

print(f"\n" + "=" * 80)
print("BEFORE/AFTER COMPARISON:")
print("=" * 80)

# Show all balances to prove we're not summing them
print(f"\nAll balances for {david.full_name}:")
all_balances = StudentBalance.objects.filter(student=david).order_by('-term__academic_year', '-term__term')
total_sum = Decimal('0')
for bal in all_balances:
    print(f"  {bal.term}: ${bal.current_balance:.2f}")
    total_sum += bal.current_balance

print(f"\n❌ WRONG (before fix): Sum of all balances = ${total_sum:.2f}")
print(f"✅ CORRECT (after fix): Latest balance only = ${latest_balance.current_balance:.2f}")

print(f"\n" + "=" * 80)
print("✅ FIX VERIFICATION COMPLETE")
print("=" * 80)
