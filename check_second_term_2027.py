#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm, StudentBalance

student = Student.objects.get(first_name='Edwin', surname='Mavhe')
current_term = AcademicTerm.objects.filter(is_current=True).first()

print(f'Current Term: {current_term}')
print(f'Student: {student.first_name} {student.surname}')
print(f'Grade: {student.current_class}')
print(f'Overall Balance: {student.overall_balance}')
print(f'Is Active: {student.is_active}')
print()

balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
print('All Balance Records:')
for b in balances:
    print(f'  {b.term}: Fee {b.term_fee} + Arrears {b.previous_arrears} = {b.total_due} (Paid: {b.amount_paid}, Balance: {b.current_balance})')

print()
print('EXPECTED FOR SECOND TERM 2027:')
print('  Fee: $100')
print('  Arrears from T1 2027: $400')
print('  Expected Balance: $500')
