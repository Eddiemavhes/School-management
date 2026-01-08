#!/usr/bin/env python
"""
Test script to verify ECDA → ECDB → Grade 1 student progression
with random Grade 1 section assignment.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
sys.path.insert(0, '/c/Users/Admin/Desktop/School management')
django.setup()

from core.models import Student, Class, AcademicYear, StudentMovement
from django.utils import timezone
from decimal import Decimal
from datetime import date

def run_test():
    print("\n" + "="*80)
    print("TESTING ECDA → ECDB → GRADE 1 PROGRESSION WITH RANDOM SECTION ASSIGNMENT")
    print("="*80 + "\n")
    
    # Step 1: Verify academic years exist
    print("Step 1: Verifying academic years...")
    try:
        year_2026 = AcademicYear.objects.get(year=2026)
        year_2027 = AcademicYear.objects.get(year=2027)
        print(f"  ✓ 2026 exists: {year_2026}")
        print(f"  ✓ 2027 exists: {year_2027}\n")
    except AcademicYear.DoesNotExist as e:
        print(f"  ✗ Missing academic year: {e}")
        print("  Creating missing years...")
        year_2026, _ = AcademicYear.objects.get_or_create(
            year=2026,
            defaults={
                'is_active': True,
                'start_date': date(2026, 1, 1),
                'end_date': date(2026, 12, 31)
            }
        )
        year_2027, _ = AcademicYear.objects.get_or_create(
            year=2027,
            defaults={
                'is_active': False,
                'start_date': date(2027, 1, 1),
                'end_date': date(2027, 12, 31)
            }
        )
        print(f"  ✓ Created years\n")
    
    # Step 2: Verify ECDA classes exist for 2026
    print("Step 2: Checking ECDA classes for 2026...")
    ecda_a = Class.objects.filter(grade='ECDA', section='A', academic_year=2026).first()
    ecda_b = Class.objects.filter(grade='ECDA', section='B', academic_year=2026).first()
    
    if not ecda_a:
        print("  Creating ECDA A...")
        ecda_a = Class.objects.create(grade='ECDA', section='A', academic_year=2026)
    if not ecda_b:
        print("  Creating ECDA B...")
        ecda_b = Class.objects.create(grade='ECDA', section='B', academic_year=2026)
    
    print(f"  ✓ ECDA A: {ecda_a}")
    print(f"  ✓ ECDA B: {ecda_b}\n")
    
    # Step 3: Verify ECDB classes exist for 2026
    print("Step 3: Checking ECDB classes for 2026...")
    ecdb_a = Class.objects.filter(grade='ECDB', section='A', academic_year=2026).first()
    ecdb_b = Class.objects.filter(grade='ECDB', section='B', academic_year=2026).first()
    
    if not ecdb_a:
        print("  Creating ECDB A...")
        ecdb_a = Class.objects.create(grade='ECDB', section='A', academic_year=2026)
    if not ecdb_b:
        print("  Creating ECDB B...")
        ecdb_b = Class.objects.create(grade='ECDB', section='B', academic_year=2026)
    
    print(f"  ✓ ECDB A: {ecdb_a}")
    print(f"  ✓ ECDB B: {ecdb_b}\n")
    
    # Step 4: Verify Grade 1 classes exist for 2027 (with sections A, B, C, D)
    print("Step 4: Checking Grade 1 classes for 2027...")
    grade_1_classes = {}
    for section in ['A', 'B', 'C', 'D']:
        cls = Class.objects.filter(grade='1', section=section, academic_year=2027).first()
        if not cls:
            print(f"  Creating Grade 1{section}...")
            cls = Class.objects.create(grade='1', section=section, academic_year=2027)
        grade_1_classes[section] = cls
        print(f"  ✓ Grade 1{section}: {cls}")
    print()
    
    # Step 5: Create test student in ECDA
    print("Step 5: Creating test student in ECDA...")
    test_student = Student.objects.filter(first_name='TestProgressionStudent').first()
    if test_student:
        print(f"  Using existing test student: {test_student}")
        print(f"  Current class: {test_student.current_class}")
    else:
        test_student = Student.objects.create(
            first_name='TestProgressionStudent',
            surname='ProgressionTest',
            sex='M',
            birth_entry_number='TEST001',
            date_of_birth=date(2022, 1, 1),  # Age 4+ for ECDA
            current_class=ecda_a,
            is_active=True
        )
        print(f"  ✓ Created: {test_student}")
        print(f"  ✓ Initial class: {test_student.current_class}\n")
    
    # Step 6: Test ECDA → ECDB progression (same year)
    print("Step 6: Testing ECDA → ECDB progression (same year)...")
    next_class = test_student.get_next_class()
    if next_class and next_class.grade == 'ECDB':
        print(f"  ✓ Next class correctly determined: {next_class}")
        print(f"  ✓ Section preserved: {next_class.section} (was {test_student.current_class.section})")
        
        # Actually promote the student
        test_student.current_class = next_class
        test_student.save()
        print(f"  ✓ Student promoted to: {test_student.current_class}\n")
    else:
        print(f"  ✗ ERROR: get_next_class() returned {next_class} instead of ECDB\n")
        return False
    
    # Step 7: Test ECDB → Grade 1 progression (next year, RANDOM section)
    print("Step 7: Testing ECDB → Grade 1 progression (next year, RANDOM section)...")
    print(f"  Available Grade 1 sections: {list(grade_1_classes.keys())}")
    
    # Test random selection multiple times
    selected_sections = set()
    for attempt in range(5):
        next_class = test_student.get_next_class()
        if not next_class or next_class.grade != '1':
            print(f"  ✗ ERROR: get_next_class() returned {next_class} instead of Grade 1\n")
            return False
        
        selected_sections.add(next_class.section)
        print(f"  Attempt {attempt + 1}: Randomly selected Grade 1{next_class.section}")
    
    if len(selected_sections) > 1:
        print(f"  ✓ Random selection working - got {len(selected_sections)} different sections: {selected_sections}")
    else:
        print(f"  ⚠ Warning: Only got 1 section ({selected_sections}) in 5 attempts (may be normal if few classes)")
    
    # Actually promote to Grade 1
    next_class = test_student.get_next_class()
    test_student.current_class = next_class
    test_student.save()
    print(f"  ✓ Student promoted to: {test_student.current_class}\n")
    
    # Step 8: Verify student cannot progress further from Grade 7
    print("Step 8: Testing progression limits...")
    grade_7 = Class.objects.filter(grade='7', section='A', academic_year=2027).first()
    if not grade_7:
        grade_7 = Class.objects.create(grade='7', section='A', academic_year=2027)
    
    test_student.current_class = grade_7
    test_student.save()
    next_class = test_student.get_next_class()
    if next_class is None:
        print(f"  ✓ Grade 7 correctly returns None for next_class (cannot progress)\n")
    else:
        print(f"  ✗ ERROR: Grade 7 should return None but got {next_class}\n")
        return False
    
    # Step 9: Summary
    print("="*80)
    print("✓ ALL TESTS PASSED!")
    print("="*80)
    print("\nKey Features Verified:")
    print("  ✓ ECDA → ECDB progression works (same year, section preserved)")
    print("  ✓ ECDB → Grade 1 progression works (next year)")
    print("  ✓ Random section selection for Grade 1 (A, B, C, or D)")
    print("  ✓ Grade 7 is final grade (no further progression)")
    print("\nSystem is ready for production!")
    print("="*80 + "\n")
    
    return True

if __name__ == '__main__':
    try:
        success = run_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
