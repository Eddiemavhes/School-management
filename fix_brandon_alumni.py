#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student

brandon = Student.all_students.get(first_name='Brandon')
print(f"Brandon before: Status={brandon.status}, Archived={brandon.is_archived}")

brandon.is_archived = True
brandon.save()

print(f"Brandon after: Status={brandon.status}, Archived={brandon.is_archived}")
