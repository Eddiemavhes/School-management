#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm, Payment
from django.db.models import Sum

print("=" * 80)
print("FIXING ANNAH TERM 1 2027 PAYMENT")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()
term1_2027 = AcademicTerm.objects.filter(academic_year=2027, term=1).first()

balance = StudentBalance.objects.filter(student=annah, term=term1_2027).first()

print(f"BEFORE:")
print(f"  amount_paid: ${balance.amount_paid}")
print(f"  current_balance: ${balance.current_balance}")
print()

# Get actual payments for this term
actual_paid = Payment.objects.filter(
    student=annah,
    term=term1_2027
).aggregate(Sum('amount'))['amount__sum'] or 0

print(f"Actual Payments in Term 1 2027: ${actual_paid}")
print()

# Update the balance
balance.amount_paid = actual_paid
balance.save()

print(f"AFTER:")
print(f"  amount_paid: ${balance.amount_paid}")
print(f"  current_balance: ${balance.current_balance}")
print()

# Now check Term 2 2027
term2_2027 = AcademicTerm.objects.filter(academic_year=2027, term=2).first()
balance2 = StudentBalance.objects.filter(student=annah, term=term2_2027).first()

print(f"Term 2 2027 (after Term 1 fix):")
print(f"  Previous Arrears should be: ${balance.current_balance}")
print(f"  Previous Arrears actually is: ${balance2.previous_arrears}")

if balance2.previous_arrears == balance.current_balance:
    print(f"  ✓ Correct!")
else:
    print(f"  ❌ Need to update!")
    # Delete and recreate
    balance2.delete()
    balance2 = StudentBalance.initialize_term_balance(annah, term2_2027)
    print(f"  Recreated Term 2 with correct arrears")

print()
print(f"Term 2 2027 (updated):")
print(f"  Fee: ${balance2.term_fee}")
print(f"  Arrears: ${balance2.previous_arrears}")
print(f"  Balance: ${balance2.current_balance}")
print()

print(f"Overall Balance: ${annah.overall_balance}")
if annah.overall_balance == 80:
    print(f"✓✓✓ CORRECT!")
else:
    print(f"❌ Shows ${annah.overall_balance}, expected $80")
