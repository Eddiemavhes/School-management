#!/usr/bin/env python
"""
Initialize StudentBalance records for all students in current term
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicYear
from core.models.academic import AcademicTerm
from core.models.fee import StudentBalance

print("=" * 70)
print("INITIALIZING STUDENT BALANCES")
print("=" * 70)
print()

# Get current active year
current_year = AcademicYear.objects.filter(is_active=True).first()
if not current_year:
    print("ERROR: No active academic year found!")
    exit(1)

print(f"Active Year: {current_year.year}")

# Get the current term
current_term = AcademicTerm.get_current_term()
if not current_term:
    print("ERROR: No current academic term found!")
    exit(1)

print(f"Current Term: {current_term.get_term_display()}")
print()

# Get all active students
students = Student.objects.filter(is_active=True)
print(f"Processing {students.count()} active students...")
print()

created_count = 0
for student in students:
    # Check if StudentBalance already exists
    existing = StudentBalance.objects.filter(
        student=student,
        term=current_term
    ).exists()
    
    if not existing:
        # Initialize the balance (this will create StudentBalance with proper arrears)
        StudentBalance.initialize_term_balance(student, current_term)
        print(f"✓ Created balance for: {student.surname}, {student.first_name}")
        created_count += 1
    else:
        print(f"✓ Already exists: {student.surname}, {student.first_name}")

print()
print("=" * 70)
print(f"Total Balances Created: {created_count}")
print("=" * 70)
print()

# Verify the balances
print("VERIFICATION - Current Balances:")
print("-" * 70)
for student in students:
    balance = StudentBalance.objects.filter(
        student=student,
        term=current_term
    ).first()
    
    if balance:
        print(f"{student.surname}, {student.first_name}: ${balance.current_balance:.2f}")
        print(f"  (Term Fee: ${balance.term_fee:.2f}, Paid: ${balance.amount_paid:.2f}, Arrears: ${balance.previous_arrears:.2f})")
    else:
        print(f"{student.surname}, {student.first_name}: NO BALANCE RECORD")

print()
