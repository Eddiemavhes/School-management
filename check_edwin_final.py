import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.fee import StudentBalance

edwin = Student.objects.filter(first_name='Edwin').first()
if edwin:
    print(f"Edwin: {edwin.full_name}")
    print(f"Status: {edwin.status}")
    print(f"Is Active: {edwin.is_active}")
    print(f"Overall Balance: ${edwin.overall_balance}")
    
    # Show remaining balances
    balances = StudentBalance.objects.filter(student=edwin).order_by('-term__academic_year', '-term__term')
    print(f"\nRemaining balance records: {balances.count()}")
    for balance in balances:
        print(f"  {balance.term}: balance=${balance.current_balance}")
