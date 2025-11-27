import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.fee import StudentBalance
from core.models.academic import Payment
from core.models.student import Student

# Find Carol's records
carol_student = Student.objects.filter(first_name='Carol', surname='Cross').first()

if carol_student:
    print("=" * 80)
    print(f"CAROL PAYMENT ISSUE ANALYSIS")
    print("=" * 80)
    
    print(f"\nStudent: {carol_student.first_name} {carol_student.surname} (ID: {carol_student.id})")
    
    # Get all balances ordered by term
    balances = StudentBalance.objects.filter(student=carol_student).order_by('term__academic_year', 'term__term')
    
    print("\n" + "=" * 80)
    print("TERM-BY-TERM BREAKDOWN")
    print("=" * 80)
    
    cumulative_balance = 0
    for i, balance in enumerate(balances, 1):
        term_display = f"{balance.term.get_term_display()} {balance.term.academic_year}"
        print(f"\n{i}. {term_display}")
        print(f"   Term Fee: ${balance.term_fee}")
        print(f"   Previous Arrears: ${balance.previous_arrears}")
        print(f"   Total Due This Term: ${balance.total_due}")
        print(f"   Amount Paid (in DB): ${balance.amount_paid}")
        print(f"   Current Balance: ${balance.current_balance}")
        print(f"   Arrears Remaining: ${balance.arrears_remaining}")
        print(f"   Term Fee Remaining: ${balance.term_fee_remaining}")
        
        # Get payments for this term
        term_payments = Payment.objects.filter(student=carol_student, term=balance.term)
        actual_paid = sum(p.amount for p in term_payments)
        print(f"\n   Actual Payments for this Term: ${actual_paid}")
        for p in term_payments:
            print(f"      - ${p.amount} on {p.payment_date} (Ref: {p.reference_number})")
    
    print("\n" + "=" * 80)
    print("MISMATCH ANALYSIS")
    print("=" * 80)
    
    for balance in balances:
        term_display = f"{balance.term.get_term_display()} {balance.term.academic_year}"
        term_payments = Payment.objects.filter(student=carol_student, term=balance.term)
        actual_paid = sum(p.amount for p in term_payments)
        
        if actual_paid != balance.amount_paid:
            print(f"\n⚠️  MISMATCH in {term_display}")
            print(f"   Database says: ${balance.amount_paid}")
            print(f"   Sum of payments: ${actual_paid}")
            print(f"   Difference: ${balance.amount_paid - actual_paid}")
