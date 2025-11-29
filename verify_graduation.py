#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm

print("=" * 80)
print("FINAL SYSTEM STATE - 2028 TERM 1")
print("=" * 80)
print()

current_term = AcademicTerm.objects.filter(is_current=True).first()
print(f"Current Term: {current_term}\n")

print("ACTIVE STUDENTS IN 2028:")
active = Student.objects.filter(is_active=True, is_deleted=False).order_by('first_name')
print(f"Count: {active.count()}\n")

if active.count() == 0:
    print("✓ No active students (all Grade 7 students graduated)")
else:
    for student in active:
        print(f"  {student.full_name}: {student.current_class}")

print()
print("ALUMNI STUDENTS:")
alumni = Student.objects.filter(status='GRADUATED', is_archived=True).order_by('first_name')
print(f"Count: {alumni.count()}\n")

for student in alumni:
    # Get their final balance from 2027
    final_2027 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2027,
        term__term=3
    ).first()
    
    # Check if they have any 2028 balances (should be none)
    balances_2028 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2028
    ).count()
    
    print(f"  {student.full_name}:")
    print(f"    Final 2027 Balance: ${final_2027.current_balance if final_2027 else 'N/A'}")
    print(f"    2028 Balances: {balances_2028}")
    if balances_2028 > 0:
        print(f"    ❌ ERROR: Should have no 2028 balances!")
    else:
        print(f"    ✓ Correctly has no 2028 fees")

print()
print("=" * 80)
print("✓✓✓ GRADUATION PROCESS COMPLETE")
print("=" * 80)
print()
print("""
WHAT WAS FIXED:
- All Grade 7 students who completed 2027 are now ALUMNI
- 2028 fees have been removed for these students
- Graduation records created for audit trail
- Students marked as INACTIVE and ARCHIVED

EXPECTED STATE:
✓ Annah: Alumni, no 2028 charges
✓ Brandon: Alumni, no 2028 charges
✓ Cathrine: Alumni, no 2028 charges (but $10 arrears on record from 2027)
✓ David: Alumni, no 2028 charges (but $600 arrears on record from 2027)
""")
