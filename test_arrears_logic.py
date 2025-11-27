import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.fee import StudentBalance
from core.models.academic import Payment, AcademicTerm
from core.models.student import Student
from decimal import Decimal
from django.utils import timezone

# Find Carol
carol = Student.objects.filter(first_name='Carol', surname='Cross').first()
term3 = AcademicTerm.objects.get(academic_year=2026, term=3)

print("\n" + "=" * 100)
print("TESTING: Does Payment Recording Update Balance Correctly When Arrears Exist?")
print("=" * 100)

# Get current state
balance_term3 = StudentBalance.objects.get(student=carol, term=term3)
print(f"\nBEFORE: Term 3")
print(f"  previous_arrears: ${balance_term3.previous_arrears}")
print(f"  term_fee: ${balance_term3.term_fee}")
print(f"  total_due: ${balance_term3.total_due}")
print(f"  amount_paid: ${balance_term3.amount_paid}")
print(f"  current_balance: ${balance_term3.current_balance}")
print(f"  Marked as PAID? {balance_term3.current_balance <= 0}")

# Now simulate that Carol just paid $100 for Term 3
# (The system will see amount_paid = $100, but arrears = $20 should still be there)

print(f"\n\nNow... what if we look at the payment_status property?")
print(f"  payment_status = {balance_term3.payment_status}")

print(f"\n\nNow let's check the arrears and fee remaining properties:")
print(f"  arrears_remaining: ${balance_term3.arrears_remaining}")
print(f"  term_fee_remaining: ${balance_term3.term_fee_remaining}")

# The issue: if previous_arrears > 0, the formula is:
# arrears_remaining = max(0, previous_arrears - amount_paid) 
# But this is WRONG when amount_paid only covers the term_fee!

print(f"\n\nLet me trace the logic:")
print(f"  previous_arrears = ${balance_term3.previous_arrears} (positive = money owed)")
print(f"  amount_paid = ${balance_term3.amount_paid}")

if balance_term3.previous_arrears > 0:
    print(f"  Since previous_arrears > 0:")
    print(f"    The first ${balance_term3.previous_arrears} of payment should go to arrears")
    print(f"    Then remaining goes to term_fee")
    
    # What the property does:
    arrears_paid = min(balance_term3.amount_paid, balance_term3.previous_arrears)
    print(f"\n  Calculation in 'arrears_remaining' property:")
    print(f"    arrears_paid = min({balance_term3.amount_paid}, {balance_term3.previous_arrears}) = ${arrears_paid}")
    print(f"    arrears_remaining = ${balance_term3.previous_arrears} - ${arrears_paid} = ${balance_term3.previous_arrears - arrears_paid}")
    print(f"    BUT the property returns: ${balance_term3.arrears_remaining}")
    
    # What should be true:
    print(f"\n  ISSUE DETECTED:")
    print(f"    Property says arrears_remaining = ${balance_term3.arrears_remaining}")
    print(f"    But it should be ${balance_term3.previous_arrears} - min({balance_term3.amount_paid}, {balance_term3.previous_arrears})")
    print(f"                    = ${balance_term3.previous_arrears} - ${min(balance_term3.amount_paid, balance_term3.previous_arrears)}")
    print(f"                    = ${max(0, balance_term3.previous_arrears - balance_term3.amount_paid)}")
