#!/usr/bin/env python
"""Test script to verify payment creation works for ALL students"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from core.models.student import Student
from core.models.academic import AcademicTerm, Payment
from core.models.fee import StudentBalance
from core.models.administrator import Administrator

def main():
    print("=" * 70)
    print("BULK TEST: Creating payments for ALL 9 students")
    print("=" * 70)

    current_term = AcademicTerm.get_current_term()
    admin = Administrator.objects.first()

    print(f"Term: {current_term}")
    print(f"Admin: {admin.full_name}")
    print()

    success_count = 0
    fail_count = 0

    for student in Student.objects.all():
        try:
            # Initialize balance
            balance = StudentBalance.initialize_term_balance(student, current_term)
            
            # Create payment
            payment = Payment(
                student=student,
                term=current_term,
                amount=60,  # Pay half of 120
                payment_method='CASH',
                reference_number=f'TEST-{student.id}',
                notes=f'Test payment for {student.full_name}',
                recorded_by=admin
            )
            payment.full_clean()
            payment.save()
            
            # Verify balance updated
            balance.refresh_from_db()
            
            print(f"✓ {student.full_name}: {balance.current_balance} remaining ({balance.payment_status})")
            success_count += 1
            
        except Exception as e:
            print(f"✗ {student.full_name}: {str(e)[:60]}")
            fail_count += 1

    print()
    print("=" * 70)
    print(f"RESULTS: {success_count} succeeded, {fail_count} failed")
    print("=" * 70)

if __name__ == '__main__':
    main()
