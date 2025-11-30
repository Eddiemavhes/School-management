#!/usr/bin/env python
"""
TEST: Year-End Graduation Trigger
Verify that Grade 7 auto-graduation fires when 2028 Term 1 is activated
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm, Class
from decimal import Decimal

print("="*80)
print("TEST: YEAR-END GRADUATION TRIGGER")
print("="*80)

# Check current state of students
print("\n1️⃣  CHECKING CURRENT STUDENT STATUS...")
students_to_check = ['Annah', 'Brandon', 'Cathrine', 'David']

student_states = {}
for name in students_to_check:
    student = Student.all_students.filter(first_name=name).first()
    if student:
        status_info = f"Status={student.status}, Active={student.is_active}, Archived={student.is_archived}"
        student_states[name] = student.status
        print(f"  {name}: {status_info}")

# Verify their state before activation
print("\n2️⃣  STUDENTS BEFORE 2028 TERM 1 ACTIVATION:")
for name in students_to_check:
    student = Student.objects.filter(first_name=name).first()
    if student:
        final_balance = StudentBalance.objects.filter(
            student=student,
            term__academic_year=2027
        ).order_by('-term__term').first()
        
        balance_text = f"${final_balance.current_balance:.2f}" if final_balance else "No balance"
        print(f"  {name}: Status={student.status}, Active={student.is_active}, Archived={student.is_archived}, 2027 Final={balance_text}")

# Now activate 2028 Term 1 - this should trigger graduation
print("\n3️⃣  ACTIVATING 2028 FIRST TERM...")
term_2028_t1 = AcademicTerm.objects.filter(academic_year=2028, term=1).first()

if term_2028_t1:
    term_2028_t1.is_current = True
    term_2028_t1.save()  # This triggers the signal!
    print(f"  ✓ Activated {term_2028_t1}")
else:
    print("  ❌ 2028 Term 1 does not exist!")
    print("\nCreating 2028 Term 1 first...")
    from datetime import date
    
    term = AcademicTerm.objects.create(
        academic_year=2028,
        term=1,
        start_date=date(2028, 1, 15),
        end_date=date(2028, 4, 15),
        is_current=True
    )
    print(f"  ✓ Created and activated {term}")
    term_2028_t1 = term

# Verify their state AFTER activation
print("\n4️⃣  STUDENTS AFTER 2028 TERM 1 ACTIVATION:")
all_passed = True

for name in students_to_check:
    student = Student.all_students.filter(first_name=name).first()
    if student:
        final_balance = StudentBalance.objects.filter(
            student=student,
            term__academic_year=2027
        ).order_by('-term__term').first()
        
        print(f"\n  {name}:")
        print(f"    Status: {student.status}")
        print(f"    Active: {student.is_active}")
        print(f"    Archived: {student.is_archived}")
        
        if final_balance:
            if final_balance.current_balance <= 0:
                expected_archived = True
                status_text = "ALUMNI ✓"
            else:
                expected_archived = False
                status_text = "GRADUATED (not alumni) ✓"
            
            if student.status == 'GRADUATED' and student.is_archived == expected_archived:
                print(f"    ✅ Status correct: {status_text}")
            else:
                print(f"    ❌ Status WRONG: Expected {status_text}, got Status={student.status}, Archived={student.is_archived}")
                all_passed = False
        else:
            print(f"    ⚠️  No final balance found")

print("\n" + "="*80)
if all_passed:
    print("✅ YEAR-END GRADUATION TRIGGER: WORKING CORRECTLY!")
else:
    print("❌ YEAR-END GRADUATION TRIGGER: HAS ISSUES")
print("="*80)
