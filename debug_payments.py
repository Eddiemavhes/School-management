#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.academic import Payment

s = Student.objects.get(id=64)
payments = s.payments.all().order_by('-payment_date')
print(f"Total payments: {payments.count()}")
for p in payments:
    date_str = p.payment_date.strftime("%Y-%m-%d %H:%M:%S") if p.payment_date else "N/A"
    print(f"  ID {p.id}: {date_str} - ${p.amount}")

print(f"\nTotal: ${sum([p.amount for p in payments])}")
