#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance
from decimal import Decimal

student = Student.objects.filter(first_name='Annah').first()

if student:
    print("=" * 80)
    print(f"FIXING: {student.first_name} {student.surname}")
    print("=" * 80)
    print()
    
    print("BEFORE FIX:")
    print("-" * 80)
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    for b in balances:
        print(f"  {b.term}: Fee ${b.term_fee}, Arrears ${b.previous_arrears}, Total ${b.total_due}, Balance ${b.current_balance}")
    print()
    print(f"Overall Balance: ${student.overall_balance}")
    print()
    
    # Analysis
    print("ANALYSIS:")
    print("-" * 80)
    b_t1 = balances.filter(term__term=1).first()
    if b_t1:
        print(f"Term 1 2026: Fee ${b_t1.term_fee}, Paid ${b_t1.amount_paid}")
        print(f"  Balance: ${b_t1.current_balance} (overpaid by ${abs(b_t1.current_balance)})")
        credit = abs(b_t1.current_balance)
        print()
        print(f"Since Annah has a ${credit} credit:")
        print(f"  - Term 2 should have: Fee $0 (covered by credit)")
        print(f"  - Term 3 should NOT exist yet")
        print()
        
        # Fix Term 2
        b_t2 = balances.filter(term__term=2).first()
        if b_t2:
            print(f"FIXING Term 2:")
            print(f"  Before: Fee ${b_t2.term_fee}, Arrears ${b_t2.previous_arrears}, Total ${b_t2.total_due}")
            
            # Term 2 should have:
            # - Term Fee: $0 (credit covers it)
            # - Previous Arrears: -$20 (the credit from T1)
            # - Total Due: -$20 (pure credit, no fee)
            b_t2.term_fee = Decimal('0.00')
            # previous_arrears stays the same (-$20)
            b_t2.save()
            print(f"  After: Fee ${b_t2.term_fee}, Arrears ${b_t2.previous_arrears}, Total ${b_t2.total_due}")
            print(f"  ✅ Fixed")
            print()
        
        # Delete Term 3 - it shouldn't exist yet
        b_t3 = balances.filter(term__term=3).first()
        if b_t3:
            print(f"DELETING Term 3:")
            print(f"  Term 3 should not exist while Annah has credit")
            b_t3.delete()
            print(f"  ✅ Deleted")
            print()
    
    print("AFTER FIX:")
    print("-" * 80)
    student.refresh_from_db()
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    for b in balances:
        print(f"  {b.term}: Fee ${b.term_fee}, Arrears ${b.previous_arrears}, Total ${b.total_due}, Balance ${b.current_balance}")
    print()
    print(f"Overall Balance: ${student.overall_balance}")
    print()
    
    if student.overall_balance == 0:
        print("✅✅✅ FIXED! Balance is now $0")
    elif student.overall_balance < 0:
        print(f"✅ FIXED! Balance shows credit: ${abs(student.overall_balance)}")
    else:
        print(f"⚠️  Balance still shows: ${student.overall_balance}")
