#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm, StudentBalance

current_term = AcademicTerm.objects.filter(is_current=True).first()
active_students = Student.objects.filter(is_active=True, is_deleted=False)

print(f"Current Term: {current_term}")
print(f"Re-initializing all active student balances...")
print()

for student in active_students:
    try:
        balance = StudentBalance.initialize_term_balance(student, current_term)
        if balance:
            print(f"✅ {student.first_name} {student.surname}: Fee ${balance.term_fee} + Arrears ${balance.previous_arrears} = ${balance.total_due}")
        else:
            print(f"⚠️  {student.first_name} {student.surname}: Skipped (returned None)")
    except Exception as e:
        print(f"❌ {student.first_name} {student.surname}: Error - {e}")

print()
print("Re-initialization complete!")
