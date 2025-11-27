#!/usr/bin/env python
"""
Create all 2027 classrooms (physical buildings for the year).
Grades 1-7, Sections A-B = 14 classrooms total.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Class

# Create all classrooms for 2027
GRADES = range(1, 8)  # Grades 1-7
SECTIONS = ['A', 'B']
YEAR = 2027

print("=" * 70)
print(f"CREATING 2027 CLASSROOMS")
print("=" * 70)

created_count = 0
already_exist = 0

for grade in GRADES:
    for section in SECTIONS:
        try:
            cls, created = Class.objects.get_or_create(
                grade=grade,
                section=section,
                academic_year=YEAR,
                defaults={'teacher': None}
            )
            if created:
                print(f"✓ Created: Grade {grade}{section} (2027)")
                created_count += 1
            else:
                print(f"• Already exists: Grade {grade}{section} (2027)")
                already_exist += 1
        except Exception as e:
            print(f"✗ Error creating Grade {grade}{section}: {e}")

print("\n" + "=" * 70)
print(f"SUMMARY")
print("=" * 70)
print(f"Created: {created_count} new classrooms")
print(f"Already existed: {already_exist} classrooms")
print(f"Total: {created_count + already_exist} classrooms for 2027")
print("\n✅ 2027 classrooms are ready for student promotion!")
print("=" * 70)
