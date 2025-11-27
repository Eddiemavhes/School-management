#!/usr/bin/env python
"""
Clear all data from the database except the admin user - Complete fresh system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import (
    AcademicYear, AcademicTerm, Class, 
    Student, StudentBalance, Payment, StudentMovement, TermFee, Administrator,
    TeacherAssignmentHistory
)
from core.models.school_details import SchoolDetails

# Preserve admin user info
admin_users = Administrator.objects.all().count()
print(f"✓ Preserving {admin_users} admin users")

# Clear data
models_to_clear = [
    (Payment, 'Payments'),
    (StudentBalance, 'Student Balances'),
    (TermFee, 'Term Fees'),
    (StudentMovement, 'Student Movements'),
    (Student, 'Students'),
    (TeacherAssignmentHistory, 'Teacher Assignments'),
    (Class, 'Classes'),
    (AcademicTerm, 'Academic Terms'),
    (AcademicYear, 'Academic Years'),
    (SchoolDetails, 'School Details'),
]

for model, name in models_to_clear:
    count = model.objects.count()
    if count > 0:
        model.objects.all().delete()
        print(f"✓ Deleted {count} {name}")
    else:
        print(f"- No {name} to delete")

print("\n✅ Database cleared completely! Fresh system ready.")
print("✓ Admin users preserved for login")
print("✓ Ready to configure fresh school setup")
