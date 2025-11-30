#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm, TermFee, StudentBalance, Student

# Get Term 1 2027
term_2027_1 = AcademicTerm.objects.filter(academic_year=2027, term=1).first()
print(f"Term 1 2027: {term_2027_1}")
print(f"  Is current: {term_2027_1.is_current}")

# Get term fee
term_fee = TermFee.objects.filter(term=term_2027_1).first()
if not term_fee:
    print("ERROR: No term fee found!")
    sys.exit(1)

print(f"  Fee amount: ${term_fee.amount}")

# Get all active students
active_students = Student.objects.filter(is_active=True)
print(f"\nActive students ({active_students.count()}):")
for student in active_students:
    print(f"  - {student} (ID: {student.id})")

# Create balances for all active students
print(f"\nCreating balances for all active students...")
for student in active_students:
    balance, created = StudentBalance.objects.get_or_create(
        student=student,
        term=term_2027_1,
        defaults={
            'term_fee': term_fee.amount,
            'amount_paid': 0,
            'previous_arrears': 0
        }
    )
    if created:
        print(f"  ✓ Created balance for {student}: ${balance.current_balance}")
    else:
        print(f"  - Balance already exists for {student}: ${balance.current_balance}")

# Verify
print(f"\nFinal check - Student balances for Term 1 2027:")
balances = StudentBalance.objects.filter(term=term_2027_1)
for balance in balances:
    print(f"  {balance.student}: ${balance.current_balance}")
