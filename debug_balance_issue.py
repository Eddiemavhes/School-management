#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.academic import AcademicTerm
from core.models.student import Student
from core.models.fee import StudentBalance

print("=" * 60)
print("DEBUGGING BALANCE CALCULATION ISSUE")
print("=" * 60)

# Check current term
current = AcademicTerm.get_current_term()
print(f"\nCurrent Term: {current}")
print(f"Current Year: {current.academic_year if current else 'None'}")

# Check if 2030 terms exist
year_2030_terms = AcademicTerm.objects.filter(academic_year=2030).exists()
print(f"\n2030 Academic Year terms exist: {year_2030_terms}")

# Get David Duck's balances
s = Student.objects.get(id=64)
print(f"\nStudent: {s.full_name} (ID: {s.id})")

# Query: What does the API actually use?
current_year = AcademicTerm.get_current_term().academic_year if AcademicTerm.get_current_term() else 2029
print(f"\nFilter criteria (FIXED): term__academic_year={current_year} (exact match, current year ONLY)")

all_balances = StudentBalance.objects.filter(student=s, term__academic_year=current_year)
print(f"Balances matching filter (exactly {current_year}):")
for b in all_balances:
    print(f"  {b.term.academic_year} T{b.term.term}: {b.current_balance}")

filtered = [b for b in all_balances if b.current_balance > 0]
total = sum([float(b.current_balance) for b in filtered])
print(f"\nFiltered (> 0): {len(filtered)} records")
for b in filtered:
    print(f"  {b.term.academic_year} T{b.term.term}: {b.current_balance}")
print(f"\nCalculated total_outstanding: {total}")
print(f"Expected: 1080.0 (only 2029 T1)")
print(f"Actual: {total}")
print(f"✓ CORRECT: {total == 1080.0}")

print("\n" + "=" * 60)
print("ISSUE ANALYSIS")
print("=" * 60)
if total != 1080.0:
    print(f"ERROR: total_outstanding should be 1080.0, got {total}")
    print(f"Extra amount: ${total - 1080.0}")
    print(f"\nCause: The 2030 T1 ($100) balance is being included")
    print(f"Solution: Filter to CURRENT YEAR ONLY, not >= current year")
