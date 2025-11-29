#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm

print("=" * 80)
print("CHECKING ANNAH'S 2027 TERM 1")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()
term1_2027 = AcademicTerm.objects.filter(academic_year=2027, term=1).first()

print(f"Student: {annah.first_name}")
print(f"Looking for: Term 1 2027")
print()

balance = StudentBalance.objects.filter(student=annah, term=term1_2027).first()

if balance:
    print(f"Found Term 1 2027 Balance:")
    print(f"  Fee: ${balance.term_fee}")
    print(f"  Arrears: ${balance.previous_arrears}")
    print(f"  Paid: ${balance.amount_paid}")
    print(f"  Balance: ${balance.current_balance}")
else:
    print(f"❌ NO Term 1 2027 balance found for Annah!")
    print()
    print(f"This means when Term 1 2027 became current, the system didn't create a balance for her")
    print(f"Or it was created but later deleted")

print()

# Check what the system SHOULD have done
term3_2026 = StudentBalance.objects.filter(student=annah, term__academic_year=2026, term__term=3).first()
if term3_2026:
    print(f"Annah's last 2026 balance (Term 3): ${term3_2026.current_balance}")
    print(f"When Term 1 2027 became current, should have created balance with:")
    print(f"  Previous Arrears: ${term3_2026.current_balance}")
