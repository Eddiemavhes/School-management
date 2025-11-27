#!/usr/bin/env python
"""
Test script to verify the enhanced create_terms_api auto-balance generation
Simulates what happens when user clicks "Create 3 Standard Terms" for a new year
"""

import os
import django
from datetime import date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicYear, AcademicTerm, Student
from core.models.fee import StudentBalance, TermFee

print("\n" + "="*80)
print("TESTING ENHANCED AUTO-BALANCE GENERATION")
print("="*80)

# First, clean up any test data
print("\n[1] Checking if 2030 exists...")
year_2030, created = AcademicYear.objects.get_or_create(
    year=2030,
    defaults={
        'start_date': date(2030, 1, 1),
        'end_date': date(2030, 12, 31)
    }
)
print(f"    2030 year: {'CREATED' if created else 'ALREADY EXISTS'}")

# Delete any existing terms for 2030
existing_2030_terms = AcademicTerm.objects.filter(academic_year=2030)
if existing_2030_terms.exists():
    print(f"    Cleaning up {existing_2030_terms.count()} existing 2030 terms...")
    existing_2030_terms.delete()

# Simulate calling the create_terms_api
print("\n[2] Creating 2030 terms (simulating button click)...")

terms_data = [
    {'term': 1, 'start_date': date(2030, 1, 10), 'end_date': date(2030, 4, 10)},
    {'term': 2, 'start_date': date(2030, 4, 20), 'end_date': date(2030, 8, 10)},
    {'term': 3, 'start_date': date(2030, 8, 20), 'end_date': date(2030, 11, 30)},
]

created_terms = []
term_objects = []

for term_data in terms_data:
    term, created = AcademicTerm.objects.get_or_create(
        academic_year=2030,
        term=term_data['term'],
        defaults={
            'start_date': term_data['start_date'],
            'end_date': term_data['end_date'],
        }
    )
    if created:
        created_terms.append(f"Term {term.term}")
    term_objects.append(term)

print(f"    Created terms: {', '.join(created_terms)}")

# Auto-generate StudentBalance records
print("\n[3] Auto-generating student balances...")

active_students = Student.objects.filter(is_active=True, is_deleted=False)
balances_created = 0

for student in active_students:
    for idx, term in enumerate(term_objects):
        # Skip if balance already exists
        if StudentBalance.objects.filter(student=student, term=term).exists():
            continue
        
        # Determine previous arrears
        previous_arrears = Decimal('0.00')
        
        if idx > 0:
            # Get balance from previous term
            prev_term = term_objects[idx - 1]
            prev_balance = StudentBalance.objects.filter(
                student=student, 
                term=prev_term
            ).first()
            
            if prev_balance:
                previous_arrears = (
                    Decimal(str(prev_balance.term_fee)) + 
                    Decimal(str(prev_balance.previous_arrears)) - 
                    Decimal(str(prev_balance.amount_paid))
                )
        else:
            # For first term, check if student has arrears from 2029
            last_term_2029 = AcademicTerm.objects.filter(
                academic_year=2029,
                term=3
            ).first()
            
            if last_term_2029:
                last_balance = StudentBalance.objects.filter(
                    student=student,
                    term=last_term_2029
                ).first()
                
                if last_balance:
                    previous_arrears = (
                        Decimal(str(last_balance.term_fee)) + 
                        Decimal(str(last_balance.previous_arrears)) - 
                        Decimal(str(last_balance.amount_paid))
                    )
        
        # Get or create TermFee
        term_fee_obj = TermFee.objects.filter(term=term).first()
        if not term_fee_obj:
            term_fee_obj, _ = TermFee.objects.get_or_create(
                term=term,
                defaults={
                    'amount': Decimal('100.00')
                }
            )
        
        # Create the balance
        StudentBalance.objects.create(
            student=student,
            term=term,
            term_fee=Decimal(str(term_fee_obj.amount)),
            previous_arrears=previous_arrears,
            amount_paid=Decimal('0.00')
        )
        balances_created += 1

print(f"    Created {balances_created} student balances")

# Verify results
print("\n[4] Verification Results:")

all_students = Student.objects.filter(is_active=True, is_deleted=False)
print(f"    Active students: {all_students.count()}")

missing = 0
for student in all_students:
    for term_num in [1, 2, 3]:
        term = AcademicTerm.objects.get(academic_year=2030, term=term_num)
        bal = StudentBalance.objects.filter(student=student, term=term).first()
        if not bal:
            missing += 1
            print(f"    MISSING: {student.surname}, {student.first_name} - 2030 Term {term_num}")

if missing == 0:
    print(f"    SUCCESS: All {all_students.count()} students have all 3 terms for 2030!")
else:
    print(f"    WARNING: {missing} missing balances!")

# Show sample for Audrey
print("\n[5] Sample Data - Audrey Anert for 2030:")
audrey = Student.objects.get(id=61)
audrey_2030_balances = StudentBalance.objects.filter(
    student=audrey,
    term__academic_year=2030
).select_related('term').order_by('term__term')

for bal in audrey_2030_balances:
    print(f"    2030 Term {bal.term.term}: fee=${bal.term_fee}, arrears=${bal.previous_arrears}, paid=${bal.amount_paid}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
