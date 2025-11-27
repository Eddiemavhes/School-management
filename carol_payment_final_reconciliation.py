import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.fee import StudentBalance
from core.models.academic import Payment
from core.models.student import Student
from decimal import Decimal

carol = Student.objects.filter(first_name='Carol', surname='Cross').first()

if carol:
    print("\n" + "=" * 100)
    print(f"CAROL'S COMPLETE PAYMENT RECONCILIATION".center(100))
    print("=" * 100)
    
    balances = StudentBalance.objects.filter(student=carol).order_by('term__academic_year', 'term__term')
    
    running_total_owed = Decimal('0')
    running_total_paid = Decimal('0')
    
    for balance in balances:
        term = balance.term
        term_display = f"{term.get_term_display()} {term.academic_year}"
        
        payments = Payment.objects.filter(student=carol, term=term).order_by('payment_date')
        
        print(f"\n{term_display}")
        print("-" * 100)
        
        # Show individual payments
        if payments:
            print("  Payments Made:")
            for p in payments:
                print(f"    • ${p.amount:>7.2f} on {p.payment_date} (Ref: {p.reference_number})")
            total_term_payments = sum(p.amount for p in payments)
            print(f"  Total Paid This Term: ${total_term_payments:>7.2f}")
        else:
            total_term_payments = Decimal('0')
            print("  No payments made this term")
        
        print()
        print(f"  Financial Summary:")
        print(f"    Previous Term Arrears/Credit:        ${balance.previous_arrears:>10.2f}")
        print(f"    + This Term's Fee:                  +${balance.term_fee:>10.2f}")
        print(f"    " + "=" * 50)
        print(f"    = Total Due This Term:               ${balance.total_due:>10.2f}")
        print(f"    - Amount Carol Has Paid:            -${balance.amount_paid:>10.2f}")
        print(f"    " + "=" * 50)
        print(f"    = Carol Still Owes:                  ${balance.current_balance:>10.2f}")
        
        running_total_owed += balance.current_balance
        running_total_paid += balance.amount_paid
    
    print(f"\n" + "=" * 100)
    print(f"OVERALL SUMMARY".center(100))
    print("=" * 100)
    print(f"Total Amount Paid Across All Terms:     ${running_total_paid:>10.2f}")
    print(f"Total Amount Still Owed:                ${running_total_owed:>10.2f}")
    print(f"Total Fees (sum of all term fees):      ${sum(b.term_fee for b in balances):>10.2f}")
    print("=" * 100 + "\n")
