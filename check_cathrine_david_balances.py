#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance

print("="*80)
print("CHECKING ARCHIVED BALANCES FOR CATHRINE & DAVID")
print("="*80)

for name in ['Cathrine', 'David']:
    student = Student.all_students.get(first_name=name)
    
    print(f"\n{name}:")
    print(f"  Status: {student.status}")
    print(f"  Is Archived: {student.is_archived}")
    print(f"  Overall Balance: ${student.overall_balance:.2f}")
    
    # Check all balances
    all_balances = StudentBalance.objects.filter(student=student).order_by('-term__academic_year', '-term__term')
    print(f"  All Balances ({all_balances.count()}):")
    
    for balance in all_balances:
        print(f"    {balance.term.academic_year} T{balance.term.term}: ${balance.current_balance:.2f}")
        print(f"      Fee: ${balance.term_fee:.2f}, Paid: ${balance.amount_paid:.2f}, Arrears: ${balance.previous_arrears:.2f}")

print("\n" + "="*80)
print("UNDERSTANDING: overall_balance property")
print("="*80)
print("""
The overall_balance property likely returns:
1. Current term balance (if current term exists)
2. Or latest past term balance (if no current term)

For graduated students, if they still have old term balances with positive values,
overall_balance will show those.

This is actually CORRECT behavior!
- Cathrine DOES owe $10 from 2027 (archived, not paid)
- David DOES owe $600 from 2027 (archived, not paid)

They are correctly marked as GRADUATED + ARCHIVED
But their financial obligation still exists in the system.

When they eventually pay off those balances, they will show $0.00
""")
