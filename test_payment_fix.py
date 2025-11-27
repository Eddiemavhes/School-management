#!/usr/bin/env python
"""Test script to verify payment creation works after StudentBalance validation fix"""
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
    # Test 1: Create a payment for student 52
    print("=" * 60)
    print("TEST 1: Create a Payment for Student 52")
    print("=" * 60)

    student = Student.objects.get(id=52)
    current_term = AcademicTerm.get_current_term()

    print(f"Student: {student.full_name}")
    print(f"Term: {current_term}")
    print()

    # Step 1: Ensure StudentBalance exists
    print("Step 1: Initialize StudentBalance...")
    balance = StudentBalance.initialize_term_balance(student, current_term)
    print(f"  ✓ Balance initialized: {balance.total_due} due")
    print()

    # Step 2: Try to create a payment
    print("Step 2: Create Payment...")
    try:
        admin = Administrator.objects.first()
        payment = Payment(
            student=student,
            term=current_term,
            amount=50,  # Pay half
            payment_method='CASH',
            reference_number='TEST-001',
            notes='Test payment after fix',
            recorded_by=admin
        )
        payment.full_clean()
        payment.save()
        print(f"  ✓ Payment created successfully!")
        print(f"    Payment ID: {payment.id}")
        print(f"    Receipt: {payment.receipt_number}")
        print(f"    Amount paid: {payment.amount}")
        print()
        
        # Step 3: Check updated balance
        print("Step 3: Check updated StudentBalance...")
        balance.refresh_from_db()
        print(f"  Amount paid: {balance.amount_paid}")
        print(f"  Current balance: {balance.current_balance}")
        print(f"  Status: {balance.payment_status}")
        
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}")
        print(f"    {str(e)}")

    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
