#!/usr/bin/env python
"""
Reset database - keep admin/login data, delete everything else
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.contrib.auth.models import Group
from core.models import (
    Student, Class, AcademicYear, AcademicTerm,
    Payment, Administrator, TeacherAssignmentHistory
)
from core.models.fee import StudentBalance, TermFee

print("=" * 70)
print("DATABASE CLEANUP - Keeping Admin Users, Deleting All Data")
print("=" * 70)
print()

# Count existing data
print("BEFORE CLEANUP:")
print(f"  Administrators: {Administrator.objects.count()}")
print(f"  Students: {Student.objects.count()}")
print(f"  Classes: {Class.objects.count()}")
print(f"  Academic Years: {AcademicYear.objects.count()}")
print(f"  Academic Terms: {AcademicTerm.objects.count()}")
print(f"  Payments: {Payment.objects.count()}")
print(f"  Student Balances: {StudentBalance.objects.count()}")
print(f"  Term Fees: {TermFee.objects.count()}")
print(f"  Teacher Assignments: {TeacherAssignmentHistory.objects.count()}")
print()

# Delete in order (respecting foreign keys)
print("DELETING DATA...")
print()

# Delete payments first (they reference terms and students)
deleted, _ = Payment.objects.all().delete()
print(f"✓ Deleted Payments: {deleted} records")

# Delete student balances (they reference students and terms)
deleted, _ = StudentBalance.objects.all().delete()
print(f"✓ Deleted Student Balances: {deleted} records")

# Delete term fees (they reference terms)
deleted, _ = TermFee.objects.all().delete()
print(f"✓ Deleted Term Fees: {deleted} records")

# Delete students
deleted, _ = Student.objects.all().delete()
print(f"✓ Deleted Students: {deleted} records")

# Delete classes (they reference academic years)
deleted, _ = Class.objects.all().delete()
print(f"✓ Deleted Classes: {deleted} records")

# Delete teachers
deleted, _ = TeacherAssignmentHistory.objects.all().delete()
print(f"✓ Deleted Teacher Assignments: {deleted} records")

# Delete academic terms
deleted, _ = AcademicTerm.objects.all().delete()
print(f"✓ Deleted Academic Terms: {deleted} records")

# Delete academic years
deleted, _ = AcademicYear.objects.all().delete()
print(f"✓ Deleted Academic Years: {deleted} records")

# Reset all Administrators - remove teacher flag
Administrator.objects.all().update(is_teacher=False)
print(f"✓ Reset all Administrators - removed teacher flag")

print()
print("=" * 70)
print("AFTER CLEANUP:")
print(f"  Administrators (kept): {Administrator.objects.count()}")
print(f"  Students: {Student.objects.count()}")
print(f"  Classes: {Class.objects.count()}")
print(f"  Academic Years: {AcademicYear.objects.count()}")
print(f"  Academic Terms: {AcademicTerm.objects.count()}")
print(f"  Payments: {Payment.objects.count()}")
print(f"  Student Balances: {StudentBalance.objects.count()}")
print(f"  Term Fees: {TermFee.objects.count()}")
print(f"  Teacher Assignments: {TeacherAssignmentHistory.objects.count()}")
print()
print("=" * 70)
print("✓ DATABASE RESET COMPLETE")
print("=" * 70)
print()
print("Remaining admin users (keep these credentials for login):")
for user in Administrator.objects.all():
    print(f"  - Email: {user.email} (Name: {user.first_name} {user.last_name})")
print()
