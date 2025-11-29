#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, Payment

print("=" * 80)
print("CHECKING ANNAH'S PAYMENTS")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()
payments = Payment.objects.filter(student=annah).order_by('payment_date')

print(f"All Payments for {annah.first_name}:\n")
for p in payments:
    print(f"  {p.payment_date}: ${p.amount} for {p.term}")

print()
print(f"Total Paid: ${sum(p.amount for p in payments)}")
