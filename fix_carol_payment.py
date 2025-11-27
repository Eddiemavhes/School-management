import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.fee import StudentBalance
from core.models.academic import Payment, AcademicTerm
from core.models.student import Student
from decimal import Decimal

# Find Carol's records
carol_student = Student.objects.filter(first_name='Carol', surname='Cross').first()

if carol_student:
    print("=" * 80)
    print("FIX: CORRECTING CAROL'S AMOUNT_PAID")
    print("=" * 80)
    
    balances = StudentBalance.objects.filter(student=carol_student).order_by('term__academic_year', 'term__term')
    
    for balance in balances:
        term = balance.term
        term_display = f"{term.get_term_display()} {term.academic_year}"
        
        # Get actual payments for this term
        payments = Payment.objects.filter(student=carol_student, term=term)
        actual_paid = sum(p.amount for p in payments)
        
        print(f"\n{term_display}")
        print(f"  DB amount_paid: ${balance.amount_paid}")
        print(f"  Actual payments sum: ${actual_paid}")
        
        if actual_paid != balance.amount_paid:
            print(f"  ❌ MISMATCH - Fixing...")
            balance.amount_paid = actual_paid
            balance.save(update_fields=['amount_paid'])
            print(f"  ✓ FIXED - Now: ${balance.amount_paid}")
        else:
            print(f"  ✓ OK - Matches")
    
    print("\n" + "=" * 80)
    print("VERIFICATION AFTER FIX")
    print("=" * 80)
    
    # Refresh and display
    balances = StudentBalance.objects.filter(student=carol_student).order_by('term__academic_year', 'term__term')
    
    for balance in balances:
        term = balance.term
        term_display = f"{term.get_term_display()} {term.academic_year}"
        print(f"\n{term_display}")
        print(f"  Term Fee: ${balance.term_fee}")
        print(f"  Previous Arrears: ${balance.previous_arrears}")
        print(f"  Total Due: ${balance.total_due}")
        print(f"  Amount Paid: ${balance.amount_paid}")
        print(f"  Current Balance: ${balance.current_balance}")
