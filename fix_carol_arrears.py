import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.fee import StudentBalance
from core.models.academic import AcademicTerm
from core.models.student import Student
from decimal import Decimal

# Find Carol's records
carol_student = Student.objects.filter(first_name='Carol', surname='Cross').first()

if carol_student:
    print("=" * 80)
    print("FIX: CORRECTING ARREARS CARRYOVER")
    print("=" * 80)
    
    balances = StudentBalance.objects.filter(student=carol_student).order_by('term__academic_year', 'term__term')
    balances_list = list(balances)
    
    for i, balance in enumerate(balances_list):
        term = balance.term
        term_display = f"{term.get_term_display()} {term.academic_year}"
        
        if i == 0:
            # First term should have 0 arrears
            calculated_arrears = Decimal('0')
        else:
            # Get previous term balance
            prev_balance = balances_list[i-1]
            calculated_arrears = prev_balance.current_balance
        
        print(f"\n{term_display}")
        print(f"  DB previous_arrears: ${balance.previous_arrears}")
        print(f"  Calculated previous_arrears: ${calculated_arrears}")
        
        if calculated_arrears != balance.previous_arrears:
            print(f"  ❌ MISMATCH - Fixing...")
            balance.previous_arrears = calculated_arrears
            balance.save(update_fields=['previous_arrears'])
            print(f"  ✓ FIXED - Now: ${balance.previous_arrears}")
        else:
            print(f"  ✓ OK - Matches")
    
    print("\n" + "=" * 80)
    print("FINAL VERIFICATION")
    print("=" * 80)
    
    # Refresh and display
    balances = StudentBalance.objects.filter(student=carol_student).order_by('term__academic_year', 'term__term')
    
    total_arrears = Decimal('0')
    for balance in balances:
        term = balance.term
        term_display = f"{term.get_term_display()} {term.academic_year}"
        print(f"\n{term_display}")
        print(f"  Term Fee: ${balance.term_fee}")
        print(f"  Previous Arrears: ${balance.previous_arrears}")
        print(f"  Total Due: ${balance.total_due}")
        print(f"  Amount Paid: ${balance.amount_paid}")
        print(f"  Current Balance: ${balance.current_balance}")
        
        if balance.current_balance > 0:
            total_arrears += balance.current_balance
    
    print(f"\n" + "=" * 80)
    print(f"TOTAL OUTSTANDING ARREARS: ${total_arrears}")
    print("=" * 80)
