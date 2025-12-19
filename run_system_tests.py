#!/usr/bin/env python
"""
QUICK SYSTEM VERIFICATION TEST
Run this to verify critical system functionality works

Usage:
    python manage.py shell < run_system_tests.py
"""

from core.models import (
    Student, AcademicTerm, Payment, Class, TermFee, StudentBalance,
    Administrator, AcademicYear
)
from datetime import date
from decimal import Decimal
from django.db.models import Sum

print("\n" + "="*80)
print("STARTING SYSTEM VERIFICATION TEST")
print("="*80)

# Setup: Create test data
print("\n1. Setting up test data...")
year = AcademicYear.objects.create(year=2027, start_date=date(2027,1,1), end_date=date(2027,12,31))
term = AcademicTerm.objects.create(academic_year=2027, term=1, start_date=date(2027,1,15), end_date=date(2027,4,15), is_current=True)
class_obj = Class.objects.create(academic_year=2027, grade=7, section='A')
fee = TermFee.objects.create(term=term, amount=Decimal('100.00'))
admin = Administrator.objects.create_user(email='test@test.com', password='test')
print("   [OK] Test data created")

# Test 1: Create Student
print("\n2. Testing student creation...")
student = Student.objects.create(
    surname="Smith",
    first_name="John",
    sex='M',
    date_of_birth=date(2010, 5, 15),
    birth_entry_number="BEN123ABC",
    current_class=class_obj
)
assert student.id, "Student not created"
print(f"   [OK] Created student: {student}")

# Test 2: Create Balance
print("\n3. Testing balance creation...")
balance = StudentBalance.objects.create(
    student=student,
    term=term,
    term_fee_record=fee,
    previous_arrears=Decimal('0'),
    amount_paid=Decimal('0')
)
assert balance.term_fee == Decimal('100.00'), "Term fee incorrect"
assert balance.total_due == Decimal('100.00'), "Total due incorrect"
print(f"   [OK] Balance created: Due={balance.total_due}")

# Test 3: Record Payment
print("\n4. Testing payment recording...")
payment = Payment.objects.create(
    student=student,
    term=term,
    amount=Decimal('60.00'),
    payment_method='CASH',
    recorded_by=admin
)
assert payment.id, "Payment not created"
print(f"   [OK] Payment recorded: {payment.amount}")

# Test 4: Update Balance
print("\n5. Testing balance update after payment...")
total_paid = Payment.objects.filter(student=student, term=term).aggregate(total=Sum('amount'))['total'] or Decimal('0')
balance.amount_paid = total_paid
balance.save()
assert balance.current_balance == Decimal('40.00'), f"Balance should be 40, got {balance.current_balance}"
print(f"   [OK] Balance updated: Remaining Due={balance.current_balance}")

# Test 5: Multiple Payments
print("\n6. Testing multiple payments accumulation...")
payment2 = Payment.objects.create(
    student=student,
    term=term,
    amount=Decimal('40.00'),
    payment_method='CASH',
    recorded_by=admin
)
total_paid = Payment.objects.filter(student=student, term=term).aggregate(total=Sum('amount'))['total'] or Decimal('0')
balance.amount_paid = total_paid
balance.save()
assert balance.current_balance == Decimal('0'), f"Balance should be 0, got {balance.current_balance}"
print(f"   [OK] Multiple payments work: Total Paid={balance.amount_paid}, Balance={balance.current_balance}")

# Test 6: Overpayment
print("\n7. Testing overpayment (credit)...")
student2 = Student.objects.create(
    surname="Jones",
    first_name="Jane",
    sex='F',
    date_of_birth=date(2010, 5, 15),
    birth_entry_number="BEN456DEF",
    current_class=class_obj
)
balance2 = StudentBalance.objects.create(
    student=student2,
    term=term,
    term_fee_record=fee,
    previous_arrears=Decimal('0'),
    amount_paid=Decimal('0')
)
payment3 = Payment.objects.create(
    student=student2,
    term=term,
    amount=Decimal('200.00'),
    payment_method='CASH',
    recorded_by=admin
)
total_paid2 = Payment.objects.filter(student=student2, term=term).aggregate(total=Sum('amount'))['total'] or Decimal('0')
balance2.amount_paid = total_paid2
balance2.save()
assert balance2.current_balance == Decimal('-100.00'), f"Balance should be -100 (credit), got {balance2.current_balance}"
print(f"   [OK] Overpayment creates credit: Balance={balance2.current_balance}")

# Test 7: Get Current Term
print("\n8. Testing term queries...")
current = AcademicTerm.get_current_term()
assert current.is_current, "Current term not set"
assert current == term, "Wrong current term"
print(f"   [OK] Current term: {current}")

# Test 8: Database Integrity
print("\n9. Testing database integrity...")
student_count = Student.objects.count()
balance_count = StudentBalance.objects.count()
payment_count = Payment.objects.count()
assert student_count == 2, "Wrong student count"
assert balance_count == 2, "Wrong balance count"
assert payment_count == 3, "Wrong payment count"
print(f"   [OK] Records: Students={student_count}, Balances={balance_count}, Payments={payment_count}")

print("\n" + "="*80)
print("SUCCESS: ALL SYSTEM TESTS PASSED")
print("="*80)
print("""
System Functionality Verified:
  + Student creation and management
  + Balance calculation
  + Payment recording
  + Balance updates after payment
  + Multiple payment handling
  + Overpayment (credit) handling
  + Term management
  + Database integrity

The system core is WORKING CORRECTLY.

Next Steps:
  1. Test in the web interface
  2. Verify graduation workflows
  3. Test fee management
  4. Test class assignments
  5. Run full test suite before production

""")
