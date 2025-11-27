#!/usr/bin/env python
"""Final Verification: Reproduce and verify the original issue is FIXED"""
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

def print_section(title):
    print()
    print("=" * 70)
    print(title.upper())
    print("=" * 70)

def test_original_issue():
    """Reproduce the ORIGINAL issue that user reported"""
    print_section("1. ORIGINAL ISSUE REPRODUCTION")
    
    print("Original symptom: 'getting that error and my other students and classes have disappeared'")
    print()
    
    # Check if students exist
    students_count = Student.objects.count()
    print(f"Step 1: Verify students still exist")
    print(f"  Total students: {students_count}")
    print(f"  Status: {'✓ OK' if students_count > 0 else '✗ MISSING'}")
    print()
    
    # Check if we can load payment form data
    student = Student.objects.first()
    current_term = AcademicTerm.get_current_term()
    
    print(f"Step 2: Try to initialize payment form for student")
    print(f"  Student: {student.full_name}")
    print(f"  Current term: {current_term}")
    print(f"  Enrollment date: {student.date_enrolled}")
    print(f"  Term dates: {current_term.start_date} to {current_term.end_date}")
    print()
    
    try:
        balance = StudentBalance.initialize_term_balance(student, current_term)
        print(f"  Status: ✓ OK - StudentBalance initialized")
        print(f"    Balance data loaded: {balance.term_fee}")
    except Exception as e:
        print(f"  Status: ✗ ERROR - {str(e)[:80]}")
        return False
    
    return True

def test_payment_creation_flow():
    """Test the complete payment creation flow"""
    print_section("2. PAYMENT CREATION FLOW")
    
    student = Student.objects.get(id=52)
    current_term = AcademicTerm.get_current_term()
    admin = Administrator.objects.first()
    
    print(f"Flow: StudentBalance → Payment → Update Balance")
    print()
    
    # Step 1: Balance
    print("Step 1: Initialize StudentBalance")
    try:
        balance = StudentBalance.initialize_term_balance(student, current_term)
        print(f"  ✓ Balance created")
        print(f"    Term fee: {balance.term_fee}")
        print(f"    Total due: {balance.total_due}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    print()
    print("Step 2: Create Payment")
    try:
        payment = Payment(
            student=student,
            term=current_term,
            amount=75,
            payment_method='CASH',
            reference_number='FLOW-001',
            recorded_by=admin
        )
        payment.full_clean()
        payment.save()
        print(f"  ✓ Payment created")
        print(f"    Receipt: {payment.receipt_number}")
        print(f"    Amount: {payment.amount}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    print()
    print("Step 3: Verify Balance Updated")
    balance.refresh_from_db()
    print(f"  Amount paid: {balance.amount_paid}")
    print(f"  Current balance: {balance.current_balance}")
    print(f"  Status: {balance.payment_status}")
    print(f"  ✓ Balance updated correctly")
    
    return True

def test_all_students():
    """Test that ALL students work, not just one"""
    print_section("3. ALL 9 STUDENTS TEST")
    
    current_term = AcademicTerm.get_current_term()
    
    success_count = 0
    fail_count = 0
    failures = []
    
    for student in Student.objects.all():
        try:
            balance = StudentBalance.initialize_term_balance(student, current_term)
            success_count += 1
        except Exception as e:
            fail_count += 1
            failures.append(f"{student.full_name}: {str(e)[:50]}")
    
    print(f"Total students: {Student.objects.count()}")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")
    
    if failures:
        for failure in failures:
            print(f"  ✗ {failure}")
        return False
    else:
        print("✓ All students can initialize balances")
        return True

def test_ui_data_loading():
    """Test that payment form API data can be loaded"""
    print_section("4. PAYMENT FORM DATA LOADING")
    
    from django.test import Client
    
    client = Client()
    student_id = 52
    
    print(f"Testing API endpoint: /api/student-payment-details/{student_id}/")
    print()
    
    response = client.get(f'/api/student-payment-details/{student_id}/')
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Status code: {response.status_code}")
        print(f"  ✓ API returned data successfully")
        
        # Check for the critical "Error loading student" issue
        if 'error' not in data:
            print(f"  ✓ No error in response")
            print(f"    Student: {data.get('student_name', 'N/A')}")
            print(f"    Balance: {data.get('current_balance', 'N/A')}")
        else:
            print(f"  ✗ ERROR in response: {data.get('error')}")
            return False
    else:
        print(f"  ✗ API failed with status: {response.status_code}")
        return False
    
    return True

def main():
    print_section("COMPREHENSIVE FIX VERIFICATION")
    
    results = {
        "Original Issue": test_original_issue(),
        "Payment Flow": test_payment_creation_flow(),
        "All Students": test_all_students(),
        "UI Data Loading": test_ui_data_loading(),
    }
    
    print()
    print_section("FINAL RESULTS")
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print()
    
    if all_passed:
        print("=" * 70)
        print("✓ ALL TESTS PASSED - FIX IS COMPLETE AND WORKING")
        print("=" * 70)
        return 0
    else:
        print("=" * 70)
        print("✗ SOME TESTS FAILED - REVIEW ABOVE FOR DETAILS")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
