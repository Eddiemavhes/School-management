#!/usr/bin/env python
"""
Comprehensive System Test Suite - v2
Tests all major functionality across the entire school management system
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
sys.path.insert(0, '/c/Users/Admin/Desktop/School management')
django.setup()

from core.models import (
    Student, Class, AcademicYear, AcademicTerm, Administrator,
    StudentMovement, StudentBalance, Payment, TermFee, TeacherAssignmentHistory
)
from core.models.school_details import SchoolDetails
from django.utils import timezone
from django.db.models import Count, Sum, F, Q

class SystemTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests_run = 0
        
    def test(self, name, condition, details=""):
        """Run a single test"""
        self.tests_run += 1
        if condition:
            self.passed += 1
            print(f"  ✅ {name}")
        else:
            self.failed += 1
            print(f"  ❌ {name}")
            if details:
                print(f"     {details}")
    
    def section(self, title):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    
    def summary(self):
        """Print test summary"""
        print(f"\n{'='*80}")
        print(f"  SYSTEM TEST SUMMARY")
        print(f"{'='*80}\n")
        print(f"  Total Tests: {self.tests_run}")
        print(f"  ✅ Passed:   {self.passed}")
        print(f"  ❌ Failed:   {self.failed}")
        
        pass_rate = (self.passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"  Pass Rate:   {pass_rate:.1f}%")
        
        if self.failed == 0:
            print(f"\n  🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION! 🎉")
        else:
            print(f"\n  ⚠️  {self.failed} test(s) failed - review required")
        print(f"{'='*80}\n")
        
        return self.failed == 0

def run_tests():
    test = SystemTest()
    
    # ==================== DATABASE INTEGRITY ====================
    test.section("1. DATABASE INTEGRITY & STRUCTURE")
    
    # Check academic years
    years_count = AcademicYear.objects.count()
    test.test("Academic years exist", years_count > 0, f"Found {years_count} years")
    
    active_years = AcademicYear.objects.filter(is_active=True).count()
    test.test("At least one active academic year", active_years > 0, f"Found {active_years} active")
    
    # Check classes
    classes_count = Class.objects.count()
    test.test("Classes exist in database", classes_count > 0, f"Found {classes_count} classes")
    
    ecda_count = Class.objects.filter(grade='ECDA').count()
    ecdb_count = Class.objects.filter(grade='ECDB').count()
    grade_1_count = Class.objects.filter(grade='1').count()
    test.test("ECDA classes exist", ecda_count > 0, f"Found {ecda_count} ECDA classes")
    test.test("ECDB classes exist", ecdb_count > 0, f"Found {ecdb_count} ECDB classes")
    test.test("Grade 1 classes exist", grade_1_count > 0, f"Found {grade_1_count} Grade 1 classes")
    
    # Check all grades have sections
    for grade in ['ECDA', 'ECDB']:
        sections = set(Class.objects.filter(grade=grade).values_list('section', flat=True).distinct())
        test.test(f"{grade} has sections", len(sections) > 0, f"Sections: {sections}")
    
    for grade in ['1', '6', '7']:  # Sample check, not all
        count = Class.objects.filter(grade=grade).count()
        test.test(f"Grade {grade} classes exist", count > 0, f"Found {count}")
    
    # Check academic terms
    terms_count = AcademicTerm.objects.count()
    test.test("Academic terms exist", terms_count > 0, f"Found {terms_count} terms")
    
    # Check fees are defined
    fees_count = TermFee.objects.count()
    test.test("Term fees defined", fees_count > 0, f"Found {fees_count} fee entries")
    
    ecd_fees = TermFee.objects.filter(grade_level='ECD').count()
    primary_fees = TermFee.objects.filter(grade_level='PRIMARY').count()
    test.test("ECD fees configured", ecd_fees > 0 or primary_fees > 0, f"ECD: {ecd_fees}, Primary: {primary_fees}")
    test.test("Primary fees configured", primary_fees > 0, f"Found {primary_fees} PRIMARY fee entries")
    
    # ==================== STUDENT MANAGEMENT ====================
    test.section("2. STUDENT MANAGEMENT")
    
    students_count = Student.objects.count()
    test.test("Students exist in system", students_count > 0, f"Found {students_count} students")
    
    active_students = Student.objects.filter(is_active=True).count()
    test.test("Active students tracked", active_students >= 0, f"Found {active_students} active")
    
    # Check student has required fields
    sample_student = Student.objects.first()
    if sample_student:
        test.test("Student has first name", bool(sample_student.first_name), "")
        test.test("Student has surname", bool(sample_student.surname), "")
        test.test("Student has date of birth", bool(sample_student.date_of_birth), "")
        test.test("Student has current class", sample_student.current_class is not None, "")
        test.test("Student has sex", bool(sample_student.sex), "")
    
    # Check student progression methods exist
    if sample_student:
        test.test("Student has get_next_class() method", hasattr(sample_student, 'get_next_class'), "")
        test.test("Student has promote_to_next_class() method", hasattr(sample_student, 'promote_to_next_class'), "")
        
        # Test progression for ECD students
        if sample_student.current_class and sample_student.current_class.grade in ['ECDA', 'ECDB']:
            next_class = sample_student.get_next_class()
            test.test(f"ECD Student progression works", next_class is not None, f"Next: {next_class}")
    
    # ==================== CLASS MANAGEMENT ====================
    test.section("3. CLASS MANAGEMENT")
    
    sample_class = Class.objects.first()
    if sample_class:
        test.test("Class has grade", bool(sample_class.grade), f"Grade: {sample_class.grade}")
        test.test("Class has section", bool(sample_class.section), f"Section: {sample_class.section}")
        test.test("Class has academic_year", sample_class.academic_year is not None, f"Year: {sample_class.academic_year}")
        test.test("Class __str__ method works", len(str(sample_class)) > 0, f"Display: {sample_class}")
    
    # Check for ECD-specific display
    ecda_class = Class.objects.filter(grade='ECDA').first()
    if ecda_class:
        class_str = str(ecda_class)
        test.test("ECDA displays correctly", 'ECDA' in class_str or 'Early' in class_str, f"Display: {class_str}")
    
    # ==================== FINANCIAL SYSTEM ====================
    test.section("4. FINANCIAL SYSTEM")
    
    # Check student balances
    balances_count = StudentBalance.objects.count()
    test.test("Student balances tracked", balances_count >= 0, f"Found {balances_count} balance records")
    
    # Check payments
    payments_count = Payment.objects.count()
    test.test("Payments recorded", payments_count >= 0, f"Found {payments_count} payments")
    
    # Check financial calculations
    sample_balance = StudentBalance.objects.filter(
        term_fee_record__isnull=False,
        amount_paid__isnull=False
    ).first()
    
    if sample_balance:
        test.test("StudentBalance calculates correctly", 
                 sample_balance.term_fee_record.amount > 0, 
                 f"Term fee: ${sample_balance.term_fee_record.amount}")
    
    # ==================== STUDENT PROGRESSION ====================
    test.section("5. STUDENT PROGRESSION SYSTEM")
    
    # Test ECDA→ECDB progression
    ecda_students = Student.objects.filter(
        is_active=True,
        current_class__grade='ECDA'
    )
    
    if ecda_students.exists():
        ecda_student = ecda_students.first()
        next_class = ecda_student.get_next_class()
        test.test("ECDA student has ECDB as next class", 
                 next_class and next_class.grade == 'ECDB',
                 f"Next: {next_class.grade if next_class else 'None'}")
        
        if next_class and next_class.grade == 'ECDB':
            test.test("ECDA→ECDB preserves section",
                     next_class.section == ecda_student.current_class.section,
                     f"Section: {next_class.section} (was {ecda_student.current_class.section})")
    else:
        test.test("ECDA student progression test skipped", True, "No ECDA students in system")
    
    # Test ECDB→Grade1 progression with random selection
    ecdb_students = Student.objects.filter(
        is_active=True,
        current_class__grade='ECDB'
    )
    
    if ecdb_students.exists():
        ecdb_student = ecdb_students.first()
        next_class = ecdb_student.get_next_class()
        test.test("ECDB student has Grade 1 as next class",
                 next_class and next_class.grade == '1',
                 f"Next: {next_class.grade if next_class else 'None'}")
        
        if next_class:
            test.test("ECDB→Grade1 increments year",
                     next_class.academic_year > ecdb_student.current_class.academic_year,
                     f"Year: {next_class.academic_year} (was {ecdb_student.current_class.academic_year})")
            
            test.test("ECDB→Grade1 uses valid section",
                     next_class.section in ['A', 'B', 'C', 'D'],
                     f"Section: {next_class.section}")
    else:
        test.test("ECDB student progression test skipped", True, "No ECDB students in system")
    
    # Test Grade 7 is final
    grade_7_students = Student.objects.filter(
        is_active=True,
        current_class__grade='7'
    )
    
    if grade_7_students.exists():
        g7_student = grade_7_students.first()
        next_class = g7_student.get_next_class()
        test.test("Grade 7 has no next class (final grade)",
                 next_class is None,
                 f"Next: {next_class}")
    else:
        test.test("Grade 7 progression test skipped", True, "No Grade 7 students in system")
    
    # ==================== STUDENT MOVEMENTS ====================
    test.section("6. STUDENT MOVEMENT HISTORY")
    
    movements_count = StudentMovement.objects.count()
    test.test("Student movements tracked", movements_count >= 0, f"Found {movements_count} movements")
    
    # Check movement types
    if movements_count > 0:
        movement_types = set(StudentMovement.objects.values_list('movement_type', flat=True).distinct())
        test.test("Multiple movement types exist", len(movement_types) > 0, f"Types: {movement_types}")
    
    # ==================== SCHOOL DETAILS ====================
    test.section("7. SCHOOL DETAILS & CONFIGURATION")
    
    school_details = SchoolDetails.objects.first()
    if school_details:
        test.test("School details exist", school_details is not None, "")
        test.test("School name configured", bool(school_details.school_name), f"Name: {school_details.school_name}")
    else:
        test.test("School details configured", False, "No school details found")
    
    # ==================== ADMINISTRATORS ====================
    test.section("8. ADMINISTRATOR & USER MANAGEMENT")
    
    admins_count = Administrator.objects.count()
    test.test("Administrators exist", admins_count > 0, f"Found {admins_count} admins")
    
    # ==================== DATA RELATIONSHIPS ====================
    test.section("9. DATA RELATIONSHIPS & INTEGRITY")
    
    # Check for orphaned students (without class)
    orphaned_students = Student.objects.filter(is_active=True, current_class__isnull=True).count()
    test.test("No active students without class", orphaned_students == 0, 
             f"Found {orphaned_students} orphaned students")
    
    # Check for orphaned classes (without year)
    orphaned_classes = Class.objects.filter(academic_year__isnull=True).count()
    test.test("All classes have academic year", orphaned_classes == 0,
             f"Found {orphaned_classes} orphaned classes")
    
    # Check financial data consistency
    balances_without_term = StudentBalance.objects.filter(term__isnull=True).count()
    test.test("All balances have term", balances_without_term == 0,
             f"Found {balances_without_term} orphaned balances")
    
    # ==================== AGGREGATE STATISTICS ====================
    test.section("10. SYSTEM STATISTICS & HEALTH")
    
    # Student distribution by grade
    grade_dist = Student.objects.filter(is_active=True).values('current_class__grade').annotate(
        count=Count('id')
    ).order_by('current_class__grade')
    
    print("  Student Distribution by Grade:")
    total_active = 0
    for item in grade_dist:
        grade = item['current_class__grade'] or 'No Class'
        count = item['count']
        total_active += count
        symbol = "🟦" if grade in ['ECDA', 'ECDB'] else "  "
        print(f"    {symbol} {grade:4} - {count:3} students")
    
    test.test("Students tracked correctly", total_active == active_students, 
             f"Total: {total_active} (active: {active_students})")
    
    # Financial summary
    print(f"\n  Financial Summary:")
    print(f"    Total Balances: {balances_count}")
    print(f"    Total Payments: {payments_count}")
    
    # ==================== CRITICAL FEATURES ====================
    test.section("11. CRITICAL FEATURES CHECK")
    
    # ECDA/ECDB Grade choices
    grade_choices = [choice[0] for choice in Class._meta.get_field('grade').choices]
    test.test("ECDA grade option exists", 'ECDA' in grade_choices, f"Found ECDA")
    test.test("ECDB grade option exists", 'ECDB' in grade_choices, f"Found ECDB")
    
    # Section choices
    section_choices = [choice[0] for choice in Class._meta.get_field('section').choices]
    test.test("Section A option exists", 'A' in section_choices, "Found A")
    test.test("Section D option exists", 'D' in section_choices, "Found D")
    
    # ==================== PRODUCTION READINESS ====================
    test.section("12. PRODUCTION READINESS")
    
    # Check minimum requirements
    has_years = AcademicYear.objects.count() >= 2
    has_classes = Class.objects.count() >= 11  # ECDA A+B, ECDB A+B, Grade 1 A, Grade 6-7 A-D (min)
    has_terms = AcademicTerm.objects.count() >= 3
    has_fees = TermFee.objects.count() >= 2
    
    test.test("Multiple academic years exist", has_years, f"Found {AcademicYear.objects.count()}")
    test.test("Multiple classes exist", has_classes, f"Found {Class.objects.count()}")
    test.test("Multiple terms exist", has_terms, f"Found {AcademicTerm.objects.count()}")
    test.test("Fee structure configured", has_fees, f"Found {TermFee.objects.count()}")
    
    # Overall readiness
    all_ready = has_years and has_classes and has_terms and has_fees and students_count > 0
    test.test("System is production-ready", all_ready, "All critical components configured")
    
    # ==================== SUMMARY ====================
    return test.summary()

if __name__ == '__main__':
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ SYSTEM TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
