#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm, StudentBalance

# Get all active students
active_students = Student.objects.filter(is_active=True, is_deleted=False)
current_term = AcademicTerm.objects.filter(is_current=True).first()

print(f"Current Term: {current_term}")
print(f"Active Students Count: {active_students.count()}")
print()

missing_count = 0
for student in active_students:
    try:
        balance = StudentBalance.objects.get(student=student, term=current_term)
        # Has balance
    except StudentBalance.DoesNotExist:
        missing_count += 1
        print(f"❌ {student.first_name} {student.surname} - MISSING {current_term} balance")

print()
print(f"Total Students Missing Current Term Balance: {missing_count}")
