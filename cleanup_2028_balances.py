#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance

student = Student.objects.get(first_name='Edwin', surname='Mavhe')

print("Deleting incorrect 2028 T2 and T3 balances...")
print()

# Delete 2028 T2 and T3
deleted_count = 0
for balance in StudentBalance.objects.filter(
    student=student, 
    term__academic_year=2028, 
    term__term__in=[2, 3]
):
    print(f"Deleting: {balance.term} (Fee ${balance.term_fee}, Total ${balance.total_due})")
    balance.delete()
    deleted_count += 1

print(f"Deleted {deleted_count} balance records")
print()

# Check remaining balances
print("Remaining balances:")
balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
for b in balances:
    print(f"  {b.term}: Total ${b.total_due}, Paid ${b.amount_paid}, Balance ${b.current_balance}")

print()
print(f"Overall Balance: ${student.overall_balance}")
print()

# Check auto-graduation status
print(f"Student Status:")
print(f"  Is Active: {student.is_active}")
print(f"  Is Archived: {student.is_archived}")
print(f"  Current Grade: {student.current_class}")
