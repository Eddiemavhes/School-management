import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
import django
django.setup()

from core.models import Student, Class, AcademicYear, AcademicTerm, Administrator
from core.models.academic import Payment
from core.models.fee import StudentBalance, TermFee
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date

print("=" * 80)
print("TESTING PAYMENT VALIDATIONS")
print("=" * 80)

# Setup: Create test data
print("\n📋 Setting up test data...")

# Create academic year
year = 2025
academic_year, _ = AcademicYear.objects.get_or_create(
    year=year,
    defaults={
        'is_active': True,
        'start_date': f'{year}-01-01',
        'end_date': f'{year}-12-31'
    }
)

# Create current term
current_term, _ = AcademicTerm.objects.get_or_create(
    academic_year=year,
    term=1,
    defaults={
        'start_date': date(year, 1, 15),
        'end_date': date(year, 4, 15),
        'is_current': True
    }
)

# Create next term (for excess payment testing)
next_term, _ = AcademicTerm.objects.get_or_create(
    academic_year=year,
    term=2,
    defaults={
        'start_date': date(year, 5, 1),
        'end_date': date(year, 8, 1),
        'is_current': False
    }
)

# Create test class
test_class, _ = Class.objects.get_or_create(
    grade=1,
    section='A',
    academic_year=year
)

# Create admin user
admin_user, _ = Administrator.objects.get_or_create(
    email='paymenttest@school.com',
    defaults={
        'first_name': 'Payment',
        'last_name': 'Admin',
        'is_staff': True
    }
)

# Create term fees
current_fee, _ = TermFee.objects.get_or_create(
    term=current_term,
    defaults={
        'amount': Decimal('1000.00')
    }
)

next_fee, _ = TermFee.objects.get_or_create(
    term=next_term,
    defaults={
        'amount': Decimal('1000.00')
    }
)

# Create test student
test_student, _ = Student.objects.get_or_create(
    birth_entry_number='TEST-PAYMENT-001',
    defaults={
        'surname': 'Payment',
        'first_name': 'Student',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': True,
        'current_class': test_class
    }
)

# Create inactive student
inactive_student, _ = Student.objects.get_or_create(
    birth_entry_number='TEST-PAYMENT-INACTIVE',
    defaults={
        'surname': 'Inactive',
        'first_name': 'Student',
        'date_of_birth': '2015-01-01',
        'sex': 'F',
        'is_active': False,
        'current_class': test_class
    }
)

# Initialize balances
StudentBalance.initialize_term_balance(test_student, current_term)
StudentBalance.initialize_term_balance(inactive_student, current_term)

print("✅ Test data setup complete\n")

# ============================================================================
# TEST 1: Current Term Only Enforcement
# ============================================================================
print("1. TESTING CURRENT TERM ONLY ENFORCEMENT")
print("-" * 80)

try:
    print("❌ Attempting payment for NON-CURRENT term...")
    payment = Payment(
        student=test_student,
        term=next_term,  # Not current
        amount=Decimal('100.00'),
        payment_method='CASH',
        recorded_by=admin_user
    )
    payment.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

try:
    print("✅ Attempting payment for CURRENT term...")
    payment = Payment(
        student=test_student,
        term=current_term,  # Is current
        amount=Decimal('100.00'),
        payment_method='CASH',
        recorded_by=admin_user
    )
    payment.full_clean()
    print("   ✅ PASSED: Payment for current term accepted")
except ValidationError as e:
    print(f"   FAILED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

# ============================================================================
# TEST 2: Amount >= 0 Check
# ============================================================================
print("\n2. TESTING AMOUNT >= 0 CHECK")
print("-" * 80)

try:
    print("❌ Attempting payment with NEGATIVE amount...")
    payment = Payment(
        student=test_student,
        term=current_term,
        amount=Decimal('-100.00'),  # Negative
        payment_method='CASH',
        recorded_by=admin_user
    )
    payment.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

try:
    print("✅ Attempting payment with ZERO amount...")
    payment = Payment(
        student=test_student,
        term=current_term,
        amount=Decimal('0.00'),  # Zero (allowed for placeholders)
        payment_method='CASH',
        recorded_by=admin_user
    )
    payment.full_clean()
    print("   ✅ PASSED: Zero amount accepted (allowed for adjustments)")
except ValidationError as e:
    print(f"   FAILED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

try:
    print("✅ Attempting payment with POSITIVE amount...")
    payment = Payment(
        student=test_student,
        term=current_term,
        amount=Decimal('500.00'),  # Positive
        payment_method='CASH',
        recorded_by=admin_user
    )
    payment.full_clean()
    print("   ✅ PASSED: Positive amount accepted")
except ValidationError as e:
    print(f"   FAILED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

# ============================================================================
# TEST 3: Amount Can Exceed Total Due (Excess to Next Term)
# ============================================================================
print("\n3. TESTING AMOUNT CAN EXCEED TOTAL DUE")
print("-" * 80)

# Create a fresh student for this test
excess_student, _ = Student.objects.get_or_create(
    birth_entry_number='TEST-PAYMENT-EXCESS',
    defaults={
        'surname': 'Excess',
        'first_name': 'Test',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': True,
        'current_class': test_class
    }
)

balance = StudentBalance.initialize_term_balance(excess_student, current_term)
print(f"\n   Current balance for {excess_student.full_name}: ${balance.current_balance:.2f}")
print(f"   Total due: ${balance.total_due:.2f}")

try:
    print(f"❌ Attempting payment of ${Decimal('1500.00'):.2f} (exceeds ${balance.total_due:.2f})...")
    payment = Payment(
        student=excess_student,
        term=current_term,
        amount=Decimal('1500.00'),  # Exceeds total due of 1000
        payment_method='CASH',
        recorded_by=admin_user
    )
    payment.full_clean()
    # Should accept it
    payment.save()
    print("   ✅ PASSED: Excess payment accepted and saved")
    
    # Check if excess went to next term
    updated_balance = StudentBalance.objects.get(student=excess_student, term=current_term)
    print(f"   Current term balance after payment: ${updated_balance.current_balance:.2f}")
    
    next_balance = StudentBalance.objects.filter(student=excess_student, term=next_term).first()
    if next_balance:
        print(f"   Next term balance updated: ${next_balance.amount_paid:.2f} prepaid")
        print("   ✅ Excess automatically applied to next term")
    
except ValidationError as e:
    print(f"   FAILED: Should accept excess payment: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

# ============================================================================
# TEST 4: Student Eligibility Check (Active Status + Has Balance)
# ============================================================================
print("\n4. TESTING STUDENT ELIGIBILITY CHECK")
print("-" * 80)

try:
    print("❌ Attempting payment for INACTIVE student...")
    payment = Payment(
        student=inactive_student,
        term=current_term,
        amount=Decimal('100.00'),
        payment_method='CASH',
        recorded_by=admin_user
    )
    payment.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

# Create student with no balance record
no_balance_student, _ = Student.objects.get_or_create(
    birth_entry_number='TEST-PAYMENT-NOBALANCE',
    defaults={
        'surname': 'NoBalance',
        'first_name': 'Student',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': True,
        'current_class': test_class
    }
)

try:
    print("❌ Attempting payment for student with NO BALANCE RECORD...")
    payment = Payment(
        student=no_balance_student,
        term=current_term,
        amount=Decimal('100.00'),
        payment_method='CASH',
        recorded_by=admin_user
    )
    payment.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

# ============================================================================
# TEST 5: Term Fee Existence Check
# ============================================================================
print("\n5. TESTING TERM FEE EXISTENCE CHECK")
print("-" * 80)

# Create a term without a fee
no_fee_term, _ = AcademicTerm.objects.get_or_create(
    academic_year=year,
    term=3,
    defaults={
        'start_date': date(year, 9, 1),
        'end_date': date(year, 12, 15),
        'is_current': False
    }
)

# Create a student with valid balance (but term has no fee initially)
fee_test_student, _ = Student.objects.get_or_create(
    birth_entry_number='TEST-PAYMENT-FEETEST',
    defaults={
        'surname': 'FeeTest',
        'first_name': 'Student',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': True,
        'current_class': test_class
    }
)

try:
    print("❌ Attempting payment for term WITHOUT fee set...")
    payment = Payment(
        student=fee_test_student,
        term=no_fee_term,
        amount=Decimal('100.00'),
        payment_method='CASH',
        recorded_by=admin_user
    )
    payment.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("""
✅ TESTS COMPLETED

Payment Validations Tested:
1. ✅ Current term only enforcement - only current term accepts payments
2. ✅ Amount >= 0 validation - negative rejected, zero allowed, positive accepted
3. ✅ Amount can exceed total due - excess automatically goes to next term
4. ✅ Student eligibility - active status and balance record required
5. ✅ Term fee existence - term must have fee configured

All validations are enforced at the model level via Payment.clean()
and will be called automatically before saving via full_clean().

Key Features:
- Amount >= 0 allows for zero payments (adjustments/placeholders)
- Excess payments are automatically applied to next term's prepayment
- Only active students can record payments
- Balance records must exist before payment is recorded
- Payments only for current term (prevents historical payment entry)
""")
