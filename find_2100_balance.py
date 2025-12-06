#!/usr/bin/env python
"""Analyze where the 2100 balance display comes from"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.fee import StudentBalance
from decimal import Decimal

# Get all students
students = Student.objects.all()

print(f"{'='*60}")
print(f"CHECKING FOR 2100 BALANCE DISPLAYS")
print(f"{'='*60}")

for student in students:
    # Check if this student has a 2100 balance somewhere
    
    # 1. Check student.overall_balance property
    overall = student.overall_balance
    
    # 2. Check sum of all balances
    all_balances = StudentBalance.objects.filter(student=student)
    sum_of_balances = sum(b.current_balance for b in all_balances)
    
    # 3. Check sum of first 6 balances (1+2+3+4+5+6 = 2100)
    sum_first_six = sum(b.current_balance for b in all_balances[:6])
    
    # Check if any of these equal 2100
    if overall == 2100 or sum_of_balances == 2100 or sum_first_six == 2100:
        print(f"\n{student.full_name}:")
        print(f"  overall_balance: ${overall:.2f}")
        print(f"  sum of all balances: ${sum_of_balances:.2f}")
        print(f"  sum of first 6 balances: ${sum_first_six:.2f}")
        print(f"  ⚠️ Found potential 2100 issue!")

# Also check for David specifically
david = Student.objects.filter(first_name='David').first()
if david:
    print(f"\n{'='*60}")
    print(f"DAVID'S DETAILED ANALYSIS")
    print(f"{'='*60}")
    print(f"David overall_balance: ${david.overall_balance:.2f}")
    
    balances = StudentBalance.objects.filter(student=david).order_by('term__academic_year', 'term__term')
    print(f"\nAll balance records:")
    balance_sum = Decimal('0')
    for i, b in enumerate(balances, 1):
        print(f"  {i}. {b.term}: ${b.current_balance:.2f}")
        balance_sum += b.current_balance
        
    print(f"\nSum of first 6 balances: ${sum(b.current_balance for b in balances[:6]):.2f}")
    print(f"Sum of all {len(list(balances))} balances: ${balance_sum:.2f}")
    print(f"Latest balance only: ${balances.last().current_balance:.2f}")
