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
print("ANALYZING TERM 2027 TRANSITION")
print("=" * 80)
print()

current_term = AcademicTerm.objects.filter(is_current=True).first()
print(f"Current Term: {current_term}\n")

students = ['Annah', 'Brandon', 'Cathrine', 'David']

for name in students:
    student = Student.objects.filter(first_name=name).first()
    
    print(f"\n{name}:")
    print("-" * 80)
    
    # Get all balances
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    
    print(f"All Balances:")
    for b in balances:
        is_current = "← CURRENT" if b.term == current_term else ""
        print(f"  {b.term}: Fee ${b.term_fee}, Arrears ${b.previous_arrears}, Paid ${b.amount_paid}, Balance ${b.current_balance} {is_current}")
    
    print()
    
    # Analyze the 2026->2027 transition
    last_2026 = StudentBalance.objects.filter(student=student, term__academic_year=2026).order_by('-term__term').first()
    first_2027 = StudentBalance.objects.filter(student=student, term__academic_year=2027, term__term=1).first()
    
    if last_2026:
        print(f"Last 2026 Balance: ${last_2026.current_balance}")
    
    if first_2027:
        print(f"2027 Term 1 Setup:")
        print(f"  Fee: ${first_2027.term_fee}")
        print(f"  Previous Arrears: ${first_2027.previous_arrears}")
        print(f"  Expected: Fee + Last 2026 Balance = ${first_2027.term_fee} + ${last_2026.current_balance if last_2026 else 0}")
        print(f"  Actual Balance: ${first_2027.current_balance}")
        
        if last_2026 and first_2027.previous_arrears == last_2026.current_balance:
            print(f"  ✓ Previous arrears correctly set")
        else:
            print(f"  ❌ Previous arrears WRONG")
    
    print()
    print(f"Overall Balance (should be current term): ${student.overall_balance}")
    print()
