import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.fee import StudentBalance

edwin = Student.objects.filter(first_name='Edwin').first()
if edwin:
    balances = StudentBalance.objects.filter(student=edwin).order_by('-term__academic_year', '-term__term')
    
    print(f"Edwin's all-term balances:\n")
    total = 0
    for balance in balances:
        print(f"{balance.term}:")
        print(f"  fee=${ balance.term_fee}, paid=${balance.amount_paid}, arrears=${balance.previous_arrears}")
        print(f"  current_balance=${balance.current_balance}")
        total += balance.current_balance
    
    print(f"\n💰 TOTAL OWED ACROSS ALL TERMS: ${total}")
    print(f"\n📋 Should Edwin have $20 or ${total} outstanding?")
    print(f"   (The $20 is only from Third Term 2027)")
    print(f"   (The ${total} includes all unpaid balances from all terms)")
