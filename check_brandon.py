#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance

brandon = Student.all_students.get(first_name='Brandon')
balances = StudentBalance.objects.filter(student=brandon).order_by('-term__academic_year', '-term__term')

print("Brandon's All Balances:")
for b in balances:
    print(f"{b.term}: ${b.current_balance:.2f}")

final = balances.filter(term__academic_year=2027).order_by('-term__term').first()
if final:
    print(f"\nFinal 2027 balance: ${final.current_balance:.2f}")
    print(f"Should be archived: {final.current_balance <= 0}")
