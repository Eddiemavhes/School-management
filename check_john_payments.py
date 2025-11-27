#!/usr/bin/env python
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.academic import Payment

john = Student.objects.get(id=6)
payments = Payment.objects.filter(student=john).order_by('payment_date')

print(f'Payments for {john.full_name}: {payments.count()}')
for p in payments:
    print(f'  {p.payment_date} - Term {p.term.term} 2026 - ${p.amount} - {p.receipt_number}')
