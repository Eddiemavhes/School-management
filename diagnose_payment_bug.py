import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.fee import StudentBalance
from core.models.academic import Payment, AcademicTerm
from core.models.student import Student
from decimal import Decimal

carol = Student.objects.filter(first_name='Carol', surname='Cross').first()

if carol:
    print("\n" + "=" * 100)
    print("DIAGNOSING THE PAYMENT LOGIC BUG")
    print("=" * 100)
    
    # Simulate: Carol pays $100 in Term 3 when she owes $120 ($100 fee + $20 arrears)
    term3 = AcademicTerm.objects.get(academic_year=2026, term=3)
    balance_term3 = StudentBalance.objects.get(student=carol, term=term3)
    
    print(f"\nTERM 3 BEFORE PAYMENT:")
    print(f"  Term Fee: ${balance_term3.term_fee}")
    print(f"  Previous Arrears: ${balance_term3.previous_arrears}")
    print(f"  Total Due: ${balance_term3.total_due}")
    print(f"  Amount Paid: ${balance_term3.amount_paid}")
    print(f"  Current Balance: ${balance_term3.current_balance}")
    print(f"  Payment Status: {balance_term3.payment_status}")
    
    # Now check what the properties return
    print(f"\n  Detailed Property Breakdown:")
    print(f"    arrears_remaining: ${balance_term3.arrears_remaining}")
    print(f"    term_fee_remaining: ${balance_term3.term_fee_remaining}")
    
    # The issue: if previous_arrears > 0 and amount_paid covers it...
    print(f"\n  Logic Check:")
    print(f"    previous_arrears > 0? {balance_term3.previous_arrears > 0}")
    print(f"    amount_paid >= previous_arrears? {balance_term3.amount_paid >= balance_term3.previous_arrears}")
    
    # Check the formula for term_fee_remaining
    if balance_term3.previous_arrears > 0:
        amount_to_current_fee = max(0, balance_term3.amount_paid - balance_term3.previous_arrears)
        calc_term_fee_remaining = max(0, balance_term3.term_fee - amount_to_current_fee)
        print(f"\n  Term Fee Remaining Calculation (with positive arrears):")
        print(f"    amount_to_current_fee = max(0, {balance_term3.amount_paid} - {balance_term3.previous_arrears})")
        print(f"                          = max(0, {balance_term3.amount_paid - balance_term3.previous_arrears})")
        print(f"                          = {amount_to_current_fee}")
        print(f"    term_fee_remaining = max(0, {balance_term3.term_fee} - {amount_to_current_fee})")
        print(f"                       = max(0, {balance_term3.term_fee - amount_to_current_fee})")
        print(f"                       = {calc_term_fee_remaining}")
    
    print(f"\n  Current Status: {balance_term3.payment_status}")
    print(f"    Shows as PAID? {balance_term3.payment_status == 'PAID'}")
    print(f"    Current Balance: ${balance_term3.current_balance}")
    print(f"    Current Balance <= 0? {balance_term3.current_balance <= 0}")
