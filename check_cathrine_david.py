#!/usr/bin/env python
import os, sys, django
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import StudentBalance, Student

cathrine = Student.objects.get(id=10)
david = Student.objects.get(id=11)

print("Cathrine's balances:")
for b in StudentBalance.objects.filter(student=cathrine).order_by('term__academic_year', 'term__term'):
    print(f"  {b.term}: Fee=${b.term_fee}, Arrears=${b.previous_arrears}, Paid=${b.amount_paid}, Balance=${b.current_balance}")

print("\nDavid's balances:")
for b in StudentBalance.objects.filter(student=david).order_by('term__academic_year', 'term__term'):
    print(f"  {b.term}: Fee=${b.term_fee}, Arrears=${b.previous_arrears}, Paid=${b.amount_paid}, Balance=${b.current_balance}")
