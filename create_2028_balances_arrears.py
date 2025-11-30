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
print("CREATING 2028 BALANCES FOR STUDENTS WITH ARREARS (NO NEW FEES)")
print("=" * 80)
print()

current_term = AcademicTerm.objects.filter(is_current=True).first()
print(f"Current Term: {current_term}\n")

# Students with arrears who should NOT get new fees
students_with_arrears = ['Cathrine', 'David']

for name in students_with_arrears:
    student = Student.objects.filter(first_name=name).first()
    
    print(f"{name}:")
    print(f"  Status: {student.get_status_display()}")
    print(f"  Class: {student.current_class}")
    print(f"  Is Active: {student.is_active}")
    
    # Get their 2027 final balance
    final_2027 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2027,
        term__term=3
    ).first()
    
    if final_2027:
        print(f"  2027 Final Balance: ${final_2027.current_balance}")
    
    # Check if they already have 2028 Term 1 balance
    existing_2028 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2028,
        term__term=1
    ).first()
    
    if existing_2028:
        print(f"  2028 Term 1 Already Exists:")
        print(f"    Fee: ${existing_2028.term_fee}")
        print(f"    Arrears: ${existing_2028.previous_arrears}")
        # Delete it first
        existing_2028.delete()
        print(f"    Deleted old record")
    
    # Now create correct balance using initialize_term_balance
    term1_2028 = AcademicTerm.objects.filter(academic_year=2028, term=1).first()
    balance = StudentBalance.initialize_term_balance(student, term1_2028)
    
    print(f"  2028 Term 1 Created:")
    print(f"    Fee: ${balance.term_fee} (should be $0 for Grade 7 with arrears)")
    print(f"    Arrears: ${balance.previous_arrears}")
    print(f"    Balance: ${balance.current_balance}")
    
    if balance.term_fee == 0:
        print(f"    ✓ Correct: No new fee charged")
    else:
        print(f"    ❌ Error: Should have $0 fee!")
    
    print()

print("=" * 80)
print("VERIFICATION")
print("=" * 80)
print()

for name in students_with_arrears:
    student = Student.objects.filter(first_name=name).first()
    
    balance_2028 = StudentBalance.objects.filter(
        student=student,
        term__academic_year=2028,
        term__term=1
    ).first()
    
    if balance_2028:
        print(f"{name}:")
        print(f"  2028 Term 1 Balance: ${balance_2028.current_balance}")
        print(f"  Composition: ${balance_2028.term_fee} (fee) + ${balance_2028.previous_arrears} (arrears from 2027)")
        print()
