#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance

print("="*80)
print("CHECKING ANNAH'S BALANCE CALCULATION")
print("="*80)

# Check if Annah exists
annah = Student.all_students.filter(first_name='Annah').first()

if not annah:
    print("\n❌ Annah not found in database")
    print("\nLet me check if system was reset...")
    all_students = Student.all_students.all()
    print(f"Total students in database: {all_students.count()}")
    for student in all_students:
        print(f"  - {student.first_name} {student.surname}")
else:
    print(f"\n✓ Found: {annah.first_name}")
    print(f"  Status: {annah.status}")
    print(f"  Is Active: {annah.is_active}")
    print(f"  Is Archived: {annah.is_archived}")
    
    balances = StudentBalance.objects.filter(student=annah).order_by('-term__academic_year', '-term__term')
    print(f"\n  Total balances: {balances.count()}\n")
    
    for b in balances:
        print(f"  {b.term.academic_year} Term {b.term.term}:")
        print(f"    Term Fee: ${b.term_fee:.2f}")
        print(f"    Amount Paid: ${b.amount_paid:.2f}")
        print(f"    Previous Arrears: ${b.previous_arrears:.2f}")
        print(f"    Current Balance: ${b.current_balance:.2f}")
        
        # Check calculation
        expected = b.previous_arrears + b.term_fee - b.amount_paid
        print(f"    Expected Balance: ${expected:.2f}")
        
        if abs(expected - b.current_balance) > 0.01:
            print(f"    ⚠️  CALCULATION ERROR!")
        print()
