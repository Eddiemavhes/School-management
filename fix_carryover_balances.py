#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm, StudentBalance, Student

# Get the last term of 2026 and Term 1 2027
term_2026_3 = AcademicTerm.objects.filter(academic_year=2026, term=3).first()
term_2027_1 = AcademicTerm.objects.filter(academic_year=2027, term=1).first()

print(f"Last term of 2026: {term_2026_3}")
print(f"First term of 2027: {term_2027_1}")

# Get all students
students = Student.objects.filter(is_active=True)

print(f"\nCarrying over previous balances to Term 1 2027...")
for student in students:
    # Get the final balance from Term 3 2026
    final_2026_balance = StudentBalance.objects.filter(student=student, term=term_2026_3).first()
    
    if final_2026_balance:
        # Get the Term 1 2027 balance
        balance_2027_1 = StudentBalance.objects.filter(student=student, term=term_2027_1).first()
        
        if balance_2027_1:
            # Update with the carry-over from Term 3 2026
            new_arrears = final_2026_balance.current_balance
            balance_2027_1.previous_arrears = new_arrears
            balance_2027_1.save()
            
            print(f"  {student}: Carried over {final_2026_balance.current_balance} from Term 3 2026")
            print(f"    New Term 1 2027 balance: ${balance_2027_1.current_balance}")

print("\nVerification - Final balances for Term 1 2027:")
for student in students:
    balance = StudentBalance.objects.filter(student=student, term=term_2027_1).first()
    if balance:
        print(f"  {student}: Fee=${balance.term_fee}, Arrears=${balance.previous_arrears}, Paid=${balance.amount_paid}, Balance=${balance.current_balance}")
