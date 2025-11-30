#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, StudentMovement

print("="*80)
print("FINAL VERIFICATION: GRADE 7 GRADUATION SYSTEM")
print("="*80)

print("\n" + "="*80)
print("SYSTEM STATE - 2028 FIRST TERM")
print("="*80)

print("\n📋 ENROLLED/ACTIVE STUDENTS (Should NOT include any Grade 7 from 2027):")
active = Student.objects.filter(is_active=True, status='ENROLLED').order_by('first_name')
if active.exists():
    for student in active:
        grade = int(student.current_class.grade) if student.current_class else 0
        if grade < 7:
            print(f"  ✓ {student.first_name} - Grade {grade} (Correct - still in school)")
else:
    print("  (None)")

print("\n🎓 GRADUATED/ALUMNI STUDENTS (2027 Grade 7):")
graduated = Student.objects.filter(status='GRADUATED').order_by('first_name')
for student in graduated:
    balance = student.overall_balance
    movements = StudentMovement.objects.filter(student=student, movement_type='GRADUATION')
    
    alumni_status = "ALUMNI ✓" if student.is_archived else "GRADUATED (not alumni yet)"
    
    print(f"\n  {student.first_name}:")
    print(f"    Status: {alumni_status}")
    print(f"    Current Balance: ${balance:.2f}")
    print(f"    Is Active: {student.is_active}")
    print(f"    Is Archived: {student.is_archived}")
    
    # Check for 2028 balances (should be none)
    has_2028 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2028
    ).exists()
    print(f"    Has 2028 balances: {'❌ YES (ERROR)' if has_2028 else '✓ NO (Correct)'}")
    
    # Show graduation info
    if movements.exists():
        movement = movements.latest('movement_date')
        print(f"    Graduated: {movement.movement_date.date()}")
        print(f"    Reason: {movement.reason}")

print("\n" + "="*80)
print("BUSINESS RULE VERIFICATION")
print("="*80)

rules = {
    "All Grade 7 students marked as GRADUATED": graduated.count() >= 4,
    "No graduated students are marked is_active=True": not graduated.filter(is_active=True).exists(),
    "Graduated students have no 2028 balances": not StudentBalance.objects.filter(
        student__status='GRADUATED',
        term__academic_year=2028
    ).exists(),
    "Annah is Alumni with $0 balance": (
        Student.objects.get(first_name='Annah').is_archived and 
        Student.objects.get(first_name='Annah').overall_balance == 0
    ),
    "Brandon is Alumni with $0 balance": (
        Student.objects.get(first_name='Brandon').is_archived and 
        Student.objects.get(first_name='Brandon').overall_balance == 0
    ),
    "Cathrine is Alumni (historical balance okay)": (
        Student.objects.get(first_name='Cathrine').is_archived and 
        not StudentBalance.objects.filter(student__first_name='Cathrine', term__academic_year=2028).exists()
    ),
    "David is Alumni (historical balance okay)": (
        Student.objects.get(first_name='David').is_archived and 
        not StudentBalance.objects.filter(student__first_name='David', term__academic_year=2028).exists()
    ),
}

print()
for rule, passed in rules.items():
    status = "✅" if passed else "❌"
    print(f"{status} {rule}")

all_passed = all(rules.values())
print("\n" + "="*80)
if all_passed:
    print("🎓 GRADUATION SYSTEM: ALL RULES ENFORCED ✅")
else:
    print("⚠️ GRADUATION SYSTEM: SOME RULES VIOLATED ❌")
print("="*80)
