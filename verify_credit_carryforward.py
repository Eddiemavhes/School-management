#!/usr/bin/env python
"""
VERIFICATION: Grade 7 Graduation System - Credit Carry-Forward
Check if system correctly:
1. Carries credits forward between terms
2. Calculates outstanding correctly
3. Prevents 2028 fees for graduated students
4. Auto-updates to Alumni when cleared
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm
from decimal import Decimal

print("="*80)
print("GRADE 7 GRADUATION & CREDIT CARRY-FORWARD VERIFICATION")
print("="*80)

# Check Annah's 2027 balances
annah = Student.all_students.filter(first_name='Annah').first()

if annah:
    print(f"\n✓ Annah found: {annah.status}")
    print(f"  Active: {annah.is_active}, Archived: {annah.is_archived}")
    
    print("\n" + "="*80)
    print("2027 TERM BREAKDOWN (Grade 7 Completion Year)")
    print("="*80)
    
    for term_num in [1, 2, 3]:
        try:
            balance = StudentBalance.objects.get(
                student=annah,
                term__academic_year=2027,
                term__term=term_num
            )
            
            print(f"\nTerm {term_num} 2027:")
            print(f"  Fee: ${balance.term_fee:.2f}")
            print(f"  Previous Arrears/Credit: ${balance.previous_arrears:.2f}")
            print(f"  Amount Paid: ${balance.amount_paid:.2f}")
            print(f"  Current Balance: ${balance.current_balance:.2f}")
            
            # Interpret the balance
            if balance.current_balance < 0:
                print(f"  → Credit of ${abs(balance.current_balance):.2f}")
            elif balance.current_balance > 0:
                print(f"  → Outstanding of ${balance.current_balance:.2f}")
            else:
                print(f"  → Fully paid")
                
        except StudentBalance.DoesNotExist:
            print(f"\nTerm {term_num} 2027: NOT FOUND")
    
    # Check 2028 balances
    print("\n" + "="*80)
    print("2028 TERM 1 CHECK (Should NOT have fees)")
    print("="*80)
    
    term1_2028 = AcademicTerm.objects.filter(academic_year=2028, term=1).first()
    
    if term1_2028:
        balance_2028 = StudentBalance.objects.filter(
            student=annah,
            term=term1_2028
        ).first()
        
        if balance_2028:
            print(f"\n❌ ERROR: Annah has 2028 Term 1 balance!")
            print(f"  Fee: ${balance_2028.term_fee:.2f}")
            print(f"  This should NOT exist for graduated students")
        else:
            print(f"\n✓ CORRECT: No 2028 balance (as expected for graduated student)")
    else:
        print("\n⚠️  2028 Term 1 does not exist")
    
    # Current status
    print("\n" + "="*80)
    print("CURRENT STATUS")
    print("="*80)
    
    final_2027_balance = StudentBalance.objects.filter(
        student=annah,
        term__academic_year=2027
    ).order_by('-term__term').first()
    
    if final_2027_balance:
        print(f"\nFinal 2027 Balance: ${final_2027_balance.current_balance:.2f}")
        
        if final_2027_balance.current_balance == 0:
            print("Status: ✓ Should be GRADUATED and ARCHIVED (Alumni)")
        elif final_2027_balance.current_balance < 0:
            print(f"Status: ✓ Has credit - should be GRADUATED (not alumni)")
        else:
            print(f"Status: ✓ Has arrears - should be GRADUATED (not alumni)")
        
        print(f"\nActual Status: {annah.status}")
        print(f"Is Active: {annah.is_active}")
        print(f"Is Archived: {annah.is_archived}")
        
        # Check if status is correct
        if final_2027_balance.current_balance <= 0:
            # Should be Alumni
            if annah.status == 'GRADUATED' and annah.is_archived and not annah.is_active:
                print("✓ Status is CORRECT")
            else:
                print("❌ Status is WRONG - Should be GRADUATED, ARCHIVED, INACTIVE")
        else:
            # Has arrears - should be GRADUATED but not archived/alumni yet
            if annah.status == 'GRADUATED' and not annah.is_active:
                print("✓ Status is CORRECT")
            else:
                print("❌ Status is WRONG")
                
else:
    print("\n❌ Annah not found in database")
