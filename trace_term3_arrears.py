#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm
from decimal import Decimal

print("=" * 80)
print("TRACING CALCULATE_ARREARS LOGIC FOR ANNAH TERM 3")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()
term3 = AcademicTerm.objects.filter(academic_year=2026, term=3).first()

print(f"Student: {annah.first_name}")
print(f"Term: {term3}")
print(f"Term.term value: {term3.term}")
print(f"Term.academic_year: {term3.academic_year}")
print()

print(f"Looking for previous term in SAME YEAR:")
print(f"  Query: academic_year={term3.academic_year}, term={term3.term - 1}")

previous_term_in_year = StudentBalance.objects.filter(
    student=annah,
    term__academic_year=term3.academic_year,
    term__term=term3.term - 1
)

print(f"  Found: {previous_term_in_year.count()} records")
if previous_term_in_year.exists():
    prev = previous_term_in_year.first()
    print(f"    {prev.term}: Balance = ${prev.current_balance}")
    print(f"    → This should be carried as previous_arrears: ${prev.current_balance}")
else:
    print(f"    None found!")

print()

# Now check what's actually in Term 3
term3_balance = StudentBalance.objects.filter(student=annah, term=term3).first()
if term3_balance:
    print(f"Term 3 Balance Record:")
    print(f"  term_fee: ${term3_balance.term_fee}")
    print(f"  previous_arrears: ${term3_balance.previous_arrears}")
    print(f"  amount_paid: ${term3_balance.amount_paid}")
    print(f"  current_balance: ${term3_balance.current_balance}")
    print()
    
    if term3_balance.previous_arrears == -20:
        print(f"✓ CORRECT: Term 3 previous_arrears = -$20")
    else:
        print(f"❌ WRONG: Term 3 previous_arrears = ${term3_balance.previous_arrears}, should be -$20")
