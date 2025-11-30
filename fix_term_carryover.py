#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm, StudentBalance, Student

# Get terms
term_2027_1 = AcademicTerm.objects.filter(academic_year=2027, term=1).first()
term_2027_2 = AcademicTerm.objects.filter(academic_year=2027, term=2).first()
term_2027_3 = AcademicTerm.objects.filter(academic_year=2027, term=3).first()

# Get all students
students = Student.objects.filter(is_active=True)

print("Carrying over balances from Term 1 → Term 2 → Term 3\n")

# First: Term 1 → Term 2
print("=== Term 1 → Term 2 ===")
for student in students:
    balance_t1 = StudentBalance.objects.filter(student=student, term=term_2027_1).first()
    balance_t2 = StudentBalance.objects.filter(student=student, term=term_2027_2).first()
    
    if balance_t1 and balance_t2:
        print(f"\n{student}:")
        print(f"  Term 1 current balance: ${balance_t1.current_balance}")
        
        # Update Term 2 with Term 1's current balance as previous_arrears
        old_arrears = balance_t2.previous_arrears
        balance_t2.previous_arrears = balance_t1.current_balance
        balance_t2.save()
        
        print(f"  Term 2 arrears: ${old_arrears} → ${balance_t2.previous_arrears}")
        print(f"  Term 2 new balance: ${balance_t2.current_balance}")

# Second: Term 2 → Term 3
print("\n\n=== Term 2 → Term 3 ===")
for student in students:
    balance_t2 = StudentBalance.objects.filter(student=student, term=term_2027_2).first()
    balance_t3 = StudentBalance.objects.filter(student=student, term=term_2027_3).first()
    
    if balance_t2 and balance_t3:
        print(f"\n{student}:")
        print(f"  Term 2 current balance: ${balance_t2.current_balance}")
        
        # Update Term 3 with Term 2's current balance as previous_arrears
        old_arrears = balance_t3.previous_arrears
        balance_t3.previous_arrears = balance_t2.current_balance
        balance_t3.save()
        
        print(f"  Term 3 arrears: ${old_arrears} → ${balance_t3.previous_arrears}")
        print(f"  Term 3 new balance: ${balance_t3.current_balance}")

# Verification
print("\n\n=== FINAL VERIFICATION ===")
for student in students:
    print(f"\n{student}:")
    for i, term in enumerate([term_2027_1, term_2027_2, term_2027_3], 1):
        balance = StudentBalance.objects.filter(student=student, term=term).first()
        if balance:
            print(f"  Term {i}: Arrears=${balance.previous_arrears}, Fee=${balance.term_fee}, Paid=${balance.amount_paid}, Balance=${balance.current_balance}")
