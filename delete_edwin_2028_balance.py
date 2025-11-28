import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.fee import StudentBalance
from core.models.academic import AcademicTerm

edwin = Student.objects.filter(first_name='Edwin').first()
if edwin:
    # Get the First Term 2028 balance
    current_term = AcademicTerm.get_current_term()
    balance_2028 = StudentBalance.objects.filter(student=edwin, term=current_term).first()
    
    if balance_2028:
        print(f"Before deletion:")
        print(f"  First Term 2028 balance: ${balance_2028.current_balance}")
        print(f"  Edwin's overall_balance: ${edwin.overall_balance}")
        
        # Delete the First Term 2028 balance - he shouldn't be charged the new term fee
        balance_2028.delete()
        print(f"\n✅ Deleted First Term 2028 balance record")
        
        # Refresh and check
        edwin.refresh_from_db()
        print(f"\nAfter deletion:")
        print(f"  Edwin's overall_balance: ${edwin.overall_balance}")
        print(f"  Edwin still owes: ${StudentBalance.objects.filter(student=edwin).aggregate(models.Sum('current_balance'))['current_balance__sum'] or 0}")
