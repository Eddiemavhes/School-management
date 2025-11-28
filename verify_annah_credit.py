#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student

student = Student.objects.filter(first_name='Annah').first()

if student:
    print(f"Student: {student.first_name} {student.surname}")
    print(f"Overall Balance: ${student.overall_balance}")
    print()
    
    if student.overall_balance < 0:
        print(f"✅ Student has a CREDIT of: ${abs(student.overall_balance)}")
        print(f"   This should display as: 'Credit: ${abs(student.overall_balance)}' in UI")
    elif student.overall_balance == 0:
        print(f"✅ Student has PAID in FULL")
    else:
        print(f"❌ Student OWES: ${student.overall_balance}")
