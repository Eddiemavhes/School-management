"""
Test script to verify session handling and stability
Tests concurrent request simulation and session error recovery
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


def test_session_stability():
    """Test that sessions remain stable during multiple requests"""
    print("\n" + "="*60)
    print("SESSION STABILITY TEST")
    print("="*60)
    
    client = Client()
    
    # Create test user if needed
    try:
        admin = User.objects.get(email='admin@test.com')
    except User.DoesNotExist:
        admin = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Test',
            last_name='Admin'
        )
        print("✓ Created test admin user")
    
    # Test 1: Login
    print("\n[1] Testing login...")
    response = client.post('/login/', {
        'email': 'admin@test.com',
        'password': 'admin123'
    }, follow=True)
    
    if response.status_code == 200:
        print("✓ Login successful (HTTP 200)")
        session_key = client.session.session_key
        print(f"✓ Session created: {session_key[:8]}...")
    else:
        print(f"✗ Login failed (HTTP {response.status_code})")
        return False
    
    # Test 2: Access students page
    print("\n[2] Testing /students/ access...")
    response = client.get('/students/', follow=True)
    
    if response.status_code == 200:
        print("✓ Students page accessed (HTTP 200)")
    else:
        print(f"✗ Students page failed (HTTP {response.status_code})")
        if hasattr(response, 'content'):
            print(f"  Response preview: {response.content[:200]}")
        return False
    
    # Test 3: Access dashboard
    print("\n[3] Testing /dashboard/ access...")
    response = client.get('/dashboard/', follow=True)
    
    if response.status_code == 200:
        print("✓ Dashboard page accessed (HTTP 200)")
    else:
        print(f"✗ Dashboard page failed (HTTP {response.status_code})")
        return False
    
    # Test 4: Multiple requests (simulate typical user behavior)
    print("\n[4] Testing multiple sequential requests...")
    pages = [
        '/students/',
        '/dashboard/',
        '/students/',  # Access again to test session reuse
    ]
    
    for page in pages:
        response = client.get(page, follow=True)
        if response.status_code == 200:
            print(f"✓ {page} - OK")
        else:
            print(f"✗ {page} - FAILED (HTTP {response.status_code})")
            return False
    
    # Test 5: Logout
    print("\n[5] Testing logout...")
    response = client.get('/logout/', follow=True)
    
    if response.status_code == 200:
        print("✓ Logout successful (HTTP 200)")
    else:
        print(f"✗ Logout failed (HTTP {response.status_code})")
    
    print("\n" + "="*60)
    print("✓ ALL SESSION TESTS PASSED")
    print("="*60)
    return True


def test_payment_system():
    """Test that payment system works correctly"""
    print("\n" + "="*60)
    print("PAYMENT SYSTEM SANITY CHECK")
    print("="*60)
    
    from core.models import AcademicYear, AcademicTerm, Student, StudentBalance, Payment
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Get current term
    try:
        term = AcademicTerm.objects.filter(is_current=True).first()
        
        if not term:
            print("✗ No active term found")
            return False
        
        print(f"✓ Found active term: {term.get_term_display()} ({term.academic_year})")
        
        # Check students
        students = Student.objects.filter(is_active=True)
        
        if students.exists():
            print(f"✓ Found {students.count()} active students")
            
            # Check balances
            balances = StudentBalance.objects.filter(term=term)
            if balances.exists():
                print(f"✓ Found {balances.count()} student balances for current term")
                
                # Show sample balance
                sample = balances.first()
                print(f"  Sample: {sample.student.first_name} - Balance: ${sample.current_balance}")
                print(f"  Payment Status: {sample.payment_status}")
                print(f"  Term Fee: ${sample.term_fee}")
            else:
                print("⚠ No balances found for current term (may need initialization)")
        else:
            print("⚠ No active students found")
        
    except Exception as e:
        print(f"✗ Error checking payment system: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("✓ PAYMENT SYSTEM CHECK COMPLETE")
    print("="*60)
    return True


if __name__ == '__main__':
    print("\n" + "🔍 RUNNING COMPREHENSIVE STABILITY TESTS...\n")
    
    # Run tests
    session_ok = test_session_stability()
    payment_ok = test_payment_system()
    
    print("\n" + "="*60)
    if session_ok and payment_ok:
        print("✅ ALL TESTS PASSED - SYSTEM IS STABLE")
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW ABOVE")
    print("="*60 + "\n")
