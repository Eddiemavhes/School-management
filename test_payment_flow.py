#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm, Payment
from decimal import Decimal
from django.utils import timezone

student = Student.objects.get(first_name='Edwin', surname='Mavhe')
current_term = AcademicTerm.objects.filter(is_current=True).first()

print("TESTING PAYMENT + AUTO-GRADUATION FLOW")
print("=" * 80)
print()

print(f"Before payment:")
print(f"  Status: {student.status}")
print(f"  Is Active: {student.is_active}")
print(f"  Is Archived: {student.is_archived}")
print(f"  Overall Balance: ${student.overall_balance}")
print()

# Record payment
print(f"Recording $600 payment for {current_term}...")
payment = Payment.objects.create(
    student=student,
    term=current_term,
    amount=Decimal('600'),
    payment_date=timezone.now().date(),
    payment_method='CASH',
    receipt_number='TEST-001'
)
print(f"Payment recorded: ${payment.amount}")
print()

# Check after payment
student.refresh_from_db()
print(f"After payment:")
print(f"  Status: {student.status}")
print(f"  Is Active: {student.is_active}")
print(f"  Is Archived: {student.is_archived}")
print(f"  Overall Balance: ${student.overall_balance}")
print()

# Verify no extra terms were created
from core.models import StudentBalance
balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
print(f"Total balance records: {balances.count()}")
latest = balances.last()
if latest:
    print(f"Latest term: {latest.term} (Total Due: ${latest.total_due})")
