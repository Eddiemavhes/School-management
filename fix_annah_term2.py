#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance

print("=" * 80)
print("FIXING ANNAH'S TERM 2 BALANCE")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()

# Show before
print(f"BEFORE:")
balances = StudentBalance.objects.filter(student=annah).order_by('term__academic_year', 'term__term')
for b in balances:
    print(f"  {b.term}: Fee ${b.term_fee}, Arrears ${b.previous_arrears}, Balance ${b.current_balance}")
print()

# Delete Term 2 record so it gets recreated with correct fee
term2_balance = StudentBalance.objects.filter(student=annah, term__academic_year=2026, term__term=2).first()
if term2_balance:
    term2_balance.delete()
    print(f"Deleted: Term 2 record")
    print()

# Reinitialize Term 2 with correct logic
from core.models import AcademicTerm
term2 = AcademicTerm.objects.filter(academic_year=2026, term=2).first()
if term2:
    new_balance = StudentBalance.initialize_term_balance(annah, term2)
    print(f"Reinitialized Term 2 with correct logic")
    print()

# Show after
print(f"AFTER:")
annah.refresh_from_db()
balances = StudentBalance.objects.filter(student=annah).order_by('term__academic_year', 'term__term')
for b in balances:
    print(f"  {b.term}: Fee ${b.term_fee}, Arrears ${b.previous_arrears}, Balance ${b.current_balance}")
print()

print(f"Overall Balance: ${annah.overall_balance}")
print()

print("=" * 80)
print("VERIFICATION:")
print("=" * 80)
print()

term1 = StudentBalance.objects.filter(student=annah, term__academic_year=2026, term__term=1).first()
term2 = StudentBalance.objects.filter(student=annah, term__academic_year=2026, term__term=2).first()

print(f"Term 1 Balance: ${term1.current_balance} (Credit)")
print(f"Term 2 Fee: ${term2.term_fee}")
print(f"Term 2 Previous Arrears: ${term2.previous_arrears}")
print()
print(f"EXPECTED CALCULATION:")
print(f"  Fee: $100")
print(f"  Previous Arrears (Credit): -$20")
print(f"  Total Due: $100 + (-$20) = $80")
print()
print(f"ACTUAL:")
print(f"  Term 2 Balance: ${term2.current_balance}")
print()

if term2.current_balance == 80:
    print(f"✓ CORRECT - Annah's Term 2 showing $80 as expected!")
else:
    print(f"❌ STILL WRONG")
