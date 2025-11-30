#!/usr/bin/env python
"""
COMPREHENSIVE FINAL SYSTEM VERIFICATION
Tests all critical business rules and system functionality
"""
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, Payment, AcademicTerm, StudentMovement
from django.utils import timezone
from datetime import date

print("="*80)
print("COMPREHENSIVE FINAL SYSTEM VERIFICATION")
print("="*80)

# 1. GRADUATION SYSTEM TEST
print("\n1. GRADUATION SYSTEM VERIFICATION")
print("-" * 80)

grade7_students = Student.all_students.filter(current_class__grade=7)
print(f"Grade 7 students found: {grade7_students.count()}")

for student in grade7_students:
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    final_balance = balances.last()
    movements = StudentMovement.objects.filter(student=student, movement_type='GRADUATION')
    
    print(f"\n  {student.full_name}:")
    print(f"    Status: {student.status}")
    print(f"    Is Active: {student.is_active}")
    print(f"    Is Archived: {student.is_archived}")
    print(f"    Final Balance: ${final_balance.current_balance:.2f}")
    
    # Verify Alumni logic
    if final_balance.current_balance <= 0:
        expected_archived = True
        expected_status_type = "Alumni"
    else:
        expected_archived = False
        expected_status_type = "Graduated (with arrears)"
    
    if student.is_archived == expected_archived:
        print(f"    Alumni Status: ✅ CORRECT ({expected_status_type})")
    else:
        print(f"    Alumni Status: ❌ INCORRECT (Expected {expected_archived}, got {student.is_archived})")
    
    if movements.exists():
        movement = movements.first()
        print(f"    Graduation Record: ✅ EXISTS ({movement.reason})")
    else:
        print(f"    Graduation Record: ❌ MISSING")

# 2. BALANCE CALCULATION TEST
print("\n\n2. BALANCE CALCULATION VERIFICATION")
print("-" * 80)

david = Student.all_students.get(first_name='David')
david_balances = StudentBalance.objects.filter(student=david).order_by('term__academic_year', 'term__term')

print(f"Student: {david.full_name}")
print(f"Total balance records: {david_balances.count()}")
print(f"\nBalance progression:")

for balance in david_balances:
    print(f"  {balance.term.academic_year} Term {balance.term.term}: ${balance.current_balance:.2f} "
          f"(arrears: ${balance.previous_arrears:.2f}, fee: ${balance.term_fee:.2f}, paid: ${balance.amount_paid:.2f})")

final_balance = david_balances.last()
expected_final = Decimal('500.00')  # After our $100 test payment

print(f"\nFinal Balance: ${final_balance.current_balance:.2f}")
print(f"Expected (after test payment): ${expected_final:.2f}")

if final_balance.current_balance == expected_final:
    print("Balance Calculation: ✅ CORRECT")
else:
    print(f"Balance Calculation: ❌ INCORRECT (Expected {expected_final}, got {final_balance.current_balance})")

# 3. PAYMENT RECORDING TEST
print("\n\n3. PAYMENT RECORDING SYSTEM")
print("-" * 80)

david_payments = Payment.objects.filter(student=david)
print(f"Total payments recorded: {david_payments.count()}")

for payment in david_payments:
    print(f"  Payment {payment.id}: ${payment.amount:.2f} on {payment.payment_date}")

# 4. CREDIT CARRYOVER TEST
print("\n\n4. CREDIT CARRYOVER VERIFICATION")
print("-" * 80)

annah = Student.all_students.get(first_name='Annah')
annah_balances = StudentBalance.objects.filter(student=annah).order_by('term__academic_year', 'term__term')

print(f"Student: {annah.full_name}")
print(f"\nBalance progression (checking for credit carry-forward):")

for balance in annah_balances:
    print(f"  {balance.term.academic_year} Term {balance.term.term}: ${balance.current_balance:.2f}")
    if balance.previous_arrears < 0:
        print(f"    (Previous term credit: ${abs(balance.previous_arrears):.2f})")

final_annah_balance = annah_balances.last()
if final_annah_balance.current_balance < 0:
    print(f"\n✅ Credit carry-forward working (final balance: ${final_annah_balance.current_balance:.2f})")
else:
    print(f"\n⚠️  No overpayment credit found (final balance: ${final_annah_balance.current_balance:.2f})")

# 5. NO FEES FOR GRADUATED STUDENTS TEST
print("\n\n5. GRADUATED STUDENT FEE CHECK")
print("-" * 80)

# Check if there are any balance records for 2028 for Grade 7 students
grade7_2028_balances = StudentBalance.objects.filter(
    student__current_class__grade=7,
    term__academic_year=2028
)

print(f"Balance records for Grade 7 in 2028: {grade7_2028_balances.count()}")

if grade7_2028_balances.count() == 0:
    print("✅ No fees charged to graduated Grade 7 students in new year")
else:
    print("❌ Fees were charged to graduated Grade 7 students (should not happen)")
    for balance in grade7_2028_balances:
        print(f"  {balance.student.full_name}: ${balance.term_fee:.2f}")

# 6. OVERALL SYSTEM SUMMARY
print("\n\n6. SYSTEM SUMMARY")
print("-" * 80)

all_students = Student.all_students.all()
enrolled_count = all_students.filter(status='ENROLLED').count()
graduated_count = all_students.filter(status='GRADUATED').count()
alumni_count = all_students.filter(is_archived=True).count()

print(f"Total students: {all_students.count()}")
print(f"  Enrolled: {enrolled_count}")
print(f"  Graduated: {graduated_count}")
print(f"  Alumni (with zero/negative balance): {alumni_count}")

total_payments = Payment.objects.count()
total_paid = Payment.objects.aggregate(
    total=django.db.models.Sum('amount')
)['total'] or Decimal('0')

print(f"\nPayment System:")
print(f"  Total payments recorded: {total_payments}")
print(f"  Total amount paid: ${total_paid:.2f}")

print("\n" + "="*80)
print("VERIFICATION COMPLETE")
print("="*80)
