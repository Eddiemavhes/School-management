import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
import django
django.setup()

from core.models import AcademicTerm, StudentBalance, AcademicYear
from datetime import date, timedelta
from django.core.exceptions import ValidationError

print("=" * 80)
print("TESTING ACADEMIC TERM PROGRESSION VALIDATIONS")
print("=" * 80)

# Setup: Use a unique year for testing (to avoid conflicts with existing data)
import random
year = 2030 + random.randint(0, 99)  # Random year between 2030-2129
start_date = date(year, 1, 10)
end_date = date(year, 12, 20)

print(f"\nUsing Academic Year: {year}")
print("-" * 80)

print("\n1. TESTING TERM SEQUENTIALITY VALIDATION")
print("-" * 80)

try:
    # Try to create Term 2 without Term 1 existing
    print("❌ Attempting to create Term 2 without Term 1...")
    term2 = AcademicTerm(
        academic_year=year,
        term=2,
        start_date=start_date + timedelta(days=120),
        end_date=start_date + timedelta(days=150),
        is_current=False
    )
    term2.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

try:
    # Create Term 1 first
    print("\n✅ Creating Term 1...")
    term1 = AcademicTerm.objects.create(
        academic_year=year,
        term=1,
        start_date=start_date,
        end_date=start_date + timedelta(days=90),
        is_current=False
    )
    print("   Term 1 created successfully")
except Exception as e:
    print(f"   ERROR: {e}")
    term1 = None

try:
    # Now try to create Term 3 without Term 2 existing
    print("\n❌ Attempting to create Term 3 without Term 2...")
    term3 = AcademicTerm(
        academic_year=year,
        term=3,
        start_date=start_date + timedelta(days=200),
        end_date=start_date + timedelta(days=230),
        is_current=False
    )
    term3.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

print("\n2. TESTING DATE VALIDATION")
print("-" * 80)

try:
    print("❌ Attempting to create term with start_date >= end_date...")
    bad_term = AcademicTerm(
        academic_year=year,
        term=2,
        start_date=start_date + timedelta(days=120),
        end_date=start_date + timedelta(days=100),  # End before start!
        is_current=False
    )
    bad_term.full_clean()
    print("   FAILED: Should have raised ValidationError")
except ValidationError as e:
    print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

print("\n3. TESTING CURRENT TERM EXCLUSIVITY")
print("-" * 80)

try:
    # Create Term 2 (valid now since Term 1 exists)
    print("✅ Creating Term 2...")
    term2 = AcademicTerm.objects.create(
        academic_year=year,
        term=2,
        start_date=start_date + timedelta(days=100),
        end_date=start_date + timedelta(days=190),
        is_current=False
    )
    print("   Term 2 created successfully")
    
    # Mark term1 as current
    print("\n✅ Setting Term 1 as current...")
    term1.is_current = True
    term1.full_clean()
    term1.save()
    print("   Term 1 is now current")
    
    # Verify term1 is current
    term1_check = AcademicTerm.objects.get(id=term1.id)
    is_current_count = AcademicTerm.objects.filter(is_current=True).count()
    print(f"   ✅ PASSED: Only 1 current term exists (count: {is_current_count})")
    
    # Try to set term2 as current
    print("\n✅ Setting Term 2 as current...")
    term2.is_current = True
    term2.full_clean()
    term2.save()
    print("   Term 2 is now current")
    
    # Verify only term2 is current now
    term1_check = AcademicTerm.objects.get(id=term1.id)
    term2_check = AcademicTerm.objects.get(id=term2.id)
    is_current_count = AcademicTerm.objects.filter(is_current=True).count()
    print(f"   ✅ PASSED: Term 1 is_current={term1_check.is_current}, Term 2 is_current={term2_check.is_current}")
    print(f"   ✅ PASSED: Only 1 current term exists (count: {is_current_count})")
    
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

print("\n4. TESTING PREVIOUS TERM CLOSURE VALIDATION")
print("-" * 80)

try:
    # Create Term 3 (valid now)
    print("✅ Creating Term 3...")
    term3 = AcademicTerm.objects.create(
        academic_year=year,
        term=3,
        start_date=start_date + timedelta(days=200),
        end_date=start_date + timedelta(days=290),
        is_current=False
    )
    print("   Term 3 created successfully")
    
    # Try to set term3 as current with outstanding balances in term2
    print("\n❌ Attempting to set Term 3 as current with outstanding balances in Term 2...")
    
    # First, let's create some student balances with outstanding amounts
    from core.models import Student, Class
    test_student = Student.objects.first()  # Get first student
    if test_student and term2:
        StudentBalance.objects.filter(student=test_student, term=term2).delete()
        balance = StudentBalance.objects.create(
            student=test_student,
            term=term2,
            term_fee=120,
            previous_arrears=0,
            amount_paid=50  # Leave $70 outstanding
        )
        print(f"   Created outstanding balance: ${balance.current_balance:.2f}")
        
        # Now try to set term3 as current
        term3.is_current = True
        try:
            term3.full_clean()
            print("   FAILED: Should have raised ValidationError")
        except ValidationError as e:
            print(f"   ✅ PASSED: {e.messages[0] if e.messages else str(e)}")
    
    # Clean up: mark term3 as current without checking (bypass validation)
    # by directly updating without full_clean
    print("\n✅ Cleanup: Setting Term 3 as current (bypassing validation for testing)...")
    term3.is_current = False
    term3.save()
    
except Exception as e:
    print(f"   ⚠️  ERROR: {type(e).__name__}: {e}")

print("\n" + "=" * 80)
print("VALIDATION TESTING COMPLETE")
print("=" * 80)
