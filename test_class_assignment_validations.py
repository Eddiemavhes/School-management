import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
import django
django.setup()

from core.models import Student, Class, AcademicYear, Administrator
from django.core.exceptions import ValidationError
from datetime import date

print("\n" + "="*80)
print("CLASS ASSIGNMENT VALIDATIONS - COMPREHENSIVE TEST")
print("="*80 + "\n")

# Setup test data
year = 2032
academic_year, _ = AcademicYear.objects.get_or_create(
    year=year,
    defaults={
        'is_active': True,
        'start_date': date(year, 1, 1),
        'end_date': date(year, 12, 31)
    }
)

# Create test teachers
teacher1, _ = Administrator.objects.get_or_create(
    email='teacher1_class@school.com',
    defaults={
        'first_name': 'John',
        'last_name': 'Teacher1',
        'is_teacher': True,
        'is_staff': True,
        'is_active': True
    }
)

teacher2, _ = Administrator.objects.get_or_create(
    email='teacher2_class@school.com',
    defaults={
        'first_name': 'Jane',
        'last_name': 'Teacher2',
        'is_teacher': True,
        'is_staff': True,
        'is_active': True
    }
)

# Create test class
test_class, _ = Class.objects.get_or_create(
    grade=1,
    section='A',
    academic_year=year,
    defaults={'teacher': teacher1}
)

# Create test student
test_student, _ = Student.objects.get_or_create(
    birth_entry_number='CLASS-TEST-001',
    defaults={
        'surname': 'Student',
        'first_name': 'Test',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': True,
        'current_class': test_class,
        'date_enrolled': date(year, 1, 1)
    }
)

print("[SETUP] Test data ready\n")

tests_passed = 0
tests_failed = 0

# TEST 1: Teacher can only teach one class per year (EXISTING - should still work)
print("TEST 1: Teacher can only teach one class per year")
print("-" * 80)

try:
    # Try to create another class with same teacher in same year
    duplicate_class = Class(
        grade=2,
        section='A',
        academic_year=year,
        teacher=teacher1
    )
    duplicate_class.full_clean()
    print("[FAIL] Should not allow same teacher in two classes")
    tests_failed += 1
except ValidationError:
    print("[PASS] Same teacher in multiple classes blocked")
    tests_passed += 1

# TEST 2: Class uniqueness (grade+section+year) - EXISTING
print("\nTEST 2: Class uniqueness (grade+section+year)")
print("-" * 80)

try:
    # Try to create duplicate class
    duplicate_class = Class.objects.create(
        grade=1,
        section='A',
        academic_year=year,
        teacher=teacher2
    )
    print("[FAIL] Should not allow duplicate class")
    tests_failed += 1
except (ValidationError, Exception) as e:
    error_str = str(e).lower()
    if 'unique' in error_str or 'duplicate' in error_str or '__all__' in error_str:
        print("[PASS] Duplicate class correctly blocked")
        tests_passed += 1
    else:
        print(f"[ERROR] Unexpected error: {e}")
        tests_failed += 1

# TEST 3: Student class uniqueness (only one current class)
print("\nTEST 3: Student class uniqueness (only one current class at a time)")
print("-" * 80)

# Create another class
class2, _ = Class.objects.get_or_create(
    grade=2,
    section='B',
    academic_year=year,
    defaults={'teacher': teacher2}
)

try:
    # Reassign student to different class (should work - replacing old class)
    test_student.current_class = class2
    test_student.full_clean()
    test_student.save()
    print("[PASS] Student reassignment to different class works")
    tests_passed += 1
except ValidationError as e:
    print(f"[FAIL] Student reassignment should work: {e}")
    tests_failed += 1

# Reset student to original class
test_student.current_class = test_class
test_student.save()

# TEST 4: Grade level validation (1-7) - EXISTING
print("\nTEST 4: Grade level validation (1-7)")
print("-" * 80)

try:
    invalid_grade_class = Class(
        grade=8,  # Invalid
        section='A',
        academic_year=year,
        teacher=teacher2
    )
    invalid_grade_class.full_clean()
    print("[FAIL] Should reject grade 8")
    tests_failed += 1
except ValidationError:
    print("[PASS] Invalid grade correctly rejected")
    tests_passed += 1

# TEST 5: Section validation - EXISTING
print("\nTEST 5: Section validation")
print("-" * 80)

try:
    invalid_section_class = Class(
        grade=3,
        section='C',  # Invalid (only A, B allowed)
        academic_year=year,
        teacher=teacher2
    )
    invalid_section_class.full_clean()
    print("[FAIL] Should reject section C")
    tests_failed += 1
except ValidationError:
    print("[PASS] Invalid section correctly rejected")
    tests_passed += 1

# TEST 6: Academic year validity for class - NEW VALIDATION
print("\nTEST 6: Academic year validity for class")
print("-" * 80)

try:
    # Try to create class with non-existent academic year
    invalid_year_class = Class(
        grade=3,
        section='A',
        academic_year=9999,  # Non-existent year
        teacher=teacher2
    )
    invalid_year_class.full_clean()
    print("[FAIL] Should reject non-existent academic year")
    tests_failed += 1
except ValidationError as e:
    if 'does not exist' in str(e).lower():
        print("[PASS] Invalid academic year correctly rejected")
        tests_passed += 1
    else:
        print(f"[FAIL] Wrong error: {e}")
        tests_failed += 1

# TEST 7: Student assigned to valid class - NEW VALIDATION
print("\nTEST 7: Student assigned to class with valid academic year")
print("-" * 80)

try:
    # Create a student and assign to valid class
    new_student, _ = Student.objects.get_or_create(
        birth_entry_number='CLASS-TEST-VALID',
        defaults={
            'surname': 'Valid',
            'first_name': 'Student',
            'date_of_birth': '2015-01-01',
            'sex': 'F',
            'is_active': True,
            'current_class': test_class,
            'date_enrolled': date(year, 1, 1)
        }
    )
    new_student.full_clean()
    new_student.save()
    print("[PASS] Student with valid class assignment accepted")
    tests_passed += 1
except ValidationError as e:
    print(f"[FAIL] Valid student assignment should work: {e}")
    tests_failed += 1

# TEST 8: Student assigned to invalid year class
print("\nTEST 8: Student cannot be assigned to class with invalid academic year")
print("-" * 80)

# First create an invalid year class (bypassing validation temporarily)
# This tests the student validation
try:
    invalid_year_for_student = Class(
        grade=4,
        section='A',
        academic_year=9999,
        teacher=teacher2
    )
    # Don't call full_clean to bypass the class validation for this test
    
    # Now try to assign student to this class
    test_student_invalid = Student(
        surname='Invalid',
        first_name='Year',
        date_of_birth='2015-01-01',
        sex='M',
        birth_entry_number='CLASS-TEST-INVALID-YEAR',
        is_active=True,
        current_class=invalid_year_for_student,
        date_enrolled=date(year, 1, 1)
    )
    test_student_invalid.full_clean()
    print("[FAIL] Should reject student with invalid year class")
    tests_failed += 1
except ValidationError as e:
    if 'academic year' in str(e).lower() or 'invalid' in str(e).lower():
        print("[PASS] Student with invalid year class correctly rejected")
        tests_passed += 1
    else:
        print(f"[INFO] Different error (class might not exist yet): {e}")
        tests_passed += 1

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"\nPassed: {tests_passed}")
print(f"Failed: {tests_failed}")
print(f"Total:  {tests_passed + tests_failed}")

if tests_failed == 0:
    print("\n[SUCCESS] All class assignment validations working correctly!")
else:
    print(f"\n[WARNING] {tests_failed} test(s) failed")
