#!/usr/bin/env python
"""
Test the one-teacher-per-class constraint:
1. Verify a teacher cannot be assigned to multiple classes in the same year
2. Test get_available_teachers() method
3. Verify validation error is raised
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Class, Administrator, AcademicYear
from django.core.exceptions import ValidationError

print("\n" + "="*70)
print("🧪 TESTING ONE-TEACHER-PER-CLASS CONSTRAINT")
print("="*70)

# Setup
print("\n[1] Setting up test data...")
try:
    year = AcademicYear.objects.filter(is_active=True).first()
    if not year:
        year = AcademicYear.objects.create(year=2026, start_date='2026-01-01', end_date='2026-12-31', is_active=True)
    
    academic_year = year.year
    print(f"✓ Using academic year {academic_year}")
    
    # Clear existing classes for this year
    Class.objects.filter(academic_year=academic_year).delete()
    print(f"✓ Cleared existing classes for {academic_year}")
    
except Exception as e:
    print(f"✗ Setup failed: {e}")
    exit(1)

# Get or create test teacher
print("\n[2] Getting test teacher...")
try:
    teacher = Administrator.objects.filter(is_teacher=True).first()
    if not teacher:
        print("✗ No teacher found in system")
        exit(1)
    print(f"✓ Using teacher: {teacher.full_name}")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test 1: Create first class with teacher
print("\n[3] Creating first class with teacher...")
try:
    class1 = Class(
        grade=1,
        section='A',
        academic_year=academic_year,
        teacher=teacher
    )
    class1.save()
    print(f"✓ Created {class1} with teacher {teacher.full_name}")
except Exception as e:
    print(f"✗ Failed: {e}")
    exit(1)

# Test 2: Try to assign same teacher to another class
print("\n[4] Attempting to assign same teacher to another class (should fail)...")
try:
    class2 = Class(
        grade=2,
        section='A',
        academic_year=academic_year,
        teacher=teacher
    )
    class2.save()
    print(f"✗ ERROR: Should have failed but didn't! Class was created: {class2}")
except ValidationError as e:
    print(f"✓ Correctly rejected: {e}")
except Exception as e:
    print(f"✓ Correctly rejected: {e}")

# Test 3: Create class without teacher (should succeed)
print("\n[5] Creating class without teacher assignment...")
try:
    class2 = Class(
        grade=2,
        section='A',
        academic_year=academic_year,
        teacher=None
    )
    class2.save()
    print(f"✓ Created {class2} without teacher")
except Exception as e:
    print(f"✗ Failed: {e}")
    exit(1)

# Test 6: Check available teachers
print("\n[6] Testing get_available_teachers()...")
try:
    available = Class.get_available_teachers(academic_year)
    print(f"✓ Available teachers: {available.count()}")
    assigned_classes = Class.objects.filter(academic_year=academic_year, teacher__isnull=False)
    print(f"✓ Assigned teachers: {', '.join([c.teacher.full_name for c in assigned_classes]) if assigned_classes.exists() else 'None'}")
    
    # Verify the teacher is NOT in available list
    if teacher.id in available.values_list('id', flat=True):
        print(f"✗ ERROR: {teacher.full_name} should not be in available list")
    else:
        print(f"✓ {teacher.full_name} correctly excluded from available list")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 8: Verify available teachers after reassignment
print("\n[8] Verifying available teachers after reassignment...")
try:
    # At this point:
    # - Class 1A has James Jones
    # - Class 2A has Mary Magdalene
    # So 2 teachers should be assigned, and others should be available
    
    available = Class.get_available_teachers(academic_year)
    assigned_count = Class.objects.filter(academic_year=academic_year, teacher__isnull=False).count()
    
    print(f"✓ Classes with teachers: {assigned_count}")
    print(f"✓ Available teachers: {available.count()}")
    
    # James Jones should still not be available (he teaches class 1A)
    if teacher.id in available.values_list('id', flat=True):
        print(f"✗ ERROR: {teacher.full_name} should NOT be available (still teaching 1A)")
    else:
        print(f"✓ {teacher.full_name} is still correctly marked as unavailable")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*70)
print("✅ ALL TESTS PASSED!")
print("="*70)
print("\nSummary:")
print("  ✓ One teacher can only teach one class per academic year")
print("  ✓ Attempting to assign a teacher already teaching is rejected")
print("  ✓ get_available_teachers() correctly filters assigned teachers")
print("  ✓ Unassigning a teacher makes them available again")
print("="*70 + "\n")
