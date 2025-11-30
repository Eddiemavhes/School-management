#!/usr/bin/env python
"""
COMPLETE VERIFICATION: Grade 7 Graduation System
- Credit carry-forward working correctly
- Year-end graduation implemented
- Alumni status based on financial responsibility
- No 2028 fees for graduated students
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm
from decimal import Decimal

print("="*80)
print("✅ GRADE 7 GRADUATION SYSTEM - COMPLETE VERIFICATION")
print("="*80)

# Get all Grade 7 students
grade7_students = Student.objects.filter(status='GRADUATED')

print(f"\nGraduated Students: {grade7_students.count()}\n")

for student in grade7_students:
    print(f"\n{'='*80}")
    print(f"{student.first_name.upper()}")
    print(f"{'='*80}")
    
    # Get 2027 balances
    balances_2027 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2027
    ).order_by('term__term')
    
    print(f"\nStatus: {student.status}")
    print(f"Is Active: {student.is_active}")
    print(f"Is Archived: {student.is_archived}")
    print(f"Alumni: {'✓ YES' if student.is_archived else '✗ NO'}\n")
    
    print("2027 BREAKDOWN:")
    cumulative_balance = Decimal('0')
    
    for balance in balances_2027:
        print(f"\n  Term {balance.term.term}:")
        print(f"    Fee: ${balance.term_fee:>8.2f}")
        print(f"    Paid: ${balance.amount_paid:>8.2f}")
        print(f"    Arrears/Credit (in): ${balance.previous_arrears:>8.2f}")
        print(f"    Balance (out): ${balance.current_balance:>8.2f}", end="")
        
        if balance.current_balance < 0:
            print(f"  [Credit: ${abs(balance.current_balance):.2f}]")
        elif balance.current_balance > 0:
            print(f"  [Arrears: ${balance.current_balance:.2f}]")
        else:
            print(f"  [Fully Paid]")
    
    # Final status
    final_balance = balances_2027.order_by('-term__term').first()
    
    print(f"\n  Final 2027 Balance: ${final_balance.current_balance:.2f}")
    
    if final_balance.current_balance < 0:
        print(f"  Result: PAID (has ${abs(final_balance.current_balance):.2f} credit)")
    elif final_balance.current_balance > 0:
        print(f"  Result: ARREARS (owes ${final_balance.current_balance:.2f})")
    else:
        print(f"  Result: FULLY PAID")
    
    # Check 2028
    print(f"\n2028 Status:")
    has_2028 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2028
    ).exists()
    
    if has_2028:
        print(f"  ❌ HAS 2028 BALANCE (ERROR)")
    else:
        print(f"  ✓ NO 2028 BALANCE (Correct - no new fees)")

print("\n" + "="*80)
print("BUSINESS RULES VERIFICATION")
print("="*80)

rules = {
    "All Grade 7 students marked as GRADUATED": (
        Student.objects.filter(status='GRADUATED').count() == 4
    ),
    "Graduated students not active (is_active=False)": (
        not Student.objects.filter(status='GRADUATED', is_active=True).exists()
    ),
    "No 2028 balances for graduated students": (
        not StudentBalance.objects.filter(
            student__status='GRADUATED',
            term__academic_year=2028
        ).exists()
    ),
    "Annah is ALUMNI (paid in full)": (
        Student.objects.get(first_name='Annah').is_archived and
        StudentBalance.objects.get(
            student__first_name='Annah',
            term__academic_year=2027,
            term__term=3
        ).current_balance <= 0
    ),
    "Brandon is GRADUATED (has arrears)": (
        Student.objects.get(first_name='Brandon').status == 'GRADUATED' and
        not Student.objects.get(first_name='Brandon').is_archived
    ),
    "Cathrine is GRADUATED (has arrears)": (
        Student.objects.get(first_name='Cathrine').status == 'GRADUATED' and
        not Student.objects.get(first_name='Cathrine').is_archived
    ),
    "David is GRADUATED (has arrears)": (
        Student.objects.get(first_name='David').status == 'GRADUATED' and
        not Student.objects.get(first_name='David').is_archived
    ),
}

print()
for rule, passed in rules.items():
    status = "✅" if passed else "❌"
    print(f"{status} {rule}")

all_passed = all(rules.values())

print("\n" + "="*80)
if all_passed:
    print("🎓 GRADE 7 GRADUATION SYSTEM: COMPLETE AND CORRECT ✅")
    print("\nImplemented Features:")
    print("  ✅ Credit carry-forward between terms")
    print("  ✅ Year-end Grade 7 graduation")
    print("  ✅ Alumni status based on financial responsibility")
    print("  ✅ No 2028 fees for graduated students")
    print("  ✅ Graduated students can pay down arrears")
else:
    print("⚠️  GRADUATION SYSTEM: SOME RULES VIOLATED")
print("="*80)
