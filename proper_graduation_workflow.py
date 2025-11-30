#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm, StudentBalance, Student
from django.utils import timezone

# Get the 2028 term 1 (currently current)
term_2028_1 = AcademicTerm.objects.filter(academic_year=2028, term=1).first()
term_2027_3 = AcademicTerm.objects.filter(academic_year=2027, term=3).first()

print("Handling the graduation workflow properly\n")

# First, mark Term 3 2027 as completed
print(f"Step 1: Mark {term_2027_3} as completed")
term_2027_3.is_completed = True
term_2027_3.save(update_fields=['is_completed'])
print(f"  ✓ {term_2027_3} marked as completed\n")

# Second, unset current from 2028 T1 temporarily
print(f"Step 2: Temporarily unset {term_2028_1} as current")
term_2028_1.is_current = False
term_2028_1.save(update_fields=['is_current'])
print(f"  ✓ {term_2028_1} is no longer current\n")

# Third, mark Term 3 2027 as current (this will trigger the graduation signal)
print(f"Step 3: Mark {term_2027_3} as current (triggers graduation signal)")
term_2027_3.is_current = True
term_2027_3.save()  # full_clean() and signal handler will run
print(f"  ✓ {term_2027_3} marked as current\n")

# Fourth, mark 2028 T1 as current again
print(f"Step 4: Mark {term_2028_1} as current again")
term_2028_1.is_current = True
term_2028_1.save()
print(f"  ✓ {term_2028_1} marked as current\n")

# Verify the graduation happened
print("Verification - Student statuses:")
annah = Student.objects.get(id=8)
brandon = Student.objects.get(id=9)
cathrine = Student.objects.get(id=10)
david = Student.objects.get(id=11)

for student in [annah, brandon, cathrine, david]:
    student.refresh_from_db()
    balances = StudentBalance.objects.filter(student=student)
    print(f"\n{student}:")
    print(f"  Status: {student.status}, Active: {student.is_active}, Archived: {student.is_archived}")
    print(f"  Total balances: {balances.count()}")
    if balances.exists():
        latest = balances.order_by('-term__academic_year', '-term__term').first()
        print(f"  Latest: {latest.term} = ${latest.current_balance}")
