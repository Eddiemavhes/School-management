#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, Class

student = Student.objects.get(first_name='Edwin', surname='Mavhe')

print(f"Student: {student.first_name} {student.surname}")
print(f"Current Class: {student.current_class}")
print(f"Is Active: {student.is_active}")
print()

# Show all available grades
print("Available classes in system:")
for cls in Class.objects.all().order_by('grade'):
    count = cls.students.count()
    print(f"  {cls.grade}: {cls.name} ({count} students)")
print()

# What should happen:
print("GRADE 7 LOGIC:")
print("  - Grade 7 students who PAY their full arrears → Auto-graduate to ALUMNI")
print("  - Grade 7 students who DON'T pay → Stay in Grade 7 but DON'T get new year fees")
print()
print("YOUR ISSUE:")
print("  - Edwin is Grade 7A (from 2027)")
print("  - Edwin never paid (still owes $600 from 2027)")
print("  - Edwin shouldn't have 2028 fees added (Grade 7 who didn't graduate)")
print("  - But system added 2028 T1 fee anyway → showing $700")
