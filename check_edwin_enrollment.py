import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.fee import StudentBalance
from core.models.academic import AcademicTerm

edwin = Student.objects.filter(first_name='Edwin').first()
if edwin:
    print(f"Edwin: {edwin.full_name}")
    print(f"Current Class: {edwin.current_class}")
    print(f"Status: {edwin.status}")
    print(f"Is Active: {edwin.is_active}")
    
    # Check First Term 2028
    first_term_2028 = AcademicTerm.objects.filter(academic_year=2028, term=1).first()
    print(f"\nFirst Term 2028: {first_term_2028}")
    
    balance_2028 = StudentBalance.objects.filter(student=edwin, term=first_term_2028).first()
    print(f"Balance record in First Term 2028: {balance_2028}")
    
    if balance_2028:
        print(f"  term_fee: ${balance_2028.term_fee}")
        print(f"  amount_paid: ${balance_2028.amount_paid}")
        print(f"  previous_arrears: ${balance_2028.previous_arrears}")
        print(f"  current_balance: ${balance_2028.current_balance}")
    else:
        print("  NO BALANCE RECORD - This is the problem!")
    
    # Check what should be the previous arrears for Term 1 2028
    third_term_2027 = AcademicTerm.objects.filter(academic_year=2027, term=3).first()
    balance_2027_t3 = StudentBalance.objects.filter(student=edwin, term=third_term_2027).first()
    if balance_2027_t3:
        print(f"\nThird Term 2027 balance: ${balance_2027_t3.current_balance}")
        print(f"This $20 should carry forward as previous_arrears to First Term 2028!")
