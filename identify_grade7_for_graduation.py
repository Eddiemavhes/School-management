#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, AcademicTerm, Class

print("=" * 80)
print("IDENTIFYING GRADE 7 STUDENTS WHO SHOULD BE ALUMNI IN 2028")
print("=" * 80)
print()

current_term = AcademicTerm.objects.filter(is_current=True).first()
print(f"Current Term: {current_term}\n")

# Get all Grade 7 students currently active
grade7_students = Student.objects.filter(
    current_class__grade=7,
    is_active=True,
    is_deleted=False
)

print(f"Active Grade 7 Students: {grade7_students.count()}\n")

for student in grade7_students:
    print(f"{student.full_name}:")
    print(f"  Status: {student.get_status_display()}")
    print(f"  Class: {student.current_class}")
    print(f"  Is Archived: {student.is_archived}")
    
    # Check their 2027 history
    last_2027_balance = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2027
    ).order_by('-term__term').first()
    
    if last_2027_balance:
        print(f"  Last 2027 Balance: {last_2027_balance.term} - ${last_2027_balance.current_balance}")
    
    # Check if they have 2028 balances
    balances_2028 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2028
    ).order_by('term__term')
    
    print(f"  2028 Balances: {balances_2028.count()}")
    for b in balances_2028:
        print(f"    {b.term}: ${b.current_balance}")
    
    print()

print("=" * 80)
print("DECISION LOGIC")
print("=" * 80)
print()

print(f"""
For each Grade 7 student currently active in 2028:

1. Check if they completed 2027 (have Third Term 2027 balance)
2. Check their final 2027 balance:
   - If balance <= 0 (paid or has credit): Move to ALUMNI immediately
   - If balance > 0 (has arrears): Flag for review (arrears handling)
3. Delete any 2028 balances created for them
4. Mark as GRADUATED and ARCHIVED
""")

print()
print("=" * 80)
print("STUDENTS TO GRADUATE")
print("=" * 80)
print()

students_to_graduate = []

for student in grade7_students:
    # Check if they completed 2027
    last_2027 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2027
    ).order_by('-term__term').first()
    
    if last_2027 and last_2027.term.term == 3:  # Completed all 3 terms
        students_to_graduate.append((student, last_2027.current_balance))
        
        print(f"{student.full_name}:")
        print(f"  Final 2027 Balance: ${last_2027.current_balance}")
        
        if last_2027.current_balance <= 0:
            print(f"  ✓ Can graduate (no arrears)")
        else:
            print(f"  ⚠ Has arrears of ${last_2027.current_balance}")
        
        print()

print(f"Total students to graduate: {len(students_to_graduate)}")
