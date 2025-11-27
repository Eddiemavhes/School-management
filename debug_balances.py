#!/usr/bin/env python
"""
Debug script to check balance calculations
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicYear, AcademicTerm
from core.models.fee import StudentBalance, TermFee

print("=" * 70)
print("BALANCE DEBUG - Checking Current State")
print("=" * 70)
print()

# Check current academic year
try:
    current_year = AcademicYear.objects.filter(is_active=True).first()
    print(f"Current Active Year: {current_year.year if current_year else 'NONE'}")
    
    if current_year:
        current_term = current_year.academicterm_set.first()
        print(f"Current Term: {current_term.name if current_term else 'NONE'}")
    print()
except Exception as e:
    print(f"Error checking year/term: {e}")
    print()

# Check all students
print("STUDENTS AND BALANCES:")
print("-" * 70)
students = Student.objects.all()
print(f"Total Students: {students.count()}")
print()

for student in students:
    print(f"Student: {student.surname}, {student.first_name}")
    print(f"  - Class: {student.current_class}")
    
    # Check current_term_balance property
    balance = student.current_term_balance
    print(f"  - current_term_balance property: ${balance:.2f}")
    
    # Check StudentBalance records
    student_balances = StudentBalance.objects.filter(student=student)
    print(f"  - StudentBalance records: {student_balances.count()}")
    
    for sb in student_balances:
        print(f"    * {sb.term.name} ({sb.term.academic_year.year}):")
        print(f"      - Term Fee: ${sb.term_fee:.2f}")
        print(f"      - Amount Paid: ${sb.amount_paid:.2f}")
        print(f"      - Previous Arrears: ${sb.previous_arrears:.2f}")
        print(f"      - Current Balance: ${sb.current_balance:.2f}")
    
    if student_balances.count() == 0:
        print(f"    WARNING: No StudentBalance records!")
    
    print()

print("-" * 70)
print()

# Check TermFee settings
print("TERM FEE SETTINGS:")
print("-" * 70)
term_fees = TermFee.objects.all()
print(f"Total TermFee records: {term_fees.count()}")
print()

for tf in term_fees:
    print(f"Year: {tf.academic_year.year}")
    print(f"  - First Term: ${tf.first_term_fee:.2f}")
    print(f"  - Second Term: ${tf.second_term_fee:.2f}")
    print(f"  - Third Term: ${tf.third_term_fee:.2f}")
    print()

print("=" * 70)
