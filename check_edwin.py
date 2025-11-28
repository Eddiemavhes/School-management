import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.fee import StudentBalance
from core.models.academic import AcademicTerm, Payment

# Find Edwin
edwin = Student.objects.filter(first_name='Edwin').first()
if edwin:
    print(f"Student: {edwin.full_name}")
    print(f"Grade: {edwin.current_class}")
    print(f"Status: {edwin.status}")
    print(f"Is Archived: {edwin.is_archived}")
    print(f"Is Active: {edwin.is_active}")
    print(f"Overall Balance (property): ${edwin.overall_balance}")
    
    # Check current term
    current_term = AcademicTerm.get_current_term()
    print(f"\nCurrent Term: {current_term}")
    
    # Check all balances for Edwin
    all_balances = StudentBalance.objects.filter(student=edwin).order_by('-term__academic_year', '-term__term')
    print(f"\nAll StudentBalance records for Edwin:")
    for balance in all_balances:
        print(f"  {balance.term}: term_fee=${balance.term_fee}, paid=${balance.amount_paid}, prev_arrears=${balance.previous_arrears}, current=${balance.current_balance}")
    
    # Check payments
    all_payments = Payment.objects.filter(student=edwin).order_by('-date_paid')
    print(f"\nAll Payments for Edwin: {len(all_payments)} total")
    for payment in all_payments[:10]:
        print(f"  {payment.date_paid}: ${payment.amount} for {payment.term}")

else:
    print("Edwin not found")
