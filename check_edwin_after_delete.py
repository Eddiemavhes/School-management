import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.db.models import Sum
from core.models import Student
from core.models.fee import StudentBalance

edwin = Student.objects.filter(first_name='Edwin').first()
if edwin:
    # Show what remains
    total_outstanding = StudentBalance.objects.filter(student=edwin).aggregate(Sum('current_balance'))['current_balance__sum'] or 0
    
    print(f"After deletion:")
    print(f"  Edwin's overall_balance: ${edwin.overall_balance}")
    print(f"  Edwin's total outstanding (all terms): ${total_outstanding}")
    
    # Show remaining balances
    balances = StudentBalance.objects.filter(student=edwin).order_by('-term__academic_year', '-term__term')
    print(f"\nRemaining balance records:")
    for balance in balances:
        print(f"  {balance.term}: balance=${balance.current_balance}")
