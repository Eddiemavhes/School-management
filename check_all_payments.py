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
print("CHECKING ALL PAYMENTS")
print("=" * 80)
print()

for name in ['Annah', 'Brandon', 'Cathrine', 'David']:
    student = Student.objects.filter(first_name=name).first()
    print(f"{name}:")
    
    payments = Payment.objects.filter(student=student).order_by('payment_date')
    for p in payments:
        print(f"  {p.payment_date}: ${p.amount} for {p.term}")
    
    print()
