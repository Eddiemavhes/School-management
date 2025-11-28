#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, StudentMovement, Payment

student = Student.objects.get(first_name='Edwin', surname='Mavhe')

print("=" * 80)
print("FINAL SYSTEM VERIFICATION - PAYMENT SIGNAL FIX")
print("=" * 80)
print()

# Section 1: Student Status
print("1. STUDENT STATUS")
print("-" * 80)
print(f"   Name: {student.first_name} {student.surname}")
print(f"   Current Grade: {student.current_class}")
print(f"   Status: {student.status}")
print(f"   Is Active: {student.is_active}")
print(f"   Is Archived: {student.is_archived}")
print(f"   Overall Balance: ${student.overall_balance}")
print()

# Section 2: Graduation Movement
print("2. GRADUATION RECORD")
print("-" * 80)
movements = StudentMovement.objects.filter(student=student).order_by('-movement_date')
if movements.exists():
    movement = movements.first()
    print(f"   ✅ Graduation recorded: {movement.movement_date}")
    print(f"   From: {movement.from_class} → To: Alumni")
    print(f"   Reason: {movement.reason}")
else:
    print("   ❌ No graduation record found")
print()

# Section 3: Balance History
print("3. BALANCE HISTORY")
print("-" * 80)
balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
for b in balances:
    status = ""
    if b.term.academic_year == 2028:
        if b.current_balance == 0:
            status = " ✅ PAID"
        else:
            status = f" ❌ UNPAID ${b.current_balance}"
    print(f"   {str(b.term):20} | Fee ${b.term_fee:>6} | Paid ${b.amount_paid:>6} | Balance ${b.current_balance:>6}{status}")
print()

# Section 4: Payments
print("4. PAYMENT RECORDS")
print("-" * 80)
payments = Payment.objects.filter(student=student).order_by('payment_date')
if payments.exists():
    for p in payments:
        print(f"   {p.payment_date}: ${p.amount} for {p.term}")
else:
    print("   No payments recorded")
print()

# Section 5: Verification Checks
print("5. VERIFICATION CHECKS")
print("-" * 80)

checks = []

# Check 1: Student is graduated
checks.append(("Student status = GRADUATED", student.status == 'GRADUATED'))

# Check 2: Student is not active
checks.append(("Is Active = False", student.is_active == False))

# Check 3: Student is archived
checks.append(("Is Archived = True", student.is_archived == True))

# Check 4: Overall balance = 0
checks.append(("Overall Balance = $0", student.overall_balance == 0))

# Check 5: No orphaned future balances
future_count = StudentBalance.objects.filter(
    student=student,
    term__academic_year__gte=2028,
    term__term__gte=2
).count()
checks.append(("No 2028 T2/T3 balances", future_count == 0))

# Check 6: Graduation movement exists
checks.append(("Graduation recorded", movements.exists()))

# Check 7: 2028 T1 is paid in full
b_2028_t1 = StudentBalance.objects.filter(student=student, term__academic_year=2028, term__term=1).first()
if b_2028_t1:
    checks.append(("2028 T1 fully paid", b_2028_t1.current_balance == 0))

for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"   {status} {check_name}")

print()
print("=" * 80)
all_passed = all(result for _, result in checks)
if all_passed:
    print("✅✅✅ ALL CHECKS PASSED! SYSTEM WORKING CORRECTLY!")
else:
    print("❌ SOME CHECKS FAILED!")
print("=" * 80)
