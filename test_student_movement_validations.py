import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
import django
django.setup()

from core.models import Student, Class, AcademicYear, AcademicTerm, StudentMovement, Administrator
from django.core.exceptions import ValidationError
from decimal import Decimal

print("=" * 80)
print("TESTING STUDENT MOVEMENT VALIDATIONS")
print("=" * 80)

# Setup: Create or get test data
print("\n📋 Setting up test data...")

# Create/get academic year
year = 2025
academic_year, _ = AcademicYear.objects.get_or_create(
    year=year,
    defaults={
        'is_active': True,
        'start_date': f'{year}-01-01',
        'end_date': f'{year}-12-31'
    }
)

# Create/get test classes
class_1a, _ = Class.objects.get_or_create(
    grade=1,
    section='A',
    academic_year=year
)

class_2a, _ = Class.objects.get_or_create(
    grade=2,
    section='A',
    academic_year=year
)

class_1b, _ = Class.objects.get_or_create(
    grade=1,
    section='B',
    academic_year=year
)

# Create test user
admin_user, _ = Administrator.objects.get_or_create(
    email='testadmin@school.com',
    defaults={
        'first_name': 'Test',
        'last_name': 'Admin',
        'is_staff': True,
        'is_superuser': True
    }
)

print("✅ Test data setup complete\n")

# ============================================================================
# TEST 1: Student Prerequisites Validation
# ============================================================================
print("1. TESTING STUDENT PREREQUISITES VALIDATION")
print("-" * 80)

# Create an inactive student
inactive_student, _ = Student.objects.get_or_create(
    birth_entry_number='TEST-INACTIVE-001',
    defaults={
        'surname': 'Inactive',
        'first_name': 'Student',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': False,
        'current_class': class_1a
    }
)

try:
    print("❌ Attempting movement on INACTIVE student...")
    movement = StudentMovement(
        student=inactive_student,
        from_class=class_1a,
        to_class=class_2a,
        movement_type='PROMOTION',
        moved_by=admin_user
    )
    movement.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

# Create student with no class assigned
no_class_student, _ = Student.objects.get_or_create(
    birth_entry_number='TEST-NOCLASS-001',
    defaults={
        'surname': 'NoClass',
        'first_name': 'Student',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': True,
        'current_class': None
    }
)

try:
    print("❌ Attempting movement on student with NO CLASS...")
    movement = StudentMovement(
        student=no_class_student,
        from_class=None,
        to_class=class_1a,
        movement_type='PROMOTION',
        moved_by=admin_user
    )
    movement.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

# Create a graduated student (grade 7 with is_active=False)
class_7a, _ = Class.objects.get_or_create(
    grade=7,
    section='A',
    academic_year=year
)

graduated_student, _ = Student.objects.get_or_create(
    birth_entry_number='TEST-GRADUATED-001',
    defaults={
        'surname': 'Graduated',
        'first_name': 'Student',
        'date_of_birth': '2010-01-01',
        'sex': 'F',
        'is_active': False,
        'current_class': class_7a
    }
)

try:
    print("❌ Attempting movement on GRADUATED/INACTIVE student...")
    movement = StudentMovement(
        student=graduated_student,
        from_class=class_7a,
        to_class=class_1a,
        movement_type='PROMOTION',
        moved_by=admin_user
    )
    movement.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

# ============================================================================
# TEST 2: Promotion Validation
# ============================================================================
print("\n2. TESTING PROMOTION VALIDATION")
print("-" * 80)

# Create a valid active student for promotion
promotion_student, _ = Student.objects.get_or_create(
    birth_entry_number='TEST-PROMOTION-001',
    defaults={
        'surname': 'Promotion',
        'first_name': 'Test',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': True,
        'current_class': class_1a
    }
)

try:
    print("❌ Attempting invalid promotion (same grade)...")
    movement = StudentMovement(
        student=promotion_student,
        from_class=class_1a,
        to_class=class_1b,  # Same grade (1), different section
        movement_type='PROMOTION',
        moved_by=admin_user
    )
    movement.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

try:
    print("❌ Attempting invalid promotion (lower grade)...")
    movement = StudentMovement(
        student=promotion_student,
        from_class=class_2a,  # Simulate from higher grade
        to_class=class_1a,    # To lower grade
        movement_type='PROMOTION',
        moved_by=admin_user
    )
    # Manually set from_class for validation
    promotion_student.current_class = class_2a
    movement.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")
finally:
    # Reset student class
    promotion_student.current_class = class_1a
    promotion_student.save()

try:
    print("✅ Attempting VALID promotion (grade 1 → 2)...")
    movement = StudentMovement(
        student=promotion_student,
        from_class=class_1a,
        to_class=class_2a,
        movement_type='PROMOTION',
        moved_by=admin_user
    )
    movement.full_clean()
    print("   ✅ PASSED: Valid promotion accepted")
except ValidationError as e:
    print(f"   FAILED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

# ============================================================================
# TEST 3: Demotion Validation
# ============================================================================
print("\n3. TESTING DEMOTION VALIDATION")
print("-" * 80)

# Create student for demotion (in grade 2)
demotion_student, _ = Student.objects.get_or_create(
    birth_entry_number='TEST-DEMOTION-001',
    defaults={
        'surname': 'Demotion',
        'first_name': 'Test',
        'date_of_birth': '2014-01-01',
        'sex': 'F',
        'is_active': True,
        'current_class': class_2a
    }
)

try:
    print("❌ Attempting demotion WITHOUT reason...")
    movement = StudentMovement(
        student=demotion_student,
        from_class=class_2a,
        to_class=class_1a,
        movement_type='DEMOTION',
        moved_by=admin_user,
        reason=''  # No reason provided
    )
    movement.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

try:
    print("❌ Attempting invalid demotion (higher grade)...")
    movement = StudentMovement(
        student=demotion_student,
        from_class=class_1a,
        to_class=class_2a,  # Wrong direction (to higher grade)
        movement_type='DEMOTION',
        moved_by=admin_user,
        reason='Poor performance'
    )
    demotion_student.current_class = class_1a
    movement.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")
finally:
    demotion_student.current_class = class_2a
    demotion_student.save()

try:
    print("✅ Attempting VALID demotion (grade 2 → 1 with reason)...")
    movement = StudentMovement(
        student=demotion_student,
        from_class=class_2a,
        to_class=class_1a,
        movement_type='DEMOTION',
        moved_by=admin_user,
        reason='Poor performance in Mathematics'
    )
    movement.full_clean()
    print("   ✅ PASSED: Valid demotion accepted")
except ValidationError as e:
    print(f"   FAILED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

# ============================================================================
# TEST 4: Transfer Validation
# ============================================================================
print("\n4. TESTING TRANSFER VALIDATION")
print("-" * 80)

# Create student for transfer (in grade 1A)
transfer_student, _ = Student.objects.get_or_create(
    birth_entry_number='TEST-TRANSFER-001',
    defaults={
        'surname': 'Transfer',
        'first_name': 'Test',
        'date_of_birth': '2015-01-01',
        'sex': 'M',
        'is_active': True,
        'current_class': class_1a
    }
)

try:
    print("❌ Attempting transfer to DIFFERENT grade...")
    movement = StudentMovement(
        student=transfer_student,
        from_class=class_1a,
        to_class=class_2a,  # Different grade
        movement_type='TRANSFER',
        moved_by=admin_user
    )
    movement.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

try:
    print("✅ Attempting VALID transfer (same grade, different section)...")
    movement = StudentMovement(
        student=transfer_student,
        from_class=class_1a,
        to_class=class_1b,  # Same grade, different section
        movement_type='TRANSFER',
        moved_by=admin_user
    )
    movement.full_clean()
    print("   ✅ PASSED: Valid transfer accepted")
except ValidationError as e:
    print(f"   FAILED: {e.messages[0] if e.messages else str(e)}")
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

Validations Tested:
1. Student prerequisites (active status, has class, not graduated)
2. Promotion validation (grade must increase)
3. Demotion validation (grade must decrease, reason required)
4. Transfer validation (grade must stay same, different class required)

All validations are enforced at the model level via StudentMovement.clean()
and will be called automatically before saving or through full_clean().
""")
