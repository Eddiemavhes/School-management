#!/usr/bin/env python
"""
Diagnose why payments are not being recorded
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm, Administrator
from core.models.academic import Payment
from core.models.fee import StudentBalance, TermFee
from decimal import Decimal

print("=" * 80)
print("🔍 PAYMENT RECORDING DIAGNOSTIC")
print("=" * 80)

# Check 1: Current term
current_term = AcademicTerm.get_current_term()
if not current_term:
    print("❌ NO CURRENT TERM SET!")
    print("   → Payments cannot be recorded without a current term")
    exit(1)
else:
    print(f"✓ Current term: {current_term}")

# Check 2: Active students
students = Student.objects.filter(is_active=True, is_archived=False)
print(f"✓ Active students: {students.count()}")

if students.count() == 0:
    print("❌ NO ACTIVE STUDENTS!")
    exit(1)

# Check 3: Test with first student
student = students.first()
print(f"\n✓ Testing with: {student.full_name} (ID: {student.id})")

# Check 4: Balance exists
balance = StudentBalance.objects.filter(student=student, term=current_term).first()
if not balance:
    print(f"⚠️  NO BALANCE FOR {student.full_name} IN {current_term}")
    print(f"   Available balance records:")
    student_balances = StudentBalance.objects.filter(student=student).order_by('-term__academic_year', '-term__term')
    if student_balances.exists():
        for b in student_balances[:3]:
            print(f"   - {b.term}: ${b.current_balance:.2f}")
    else:
        print(f"   - NONE! No balance records exist")
else:
    print(f"✓ Balance exists: ${balance.current_balance:.2f}")

# Check 5: Term fee
try:
    term_fee = TermFee.objects.get(term=current_term)
    print(f"✓ Term fee set: ${term_fee.amount:.2f}")
except TermFee.DoesNotExist:
    print(f"❌ NO TERM FEE SET FOR {current_term}")

# Check 6: Admin user
admin = Administrator.objects.filter(is_superuser=True).first()
if not admin:
    print("❌ NO ADMIN USER FOUND")
    exit(1)
else:
    print(f"✓ Admin user: {admin.email}")

# Check 7: Try to create payment
print("\n" + "=" * 80)
print("🧪 ATTEMPTING PAYMENT CREATION")
print("=" * 80)

try:
    test_payment = Payment(
        student=student,
        term=current_term,
        amount=Decimal('25.00'),
        payment_method='CASH',
        recorded_by=admin,
        notes='DIAGNOSTIC TEST'
    )
    print(f"✓ Payment object created in memory")
    
    # Try to validate
    try:
        test_payment.full_clean()
        print(f"✓ Payment validation passed")
    except Exception as e:
        print(f"❌ VALIDATION FAILED: {e}")
        raise
    
    # Try to save
    test_payment.save()
    print(f"✅ PAYMENT SAVED TO DATABASE!")
    print(f"   - ID: {test_payment.id}")
    print(f"   - Receipt: {test_payment.receipt_number}")
    print(f"   - Amount: ${test_payment.amount}")
    
    # Verify in database
    retrieved = Payment.objects.get(id=test_payment.id)
    print(f"✅ VERIFIED IN DATABASE: ${retrieved.amount}")
    
    # Clean up
    retrieved.delete()
    print(f"✓ Test payment cleaned up")
    
except Exception as e:
    print(f"❌ PAYMENT CREATION FAILED: {e}")
    import traceback
    traceback.print_exc()

# Check 8: Look at existing payments
print("\n" + "=" * 80)
print("📊 EXISTING PAYMENTS")
print("=" * 80)

all_payments = Payment.objects.all().order_by('-created_at')[:5]
if all_payments.exists():
    print(f"✓ Found {Payment.objects.count()} total payments")
    print(f"   Last 5 payments:")
    for p in all_payments:
        print(f"   - {p.receipt_number}: {p.student.full_name} ${p.amount} on {p.payment_date}")
else:
    print(f"⚠️  NO PAYMENTS IN DATABASE")

# Check 9: Signal handler check
print("\n" + "=" * 80)
print("⚡ SIGNAL HANDLERS")
print("=" * 80)

from django.db.models.signals import post_save
from core.signals import update_student_balance_on_payment

# Check if signal is registered
receivers = post_save._live_receivers(Payment)
if receivers:
    print(f"✓ Signal receivers registered: {len(receivers)}")
    for receiver in receivers:
        print(f"   - {receiver.__name__}")
else:
    print(f"❌ NO SIGNAL RECEIVERS REGISTERED!")

print("\n" + "=" * 80)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 80)
