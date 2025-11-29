#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, Payment
from decimal import Decimal

# Check all students in the UI
students = Student.objects.filter(is_active=True, is_deleted=False).order_by('first_name')

print("=" * 80)
print("CHECKING ALL ACTIVE STUDENTS FOR CREDIT/OVERPAYMENT ISSUES")
print("=" * 80)
print()

for student in students:
    print(f"{student.first_name} {student.surname}:")
    print(f"  Overall Balance: ${student.overall_balance}")
    
    # Check if any term has negative balance (credit)
    balances = StudentBalance.objects.filter(student=student)
    has_credit = False
    for b in balances:
        if b.current_balance < 0:
            has_credit = True
            print(f"  ❗ {b.term}: Balance ${b.current_balance} (CREDIT ${abs(b.current_balance)})")
        
        # Check if overpaid
        if b.amount_paid > b.total_due:
            print(f"  ❗ {b.term}: Overpaid - Paid ${b.amount_paid}, Owed ${b.total_due}")
    
    if student.overall_balance < 0:
        print(f"  ✅ NET CREDIT: ${abs(student.overall_balance)}")
    
    if student.overall_balance == 0:
        print(f"  ✅ FULLY PAID")
    
    print()
