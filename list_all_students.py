#!/usr/bin/env python
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student

print('ALL STUDENTS IN DATABASE:')
print('=' * 80)
students = Student.objects.all()
for s in students:
    class_info = f'Grade {s.current_class.grade}' if s.current_class else 'NONE'
    print(f'ID: {s.id}, Name: {s.first_name} {s.surname}, Class: {class_info}')

print()
print('Total students:', students.count())
