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
print("CREATING MISSING TERM 1 2027 BALANCE FOR ANNAH")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()
term1_2027 = AcademicTerm.objects.filter(academic_year=2027, term=1).first()

print(f"Student: {annah.first_name}")
print(f"Is Active: {annah.is_active}")
print()

# Create the missing balance
print(f"Creating Term 1 2027 balance...")
balance = StudentBalance.initialize_term_balance(annah, term1_2027)

print(f"Created successfully!")
print()

# Show the result
print(f"Term 1 2027 Balance:")
print(f"  Fee: ${balance.term_fee}")
print(f"  Previous Arrears: ${balance.previous_arrears}")
print(f"  Paid: ${balance.amount_paid}")
print(f"  Balance: ${balance.current_balance}")
print()

# Now check what needs to happen for Term 2 2027
term2_2027 = AcademicTerm.objects.filter(academic_year=2027, term=2).first()
existing_term2 = StudentBalance.objects.filter(student=annah, term=term2_2027).first()

if existing_term2:
    print(f"Term 2 2027 exists with:")
    print(f"  Fee: ${existing_term2.term_fee}")
    print(f"  Previous Arrears: ${existing_term2.previous_arrears} (should be ${balance.current_balance})")
    
    if existing_term2.previous_arrears != balance.current_balance:
        print(f"  ❌ Need to fix Term 2 arrears!")
        
        # Delete and recreate Term 2
        existing_term2.delete()
        print(f"Deleted old Term 2 2027")
        
        new_term2 = StudentBalance.initialize_term_balance(annah, term2_2027)
        print(f"Recreated Term 2 2027 with correct arrears")
        print()
        print(f"Term 2 2027 (updated):")
        print(f"  Fee: ${new_term2.term_fee}")
        print(f"  Previous Arrears: ${new_term2.previous_arrears}")
        print(f"  Balance: ${new_term2.current_balance}")

print()
print(f"Overall Balance (current term): ${annah.overall_balance}")

if annah.overall_balance == 80:
    print(f"✓✓✓ CORRECT! Annah's balance is now $80")
else:
    print(f"❌ Still wrong: ${annah.overall_balance} instead of $80")
