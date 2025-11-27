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
    print("TRACING THE BALANCE CALCULATION ISSUE")
    print("=" * 80)
    
    balances = StudentBalance.objects.filter(student=carol_student).order_by('term__academic_year', 'term__term')
    
    for i, balance in enumerate(balances, 1):
        term = balance.term
        term_display = f"{term.get_term_display()} {term.academic_year}"
        print(f"\n{i}. {term_display}")
        print(f"   Term Fee: ${balance.term_fee}")
        print(f"   Previous Arrears (in DB): ${balance.previous_arrears}")
        
        # Manually calculate what previous arrears SHOULD be
        calculated_arrears = StudentBalance.calculate_arrears(carol_student, term)
        print(f"   Previous Arrears (calculated): ${calculated_arrears}")
        
        # Get actual payments
        payments = Payment.objects.filter(student=carol_student, term=term)
        actual_paid = sum(p.amount for p in payments)
        print(f"   Actual Payments: ${actual_paid}")
        print(f"   Amount Paid (in DB): ${balance.amount_paid}")
        
        # Calculate what it should be
        total_due = balance.term_fee + balance.previous_arrears
        current_balance = total_due - balance.amount_paid
        print(f"   Total Due: ${total_due}")
        print(f"   Current Balance (in DB): ${current_balance}")
        
        # Get the previous term balance
        if i > 1:
            prev_balance = balances[i-2]
            print(f"\n   Previous Term Balance (Term {i-1}):")
            print(f"      Current Balance: ${prev_balance.current_balance}")
