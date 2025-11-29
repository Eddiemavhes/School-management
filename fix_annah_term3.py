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
print("FIXING ANNAH'S TERM 3 BALANCE")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()
term3 = AcademicTerm.objects.filter(academic_year=2026, term=3).first()

# Show before
print(f"BEFORE:")
balances = StudentBalance.objects.filter(student=annah).order_by('term__term')
for b in balances:
    print(f"  {b.term}: Fee ${b.term_fee}, Arrears ${b.previous_arrears}, Paid ${b.amount_paid}, Balance ${b.current_balance}")
print(f"  Overall: ${annah.overall_balance}")
print()

# Delete Term 3
term3_balance = StudentBalance.objects.filter(student=annah, term=term3).first()
if term3_balance:
    term3_balance.delete()
    print(f"Deleted Term 3 balance")
    print()

# Reinitialize Term 3
new_balance = StudentBalance.initialize_term_balance(annah, term3)
print(f"Reinitialized Term 3")
print()

# Show after
print(f"AFTER:")
annah.refresh_from_db()
balances = StudentBalance.objects.filter(student=annah).order_by('term__term')
for b in balances:
    print(f"  {b.term}: Fee ${b.term_fee}, Arrears ${b.previous_arrears}, Paid ${b.amount_paid}, Balance ${b.current_balance}")
print(f"  Overall: ${annah.overall_balance}")
print()

print("=" * 80)
print("VERIFICATION")
print("=" * 80)
print()

term2 = StudentBalance.objects.filter(student=annah, term__term=2).first()
term3 = StudentBalance.objects.filter(student=annah, term__term=3).first()

print(f"Term 2 Balance: ${term2.current_balance}")
print(f"Term 3 Previous Arrears should be: ${term2.current_balance}")
print(f"Term 3 Previous Arrears actually is: ${term3.previous_arrears}")
print()

if term3.previous_arrears == term2.current_balance:
    print(f"✓ CORRECT: Term 3 inherited credit from Term 2")
else:
    print(f"❌ WRONG: Term 3 still has wrong arrears")
    
print()
print(f"Term 3 Balance: ${term3.current_balance}")
print()

# The overall balance should now be Term 3 balance since it's the latest term
if annah.overall_balance == -20:
    print(f"✓ CORRECT: Overall balance is -$20 (the credit)")
else:
    print(f"❌ Overall balance is ${annah.overall_balance}, expected -$20")
