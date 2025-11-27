#!/usr/bin/env python
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from core.models import Student, Payment, AcademicTerm
from core.models.fee import StudentBalance

User = get_user_model()

def test_payment_form():
    print("\n=== Testing Payment Form Submission ===\n")
    
    # Get test data
    admin = User.objects.filter(is_staff=True).first()
    student = Student.objects.first()
    term = AcademicTerm.get_current_term()
    
    if not admin:
        print("✗ No admin user found")
        return
    if not student:
        print("✗ No student found")
        return
    if not term:
        print("✗ No current term found")
        return
    
    print(f"Admin: {admin.full_name} (ID: {admin.id})")
    print(f"Student: {student.full_name} (ID: {student.id})")
    print(f"Term: {term}")
    
    # Initialize balance
    balance = StudentBalance.initialize_term_balance(student, term)
    print(f"Initial balance: ${balance.current_balance:.2f}\n")
    
    # Create test client and login
    client = Client()
    client.force_login(admin)
    
    # Count payments before
    payments_before = Payment.objects.filter(student=student, term=term).count()
    
    # Submit payment form
    print("Submitting payment form...")
    print(f"  Student ID: {student.id}")
    print(f"  Amount: 50.00")
    print(f"  Method: CASH")
    
    response = client.post('/payments/create/', {
        'student': str(student.id),
        'amount': '50.00',
        'payment_method': 'CASH',
        'reference_number': '',
        'notes': 'Test payment'
    }, follow=False)
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 302:
        print(f"✓ Redirected to: {response.url}")
    elif response.status_code == 200:
        print(f"✗ Form was re-rendered (did not redirect)")
        if hasattr(response, 'context') and response.context:
            if 'form' in response.context:
                form = response.context['form']
                if form.errors:
                    print(f"\n  Form field errors:")
                    for field, errors in form.errors.items():
                        print(f"    {field}: {errors}")
                if form.non_field_errors():
                    print(f"\n  Non-field errors:")
                    for error in form.non_field_errors():
                        print(f"    {error}")
    else:
        print(f"✗ Unexpected status code: {response.status_code}")
    
    # Check if payment was created
    payments_after = Payment.objects.filter(student=student, term=term).count()
    payments_created = payments_after - payments_before
    
    print(f"\nPayments created: {payments_created}")
    
    if payments_created > 0:
        latest = Payment.objects.filter(student=student, term=term).latest('created_at')
        print(f"✓ Latest payment: Receipt={latest.receipt_number}, Amount=${latest.amount:.2f}")
        print(f"  Reference: {latest.reference_number}")
        print(f"  Method: {latest.payment_method}")
    else:
        print("✗ No payments created")

if __name__ == '__main__':
    test_payment_form()
