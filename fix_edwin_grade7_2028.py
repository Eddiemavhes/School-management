#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm, StudentBalance
from decimal import Decimal

student = Student.objects.get(first_name='Edwin', surname='Mavhe')
term_2028_t1 = AcademicTerm.objects.get(academic_year=2028, term=1)

print(f"Fixing Edwin's 2028 Term 1 balance...")
print()

# Get the 2027 T3 balance (last term of previous year)
balance_2027_t3 = StudentBalance.objects.get(student=student, term__academic_year=2027, term__term=3)
print(f"2027 Term 3 balance: ${balance_2027_t3.current_balance}")

# Fix 2028 T1 balance
try:
    balance_2028_t1 = StudentBalance.objects.get(student=student, term=term_2028_t1)
    print(f"Found 2028 Term 1 balance:")
    print(f"  Before: Fee ${balance_2028_t1.term_fee}, Arrears ${balance_2028_t1.previous_arrears}, Total ${balance_2028_t1.total_due}")
    
    # Update to have $0 fee and carry forward arrears
    balance_2028_t1.term_fee = Decimal('0.00')
    balance_2028_t1.previous_arrears = balance_2027_t3.current_balance
    balance_2028_t1.save()
    
    print(f"  After: Fee ${balance_2028_t1.term_fee}, Arrears ${balance_2028_t1.previous_arrears}, Total ${balance_2028_t1.total_due}")
    print(f"✅ Fixed!")
    
except StudentBalance.DoesNotExist:
    print(f"2028 Term 1 balance doesn't exist yet")

print()
print(f"Overall Balance: ${student.overall_balance}")
