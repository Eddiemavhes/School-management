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
    print(f"Grade: {edwin.current_class}")
    print(f"Status: {edwin.status}")
    print(f"Is Active: {edwin.is_active}")
    print(f"Is Archived: {edwin.is_archived}")
    
    # Check his balances
    all_balances = StudentBalance.objects.filter(student=edwin).order_by('-term__academic_year', '-term__term')
    print(f"\nAll balances:")
    for balance in all_balances:
        print(f"  {balance.term}: fee=${balance.term_fee}, paid=${balance.amount_paid}, arrears=${balance.previous_arrears}, balance=${balance.current_balance}")
