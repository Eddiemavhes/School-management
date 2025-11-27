#!/usr/bin/env python
"""
Script to create StudentBalance records for existing students who don't have them
This is needed because the signal was added after students were already created
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.fee import StudentBalance, TermFee
from core.models.academic import AcademicTerm

def create_balances():
    """Create StudentBalance records for all students who don't have them"""
    current_term = AcademicTerm.get_current_term()
    
    if not current_term:
        print("❌ No current term found. Please set an active term first.")
        return
    
    # Get the term fee
    try:
        term_fee = TermFee.objects.get(term=current_term)
        fee_amount = term_fee.amount
    except TermFee.DoesNotExist:
        print(f"❌ No fee found for {current_term}. Please create a TermFee first.")
        return
    
    print(f"✓ Current term: {current_term}")
    print(f"✓ Term fee: ${fee_amount}")
    print()
    
    # Get all students
    students = Student.objects.all()
    created_count = 0
    skipped_count = 0
    
    for student in students:
        # Check if StudentBalance already exists
        balance_exists = StudentBalance.objects.filter(
            student=student,
            term=current_term
        ).exists()
        
        if not balance_exists:
            try:
                # Create StudentBalance
                balance = StudentBalance.objects.create(
                    student=student,
                    term=current_term,
                    term_fee=fee_amount,
                    previous_arrears=0,  # New student has no previous arrears
                    amount_paid=0
                )
                created_count += 1
                print(f"✓ Created balance for {student.full_name} - Outstanding: ${balance.current_balance}")
            except Exception as e:
                print(f"❌ Error creating balance for {student.full_name}: {e}")
        else:
            skipped_count += 1
            balance = StudentBalance.objects.filter(
                student=student,
                term=current_term
            ).first()
            print(f"⊘ Skipped {student.full_name} - Balance already exists (Outstanding: ${balance.current_balance})")
    
    print()
    print("=" * 60)
    print(f"Summary:")
    print(f"  Created: {created_count} new balances")
    print(f"  Skipped: {skipped_count} existing balances")
    print(f"  Total Students: {students.count()}")
    print("=" * 60)

if __name__ == '__main__':
    print("Creating StudentBalance records for existing students...")
    print()
    create_balances()
