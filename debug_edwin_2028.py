#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm, StudentBalance, StudentMovement

student = Student.objects.get(first_name='Edwin', surname='Mavhe')

print(f"Student: {student.first_name} {student.surname}")
print(f"Current Status: {'ENROLLED' if student.is_active else 'NOT ENROLLED'}")
print(f"Is Archived: {student.is_archived}")
print(f"Current Grade: {student.current_class}")
print()

# Check student movements (graduations)
movements = StudentMovement.objects.filter(student=student).order_by('movement_date')
print("Student Movements:")
if movements.exists():
    for m in movements:
        print(f"  {m.movement_date}: {m.from_class} → {m.to_class} ({m.reason})")
else:
    print("  No movements recorded")
print()

# Show all balance records
print("All Balance Records:")
balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
for b in balances:
    print(f'  {b.term} ({b.term.academic_year}): Fee ${b.term_fee} + Arrears ${b.previous_arrears} = ${b.total_due}')

print()
print("EXPECTED BEHAVIOR FOR GRADE 7:")
print("  Grade 7 students should AUTO-GRADUATE when balance reaches $0")
print("  Edwin was in Grade 7A in 2027, so he should have been archived/graduated")
print("  2028 should NOT have new fees if he was already graduated")
print()

# Check 2028 terms
terms_2028 = AcademicTerm.objects.filter(academic_year=2028).order_by('term')
if terms_2028.exists():
    print("2028 Terms in database:")
    for term in terms_2028:
        print(f"  {term}")
        balance_exists = StudentBalance.objects.filter(student=student, term=term).exists()
        print(f"    Edwin has balance: {balance_exists}")
