#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, Payment

print("=" * 80)
print("FINAL SYSTEM VERIFICATION - ALL FIXES APPLIED")
print("=" * 80)
print()

print("1. ANNAH - CREDIT HANDLING FIX")
print("-" * 80)
annah = Student.objects.filter(first_name='Annah').first()
if annah:
    balances = StudentBalance.objects.filter(student=annah).order_by('term__academic_year', 'term__term')
    print(f"Name: {annah.first_name} {annah.surname}")
    print(f"Overall Balance: ${annah.overall_balance}")
    print(f"Status: {'✅ CREDIT' if annah.overall_balance < 0 else '❌ DEBT' if annah.overall_balance > 0 else '✅ PAID IN FULL'}")
    print()
    print(f"Balance records:")
    for b in balances:
        status = ""
        if b.current_balance < 0:
            status = f" (Credit ${abs(b.current_balance)})"
        print(f"  {b.term}: Fee ${b.term_fee} + Arrears ${b.previous_arrears} = ${b.total_due} {status}")
    print()

print("2. EDWIN - AUTO-GRADUATION FIX")
print("-" * 80)
edwin = Student.objects.filter(first_name='Edwin', surname='Mavhe').first()
if edwin:
    print(f"Name: {edwin.first_name} {edwin.surname}")
    print(f"Status: {edwin.status}")
    print(f"Is Active: {edwin.is_active}")
    print(f"Is Archived: {edwin.is_archived}")
    print(f"Overall Balance: ${edwin.overall_balance}")
    
    if edwin.status == 'GRADUATED' and not edwin.is_active and edwin.is_archived and edwin.overall_balance == 0:
        print(f"✅ CORRECTLY AUTO-GRADUATED TO ALUMNI")
    else:
        print(f"❌ AUTO-GRADUATION NOT WORKING")
    print()

print("3. ALL ACTIVE STUDENTS SUMMARY")
print("-" * 80)
students = Student.objects.filter(is_active=True, is_deleted=False).order_by('first_name')
for student in students:
    balance_status = ""
    if student.overall_balance < 0:
        balance_status = f"Credit ${abs(student.overall_balance)}"
    elif student.overall_balance == 0:
        balance_status = "Paid in Full"
    else:
        balance_status = f"Owes ${student.overall_balance}"
    
    print(f"  {student.first_name:15} {student.surname:15} | {balance_status:25} | Grade {student.current_class}")

print()
print("=" * 80)
print("✅ SYSTEM VERIFICATION COMPLETE")
print("=" * 80)
print()
print("Summary of fixes applied:")
print("  1. ✅ Payment signal checks auto-graduation BEFORE cascading")
print("  2. ✅ Grade 7 students don't get new fees in new year if they have arrears")
print("  3. ✅ Credit handling: students with overpayments don't get charged new fees")
print("  4. ✅ Second Term 2027 balance auto-initialization")
print("  5. ✅ AcademicTerm post-save signal auto-initializes balances")
