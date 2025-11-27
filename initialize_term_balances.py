#!/usr/bin/env python
"""
Initialize balances for all active students in the current term.
This script should be run when moving to a new term to ensure all students
have balance records initialized properly.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm, Student
from core.models.fee import StudentBalance, TermFee

def initialize_all_balances():
    """Initialize balances for all active students in current term"""
    current_term = AcademicTerm.get_current_term()
    
    if not current_term:
        print("ERROR: No current term set!")
        return False
    
    print(f"\n{'='*80}")
    print(f"Initializing balances for: {current_term}")
    print(f"{'='*80}\n")
    
    initialized = 0
    existing = 0
    
    # Get term fee
    try:
        term_fee_obj = TermFee.objects.get(term=current_term)
        term_fee_amount = term_fee_obj.amount
    except TermFee.DoesNotExist:
        print("ERROR: No term fee set for this term!")
        return False
    
    for student in Student.objects.filter(is_active=True):
        balance, created = StudentBalance.objects.get_or_create(
            student=student,
            term=current_term,
            defaults={
                'term_fee': term_fee_amount,
                'previous_arrears': StudentBalance.calculate_arrears(student, current_term)
            }
        )
        
        if created:
            initialized += 1
            status = "✓ CREATED"
        else:
            existing += 1
            status = "✓ EXISTS"
        
        print(f"{status}: {student.surname:<15} | Fee: ${balance.term_fee:<8} | Arrears: ${balance.previous_arrears:<8} | Total Due: ${balance.total_due:<8} | Balance: ${balance.current_balance}")
    
    print(f"\n{'='*80}")
    print(f"Summary:")
    print(f"  Newly initialized: {initialized}")
    print(f"  Already existing: {existing}")
    print(f"  Total: {initialized + existing}")
    print(f"{'='*80}\n")
    
    return True

if __name__ == '__main__':
    initialize_all_balances()
