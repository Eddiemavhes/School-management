import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student

# Check database
total = Student.objects.count()
active = Student.objects.filter(is_deleted=False, status='active').count()

print(f"Total students: {total}")
print(f"Active students: {active}")

# Get any student
student = Student.objects.first()
if student:
    print(f"Sample: {student.full_name} - Status: {student.status} - Deleted: {student.is_deleted}")
