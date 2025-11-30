#!/usr/bin/env python
"""
Check student status - why are all students inactive?
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student

print("=" * 80)
print("📊 STUDENT STATUS ANALYSIS")
print("=" * 80)

all_students = Student.all_students.all()
print(f"\nTotal students (including deleted): {all_students.count()}")

# Group by status
print("\n📈 BY STATUS:")
for status_value, status_label in Student.STATUS_CHOICES:
    count = all_students.filter(status=status_value).count()
    print(f"  {status_label}: {count}")

print("\n📈 BY ACTIVE STATUS:")
active = all_students.filter(is_active=True).count()
inactive = all_students.filter(is_active=False).count()
print(f"  Active (is_active=True): {active}")
print(f"  Inactive (is_active=False): {inactive}")

print("\n📈 BY ARCHIVE STATUS:")
archived = all_students.filter(is_archived=True).count()
not_archived = all_students.filter(is_archived=False).count()
print(f"  Archived: {archived}")
print(f"  Not Archived: {not_archived}")

print("\n📈 BY DELETED STATUS:")
deleted = all_students.filter(is_deleted=True).count()
not_deleted = all_students.filter(is_deleted=False).count()
print(f"  Deleted (soft): {deleted}")
print(f"  Not Deleted: {not_deleted}")

print("\n" + "=" * 80)
print("📋 DETAILED STUDENT LIST (Not Deleted):")
print("=" * 80)

active_students = Student.objects.filter(is_active=True)
all_not_deleted = Student.all_students.filter(is_deleted=False)

print(f"\nUsing Student.objects (default - excludes deleted): {active_students.count()}")
print(f"Using Student.all_students (includes deleted): {all_not_deleted.count()}")

# Show some students
print("\nFirst 10 students (all_students, not deleted):")
for i, student in enumerate(all_not_deleted[:10], 1):
    status_icon = "🟢" if student.is_active else "🔴"
    archived_icon = "📦" if student.is_archived else " "
    print(f"{i}. {status_icon} {archived_icon} {student.full_name}")
    print(f"   Status: {student.status}, is_active: {student.is_active}, is_archived: {student.is_archived}, is_deleted: {student.is_deleted}")

print("\n" + "=" * 80)
print("⚠️  ISSUE IDENTIFIED:")
print("=" * 80)

if active_students.count() == 0:
    print("\n🔴 NO ACTIVE STUDENTS FOUND")
    print("\nPossible reasons:")
    print("1. All students were marked as GRADUATED when 2028 was activated")
    print("2. System auto-graduated 2027 students, marking them is_active=False")
    print("\nSOLUTION:")
    print("→ Students need to be re-enrolled OR")
    print("→ Previous year's students need to be marked as ACTIVE again")
    print("→ New students need to be created")
else:
    print(f"\n✓ Found {active_students.count()} active students")

print("\n" + "=" * 80)
