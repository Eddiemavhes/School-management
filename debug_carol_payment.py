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
    print(f"Student: {carol_student.first_name} {carol_student.surname}")
    print(f"Student ID: {carol_student.id}")
    print(f"\n=== BALANCES ===")
    balances = StudentBalance.objects.filter(student=carol_student)
    for balance in balances:
        term_display = f"{balance.term.get_term_display()} {balance.term.academic_year}" if balance.term else 'No term'
        print(f"Term: {term_display}")
        print(f"  Term Fee: {balance.term_fee}")
        print(f"  Previous Arrears: {balance.previous_arrears}")
        print(f"  Total Due: {balance.total_due}")
        print(f"  Amount Paid: {balance.amount_paid}")
        print(f"  Current Balance: {balance.current_balance}")
        print(f"  Arrears Remaining: {balance.arrears_remaining}")
        print(f"  Term Fee Remaining: {balance.term_fee_remaining}")
        print()
    
    print("\n=== ALL PAYMENTS ===")
    payments = Payment.objects.filter(student=carol_student)
    for payment in payments:
        term_display = f"{payment.term.get_term_display()} {payment.term.academic_year}" if payment.term else 'No term'
        print(f"Date: {payment.payment_date}")
        print(f"  Term: {term_display}")
        print(f"  Amount: {payment.amount}")
        print(f"  Payment Method: {payment.payment_method}")
        print(f"  Reference: {payment.reference_number}")
        print()
else:
    print("Carol not found")
