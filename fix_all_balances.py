#!/usr/bin/env python
"""
Fix all balance calculation errors in the system.
This script recalculates all student balances based on actual payments.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, Payment, AcademicTerm
from core.models.fee import StudentBalance
from decimal import Decimal

def fix_all_balances():
    """Recalculate and fix all student balances"""
    term = AcademicTerm.get_current_term()
    if not term:
        print("ERROR: No current term set!")
        return
    
    print(f"Fixing balances for term: {term}\n")
    print("=" * 80)
    
    errors_found = 0
    errors_fixed = 0
    
    for student in Student.objects.all():
        try:
            balance = StudentBalance.objects.get(student=student, term=term)
        except StudentBalance.DoesNotExist:
            continue
        
        # Calculate actual payments
        actual_paid = sum(p.amount for p in Payment.objects.filter(student=student, term=term))
        stored_paid = balance.amount_paid
        
        if actual_paid != stored_paid:
            errors_found += 1
            print(f"\nERROR FOUND: {student.surname}, {student.first_name} (ID: {student.id})")
            print(f"  Before fix:")
            print(f"    Stored amount_paid: {stored_paid}")
            print(f"    Actual amount (from payments): {actual_paid}")
            print(f"    Stored current_balance: {balance.current_balance}")
            
            # Fix the balance
            balance.amount_paid = actual_paid
            balance.save()
            errors_fixed += 1
            
            print(f"  After fix:")
            print(f"    New amount_paid: {balance.amount_paid}")
            print(f"    New current_balance: {balance.current_balance}")
            print(f"    Payment status: {balance.payment_status}")
    
    print("\n" + "=" * 80)
    print(f"\nSummary:")
    print(f"  Errors found: {errors_found}")
    print(f"  Errors fixed: {errors_fixed}")
    
    # Show final state
    print(f"\nFinal balance summary for {term}:")
    print("-" * 80)
    
    total_collected = Decimal('0')
    fully_paid = 0
    partial_paid = 0
    no_payment = 0
    
    for student in Student.objects.all():
        try:
            balance = StudentBalance.objects.get(student=student, term=term)
            status = balance.payment_status
            
            if status == 'PAID':
                fully_paid += 1
                # Only count the term fee toward total (overpayments go to next term)
                total_collected += balance.term_fee
            elif status == 'PARTIAL':
                partial_paid += 1
                total_collected += balance.amount_paid
            else:
                no_payment += 1
        except:
            pass
    
    print(f"Total collected (current term): ${total_collected:.2f}")
    print(f"Fully paid students: {fully_paid}")
    print(f"Partial payment students: {partial_paid}")
    print(f"No payment students: {no_payment}")

if __name__ == '__main__':
    fix_all_balances()
