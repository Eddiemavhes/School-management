#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm, StudentBalance, Student, AcademicYear

# Check all years and terms
print("All academic years and terms:")
years = AcademicYear.objects.all().order_by('year')
for year in years:
    print(f"\n{year.year}:")
    terms = AcademicTerm.objects.filter(academic_year=year.year).order_by('term')
    for term in terms:
        print(f"  {term} - Current: {term.is_current}, Completed: {term.is_completed}")

# Check Annah and Brandon status
print("\n\nStudent Status:")
annah = Student.objects.get(id=8)
brandon = Student.objects.get(id=9)

for student in [annah, brandon]:
    print(f"\n{student}:")
    print(f"  Status: {student.status}")
    print(f"  Is active: {student.is_active}")
    print(f"  Current class: {student.current_class}")
    
    # Check all balances
    print(f"  Balances:")
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    for balance in balances:
        print(f"    {balance.term}: ${balance.current_balance} (Arrears: ${balance.previous_arrears}, Paid: ${balance.amount_paid})")
