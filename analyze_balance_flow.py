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
print("ANALYZING BALANCE FLOW")
print("=" * 80)
print()

students_to_check = ['Brandon', 'Cathrine', 'David', 'Annah']

for name in students_to_check:
    student = Student.objects.filter(first_name=name).first()
    
    print(f"\n{name}:")
    print("-" * 80)
    
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    
    for i, b in enumerate(balances):
        print(f"  Term {b.term.term}:")
        print(f"    term_fee: ${b.term_fee}")
        print(f"    previous_arrears: ${b.previous_arrears}")
        print(f"    amount_paid: ${b.amount_paid}")
        print(f"    current_balance: ${b.current_balance}")
        print(f"      Calculation: (${b.term_fee} + ${b.previous_arrears}) - ${b.amount_paid} = ${b.current_balance}")
        print()
        
        if i == 0:
            print(f"    → Expected Term 1 balance: ${b.current_balance}")
        else:
            print(f"    → Term 1 balance was: ${balances[0].current_balance}")
            print(f"    → Should be carried as previous_arrears: ${balances[0].current_balance}")
            expected_balance = b.term_fee + balances[0].current_balance
            print(f"    → Expected Term 2 balance: ${b.term_fee} + ${balances[0].current_balance} = ${expected_balance}")
            if b.previous_arrears == balances[0].current_balance:
                print(f"    ✓ Previous arrears correctly set")
            else:
                print(f"    ❌ Previous arrears WRONG: should be ${balances[0].current_balance}, got ${b.previous_arrears}")
