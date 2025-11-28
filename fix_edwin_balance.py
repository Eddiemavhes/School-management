import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.fee import StudentBalance
from core.models.academic import AcademicTerm

edwin = Student.objects.filter(first_name='Edwin').first()
if edwin:
    print(f"Before: Edwin's overall_balance = ${edwin.overall_balance}")
    
    # Initialize his balance for the current term
    current_term = AcademicTerm.get_current_term()
    balance = StudentBalance.initialize_term_balance(edwin, current_term)
    
    # Refresh to get updated value
    edwin.refresh_from_db()
    print(f"After: Edwin's overall_balance = ${edwin.overall_balance}")
    
    # Show the new balance record
    if balance:
        print(f"\nCreated/Updated balance for {current_term}:")
        print(f"  term_fee: ${balance.term_fee}")
        print(f"  amount_paid: ${balance.amount_paid}")
        print(f"  previous_arrears: ${balance.previous_arrears}")
        print(f"  current_balance: ${balance.current_balance}")
