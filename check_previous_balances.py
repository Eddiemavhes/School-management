#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm, StudentBalance, Student

# Check all terms
all_terms = AcademicTerm.objects.all().order_by('academic_year', 'term')
print("All academic terms:")
for term in all_terms:
    print(f"  {term} (current: {term.is_current})")

# Check balances for each student across all terms
students = Student.objects.filter(is_active=True)
print(f"\nBalances for each student across all terms:")
for student in students:
    print(f"\n{student}:")
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    for balance in balances:
        print(f"  {balance.term}: Fee=${balance.term_fee}, Paid=${balance.amount_paid}, Arrears=${balance.previous_arrears}, Balance=${balance.current_balance}")
    
    if not balances.exists():
        print("  (no balances found)")
