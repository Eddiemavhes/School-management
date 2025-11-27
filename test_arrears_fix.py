#!/usr/bin/env python
"""
Test script to verify that arrears are properly carried forward between terms.
This test ensures that the fix prevents the recurring arrears calculation issue.
"""

import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm, TermFee

def test_arrears_carryover():
    """Test that arrears properly carry forward between terms"""
    
    print("=" * 80)
    print("TESTING ARREARS CARRYOVER LOGIC")
    print("=" * 80)
    print()
    
    # Get test students
    annah = Student.objects.get(first_name='Annah')
    brandon = Student.objects.get(first_name='Brandon')
    carol = Student.objects.get(first_name='Carol')
    ednette = Student.objects.get(first_name='Ednette')
    
    students = [annah, brandon, carol, ednette]
    
    # Get all terms
    terms = AcademicTerm.objects.all().order_by('academic_year', 'term')
    
    print("VERIFICATION 1: Check calculate_arrears() method")
    print("-" * 80)
    
    for term in terms:
        if term.id >= 77:  # Only 2027 terms
            for student in students:
                arrears = StudentBalance.calculate_arrears(student, term)
                print(f"{student.first_name:10} Term {term.id}: Expected arrears = ${arrears}")
    
    print()
    print("VERIFICATION 2: Check initialize_term_balance() creates correct balances")
    print("-" * 80)
    
    for term in terms:
        if term.id >= 77:  # Only 2027 terms
            for student in students:
                try:
                    balance = StudentBalance.initialize_term_balance(student, term)
                    if balance:
                        total_due = balance.term_fee + balance.previous_arrears
                        print(f"{student.first_name:10} Term {term.id}: Fee ${balance.term_fee} + Arrears ${balance.previous_arrears} = ${total_due}")
                except Exception as e:
                    print(f"{student.first_name:10} Term {term.id}: ERROR - {e}")
    
    print()
    print("VERIFICATION 3: Final display check")
    print("-" * 80)
    
    term_3 = AcademicTerm.objects.get(id=79)  # Current term
    for student in students:
        balance = StudentBalance.objects.get(student=student, term=term_3)
        total_due = balance.term_fee + balance.previous_arrears
        print(f"{student.first_name:10}: ${total_due:7} should display on dashboard")
    
    print()
    print("=" * 80)
    print("EXPECTED RESULTS:")
    print("  Annah:    $80   (Fee $100 - Credit $20)")
    print("  Brandon:  $100  (Fee $100 + Arrears $0)")
    print("  Carol:    $110  (Fee $100 + Arrears $10)")
    print("  Ednette:  $200  (Fee $100 + Arrears $100)")
    print("=" * 80)

if __name__ == '__main__':
    test_arrears_carryover()
