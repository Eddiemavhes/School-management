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

print("\n" + "="*80)
print("TERM FEE & ENROLLMENT VALIDATIONS - COMPREHENSIVE TEST")
print("="*80 + "\n")

# Setup test data
year = 2025
academic_year, _ = AcademicYear.objects.get_or_create(
    year=year,
    defaults={'is_active': True, 'start_date': f'{year}-01-01', 'end_date': f'{year}-12-31'}
)

current_term, _ = AcademicTerm.objects.get_or_create(
    academic_year=year,
    term=1,
    defaults={'start_date': date(year, 1, 15), 'end_date': date(year, 4, 15), 'is_current': True}
)

next_term, _ = AcademicTerm.objects.get_or_create(
    academic_year=year,
    term=2,
    defaults={'start_date': date(year, 5, 1), 'end_date': date(year, 8, 1), 'is_current': False}
)

# Create test terms with specific dates for date validation tests
test_year = 2029
test_academic_year, _ = AcademicYear.objects.get_or_create(
    year=test_year,
    defaults={'is_active': True, 'start_date': f'{test_year}-01-01', 'end_date': f'{test_year}-12-31'}
)

date_test_term1, _ = AcademicTerm.objects.get_or_create(
    academic_year=test_year,
    term=1,
    defaults={'start_date': date(test_year, 1, 15), 'end_date': date(test_year, 4, 15), 'is_current': False}
)

date_test_term2, _ = AcademicTerm.objects.get_or_create(
    academic_year=test_year,
    term=2,
    defaults={'start_date': date(test_year, 5, 1), 'end_date': date(test_year, 8, 1), 'is_current': False}
)

# Clean up existing fees for test terms
TermFee.objects.filter(term__in=[date_test_term1, date_test_term2]).delete()

# Create test class
test_class, _ = Class.objects.get_or_create(
    grade=1,
    section='A',
    academic_year=year
)

# Create admin
admin_user, _ = Administrator.objects.get_or_create(
    email='test@school.com',
    defaults={'first_name': 'Test', 'last_name': 'Admin', 'is_staff': True}
)

# Create test students
regular_student, _ = Student.objects.get_or_create(
    birth_entry_number='TERM-FEE-001',
    defaults={
        'surname': 'Regular',
        'first_name': 'Student',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': True,
        'current_class': test_class,
        'date_enrolled': date(year, 1, 10)
    }
)

late_student, _ = Student.objects.get_or_create(
    birth_entry_number='TERM-FEE-002',
    defaults={
        'surname': 'Late',
        'first_name': 'Student',
        'date_of_birth': '2015-01-01',
        'sex': 'F',
        'is_active': True,
        'current_class': test_class,
        'date_enrolled': date(year, 2, 1)
    }
)

no_class_student, _ = Student.objects.get_or_create(
    birth_entry_number='TERM-FEE-003',
    defaults={
        'surname': 'NoClass',
        'first_name': 'Student',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': True,
        'current_class': None,
        'date_enrolled': date(year, 1, 10)
    }
)

payment_student, _ = Student.objects.get_or_create(
    birth_entry_number='TERM-FEE-PAYMENT',
    defaults={
        'surname': 'Payment',
        'first_name': 'Test',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': True,
        'current_class': test_class,
        'date_enrolled': date(year, 1, 10)
    }
)

print("[SETUP] Test data ready\n")

# TEST 1: Cannot modify fee after payments
print("TEST 1: Cannot modify fee after payments recorded")
print("-" * 80)

tests_passed = 0
tests_failed = 0

# Create term with fee and payment
payment_term, _ = AcademicTerm.objects.get_or_create(
    academic_year=2031,
    term=1,
    defaults={'start_date': date(2031, 1, 1), 'end_date': date(2031, 4, 1), 'is_current': True}
)

payment_next_term, _ = AcademicTerm.objects.get_or_create(
    academic_year=2031,
    term=2,
    defaults={'start_date': date(2031, 5, 1), 'end_date': date(2031, 8, 1), 'is_current': False}
)

# Create fees for both terms
payment_fee, _ = TermFee.objects.get_or_create(
    term=payment_term,
    defaults={'amount': Decimal('1000.00')}
)

next_payment_fee, _ = TermFee.objects.get_or_create(
    term=payment_next_term,
    defaults={'amount': Decimal('1000.00')}
)

# Create balance and payment
StudentBalance.initialize_term_balance(payment_student, payment_term)
payment = Payment.objects.create(
    student=payment_student,
    term=payment_term,
    amount=Decimal('500.00'),
    payment_method='CASH',
    recorded_by=admin_user
)

try:
    payment_fee.amount = Decimal('1500.00')
    payment_fee.full_clean()
    print("[FAIL] Should not allow fee modification after payment")
    tests_failed += 1
except ValidationError:
    print("[PASS] Fee modification after payment correctly blocked")
    tests_passed += 1

# TEST 4: Student balance uniqueness
print("\nTEST 4: Student balance uniqueness per term")
print("-" * 80)

# Create initial balance
balance1, _ = StudentBalance.objects.get_or_create(
    student=regular_student,
    term=next_term,
    defaults={'term_fee': Decimal('1000.00'), 'previous_arrears': Decimal('0.00')}
)

try:
    balance2 = StudentBalance.objects.create(
        student=regular_student,
        term=next_term,
        term_fee=Decimal('1000.00'),
        previous_arrears=Decimal('0.00')
    )
    print("[FAIL] Should prevent duplicate balance creation")
    tests_failed += 1
except (ValidationError, Exception) as e:
    error_str = str(e).lower()
    if 'unique' in error_str or 'duplicate' in error_str or '__all__' in error_str:
        print("[PASS] Uniqueness constraint enforced")
        tests_passed += 1
    else:
        print(f"[ERROR] Unexpected error: {e}")
        tests_failed += 1

# TEST 5: Enrollment status validation
print("\nTEST 5: Enrollment status validation")
print("-" * 80)

try:
    balance = StudentBalance(
        student=no_class_student,
        term=next_term,
        term_fee=Decimal('1000.00'),
        previous_arrears=Decimal('0.00')
    )
    balance.full_clean()
    print("[FAIL] Should reject student without class")
    tests_failed += 1
except ValidationError:
    print("[PASS] Student without class rejected")
    tests_passed += 1

try:
    balance = StudentBalance(
        student=late_student,
        term=current_term,
        term_fee=Decimal('1000.00'),
        previous_arrears=Decimal('0.00')
    )
    balance.full_clean()
    print("[FAIL] Should reject student enrolled after term start")
    tests_failed += 1
except ValidationError:
    print("[PASS] Student enrolled after term start rejected")
    tests_passed += 1

try:
    unique_student, _ = Student.objects.get_or_create(
        birth_entry_number='TERM-FEE-VALID',
        defaults={
            'surname': 'Valid',
            'first_name': 'Student',
            'date_of_birth': '2015-01-01',
            'sex': 'M',
            'is_active': True,
            'current_class': test_class,
            'date_enrolled': date(year, 1, 10)
        }
    )
    balance = StudentBalance(
        student=unique_student,
        term=next_term,
        term_fee=Decimal('1000.00'),
        previous_arrears=Decimal('0.00')
    )
    balance.full_clean()
    print("[PASS] Properly enrolled student accepted")
    tests_passed += 1
except ValidationError as e:
    print(f"[FAIL] Should accept properly enrolled student: {e}")
    tests_failed += 1

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"\nPassed: {tests_passed}")
print(f"Failed: {tests_failed}")
print(f"Total:  {tests_passed + tests_failed}")

if tests_failed == 0:
    print("\n[SUCCESS] All term fee and enrollment validations working correctly!")
else:
    print(f"\n[WARNING] {tests_failed} test(s) failed")
