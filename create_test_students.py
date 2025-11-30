#!/usr/bin/env python
"""
Create new active students for testing payments
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, Class, AcademicYear
from core.models.fee import StudentBalance, TermFee
from core.models.academic import AcademicTerm
from django.utils import timezone
from datetime import date
from decimal import Decimal

print("=" * 80)
print("✨ CREATING NEW STUDENTS FOR PAYMENT TESTING")
print("=" * 80)

# Get latest year and term
years = AcademicYear.objects.all().order_by('-year')
if not years.exists():
    print("❌ No academic years created!")
    exit(1)

latest_year = years.first()
print(f"\nUsing year: {latest_year.year}")

# Get or create class
test_class = Class.objects.filter(academic_year=latest_year.year).first()
if not test_class:
    print(f"Creating class for {latest_year.year}...")
    test_class = Class.objects.create(
        grade=1,
        section='A',
        academic_year=latest_year.year
    )
else:
    print(f"Using class: {test_class}")

# Get current term
current_term = AcademicTerm.get_current_term()
if not current_term:
    print("❌ No current term set!")
    exit(1)

print(f"Current term: {current_term}")

# Create new test students
test_students_data = [
    {
        'surname': 'TEST',
        'first_name': 'Student One',
        'sex': 'M',
        'date_of_birth': date(2015, 5, 15),
        'birth_entry_number': 'TEST-001-2015'
    },
    {
        'surname': 'TEST',
        'first_name': 'Student Two',
        'sex': 'F',
        'date_of_birth': date(2015, 8, 22),
        'birth_entry_number': 'TEST-002-2015'
    },
    {
        'surname': 'TEST',
        'first_name': 'Student Three',
        'sex': 'M',
        'date_of_birth': date(2015, 3, 10),
        'birth_entry_number': 'TEST-003-2015'
    }
]

print(f"\nCreating {len(test_students_data)} new test students...")

created_students = []
for data in test_students_data:
    student = Student.objects.create(
        surname=data['surname'],
        first_name=data['first_name'],
        sex=data['sex'],
        date_of_birth=data['date_of_birth'],
        birth_entry_number=data['birth_entry_number'],
        current_class=test_class,
        date_enrolled=timezone.now().date(),
        is_active=True,
        status='ENROLLED'
    )
    created_students.append(student)
    print(f"✓ Created: {student.full_name} (ID: {student.id})")

print(f"\n" + "=" * 80)
print("📋 INITIALIZING BALANCES")
print("=" * 80)

# Get or create term fee
try:
    term_fee = TermFee.objects.get(term=current_term)
    print(f"✓ Term fee: ${term_fee.amount}")
except TermFee.DoesNotExist:
    print(f"⚠️  No term fee set for {current_term}")
    print(f"   Creating default fee of $100...")
    term_fee = TermFee.objects.create(term=current_term, amount=Decimal('100.00'))
    print(f"✓ Created: ${term_fee.amount}")

# Initialize balances
print(f"\nInitializing balances...")
for student in created_students:
    balance = StudentBalance.initialize_term_balance(student, current_term)
    if balance:
        print(f"✓ {student.full_name}: Balance ${balance.current_balance:.2f}")
    else:
        print(f"⚠️  Could not initialize balance for {student.full_name}")

print(f"\n" + "=" * 80)
print("✅ VERIFICATION")
print("=" * 80)

active_count = Student.objects.filter(is_active=True).count()
print(f"\nActive students: {active_count}")

active_list = Student.objects.filter(is_active=True)
if active_list.exists():
    print(f"\nActive students available for payments:")
    for student in active_list:
        balance = StudentBalance.objects.filter(
            student=student,
            term=current_term
        ).first()
        if balance:
            print(f"  • {student.full_name} - Balance: ${balance.current_balance:.2f}")
        else:
            print(f"  • {student.full_name} - No balance")

print(f"\n" + "=" * 80)
print("🎉 READY FOR PAYMENT TESTING!")
print("=" * 80)
print("\n✓ Go to Payments → Record Payment")
print("✓ Select one of the new TEST students")
print("✓ Enter a payment amount")
print("✓ Payment should now be recorded successfully!")
print("=" * 80)
