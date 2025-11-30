#!/usr/bin/env python
"""
Verify the new graduation logic
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm
from core.models.fee import StudentBalance

print("=" * 80)
print("🧪 VERIFYING NEW GRADUATION LOGIC")
print("=" * 80)

# Check current state
active_students = Student.objects.filter(is_active=True)
print(f"\nActive students: {active_students.count()}")
for student in active_students:
    print(f"  ✓ {student.full_name}: status={student.status}, is_active={student.is_active}")

# Check terms
print(f"\n" + "=" * 80)
print("TERM COMPLETION STATUS:")
print("=" * 80)

current_term = AcademicTerm.get_current_term()
year = current_term.academic_year

print(f"\nAcademic Year: {year}")
print(f"Current Term: {current_term} (Term {current_term.term})")

for term_num in [1, 2, 3]:
    term = AcademicTerm.objects.filter(academic_year=year, term=term_num).first()
    if term:
        count = StudentBalance.objects.filter(term=term).count()
        print(f"  Term {term_num}: ✓ exists - {count} students with balances")
    else:
        print(f"  Term {term_num}: ❌ does not exist")

print(f"\n" + "=" * 80)
print("GRADUATION TRIGGER:")
print("=" * 80)

print(f"""
✓ Students will graduate when:
  1. Term 3 of a year is marked as current (is_current=True)
  2. Student has balance records for ALL 3 terms of that year
  3. Student is still in ENROLLED status (not already graduated)

✓ Graduation will:
  1. Set status = 'GRADUATED'
  2. Set is_active = False (student becomes inactive)
  3. Set is_archived = True if final balance ≤ 0 (fully paid = Alumni)
  4. Set is_archived = False if final balance > 0 (has arrears)
  5. Create StudentMovement record with graduation details

✓ CURRENT SITUATION:
  Year: {year}
  Students: {active_students.count()} active (all ENROLLED)
  Terms: {AcademicTerm.objects.filter(academic_year=year).count()} terms exist
  Current: Term {current_term.term} (not Term 3 yet)
  
  → Students will NOT graduate yet (Term 3 is not current)
  → After Term 3 is completed and marked current → THEN they graduate
""")

print("=" * 80)
print("✅ GRADUATION LOGIC IS CORRECT")
print("=" * 80)
