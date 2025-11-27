#!/usr/bin/env python
"""Debug the promotion issue."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, Class

# Get Noah John
noah = Student.objects.filter(first_name='John', surname='Noah').first()
if not noah:
    print("Noah not found!")
    exit(1)

print(f"Student: {noah.full_name}")
print(f"Current Class: {noah.current_class}")
print(f"Current Grade: {noah.current_class.grade}")
print(f"Current Year: {noah.current_class.academic_year}")
print(f"Current Section: {noah.current_class.section}")

# Calculate next
next_grade = noah.current_class.grade + 1
next_year = noah.current_class.academic_year + 1
section = noah.current_class.section

print(f"\n=== LOOKING FOR NEXT CLASS ===")
print(f"Grade: {next_grade}")
print(f"Section: {section}")
print(f"Year: {next_year}")

# Try exact match
next_class = Class.objects.filter(
    grade=next_grade,
    section=section,
    academic_year=next_year
).first()

print(f"\nExact match (Grade {next_grade}{section} {next_year}): {next_class}")

if not next_class:
    print("\nExact match failed, trying any section in that grade/year...")
    next_class = Class.objects.filter(
        grade=next_grade,
        academic_year=next_year
    ).first()
    print(f"Any section (Grade {next_grade} {next_year}): {next_class}")

# Show all 2027 classes
print(f"\n=== ALL 2027 CLASSES ===")
all_2027 = Class.objects.filter(academic_year=2027).order_by('grade', 'section')
print(f"Total 2027 classes: {all_2027.count()}")
for cls in all_2027:
    print(f"  {cls}")

print(f"\n✅ Promotion should work! Found: {next_class}")
