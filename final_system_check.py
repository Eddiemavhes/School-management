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
print("FINAL SYSTEM STATE - CORRECT GRADE 7 POLICY")
print("=" * 80)
print()

current_term = AcademicTerm.objects.filter(is_current=True).first()
print(f"Current Term: {current_term}\n")

students = Student.objects.filter(first_name__in=['Annah', 'Brandon', 'Cathrine', 'David']).order_by('first_name')

for student in students:
    print(f"{student.first_name} {student.surname}:")
    print(f"  Status: {student.get_status_display()}")
    print(f"  Class: {student.current_class}")
    print(f"  Is Active: {student.is_active}")
    print(f"  Is Archived: {student.is_archived}")
    
    # Get current term balance
    current_balance = StudentBalance.objects.filter(
        student=student,
        term=current_term
    ).first()
    
    if current_balance:
        print(f"  Current Term Balance: ${current_balance.current_balance}")
    
    print(f"  Overall Balance: ${student.overall_balance}")
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()

expectations = {
    'Annah': ('ENROLLED', True, False, -20),
    'Brandon': ('ENROLLED', True, False, 0),
    'Cathrine': ('ENROLLED', True, False, 20),
    'David': ('ENROLLED', True, False, 200),
}

all_pass = True
for name, (status, is_active, is_archived, balance) in expectations.items():
    student = Student.objects.filter(first_name=name).first()
    
    status_ok = student.status == status
    active_ok = student.is_active == is_active
    archived_ok = student.is_archived == is_archived
    balance_ok = float(student.overall_balance) == balance
    
    all_pass = all_pass and status_ok and active_ok and archived_ok and balance_ok
    
    status_str = "✓" if status_ok else "❌"
    active_str = "✓" if active_ok else "❌"
    archived_str = "✓" if archived_ok else "❌"
    balance_str = "✓" if balance_ok else "❌"
    
    print(f"{name}:")
    print(f"  {status_str} Status: {student.get_status_display()} (expected {status})")
    print(f"  {active_str} Active: {student.is_active} (expected {is_active})")
    print(f"  {archived_str} Archived: {student.is_archived} (expected {is_archived})")
    print(f"  {balance_str} Balance: ${student.overall_balance} (expected ${balance})")
    print()

print("=" * 80)
if all_pass:
    print("✓✓✓ ALL STUDENTS CORRECT - Grade 7 Policy Fixed!")
else:
    print("❌ Some students still have issues")
print("=" * 80)
