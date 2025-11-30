#!/usr/bin/env python
"""
COMPLETE SYSTEM RESET
Wipes ALL data except admin/superuser accounts
Resets all auto-increment sequences to 1
"""
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import (
    Administrator, Student, Class, AcademicYear, AcademicTerm,
    StudentBalance, Payment, StudentMovement, TeacherAssignmentHistory, TermFee
)
from core.models.school_details import SchoolDetails

print("=" * 80)
print("⚠️  COMPLETE SYSTEM RESET - ALL DATA WILL BE DELETED")
print("=" * 80)
print("\nThis will:")
print("  ✓ Delete ALL students")
print("  ✓ Delete ALL classes")
print("  ✓ Delete ALL academic years/terms")
print("  ✓ Delete ALL payments and balances")
print("  ✓ Delete ALL student movements")
print("  ✓ Delete ALL teacher assignments")
print("  ✓ Reset ALL ID sequences to 1")
print("  ✓ PRESERVE admin/superuser accounts")
print("\nWARNING: This action cannot be undone!")

response = input("\nType 'RESET' to confirm: ").strip()

if response != 'RESET':
    print("\n❌ Reset cancelled.")
    exit(1)

print("\n" + "=" * 80)
print("STARTING RESET PROCESS...")
print("=" * 80)

try:
    # Step 1: Save admin/superuser data
    print("\n📋 STEP 1: Backing up admin accounts...")
    admins = list(Administrator.objects.all())
    superusers = list(Administrator.objects.filter(is_superuser=True))
    print(f"  ✓ Found {len(admins)} admin(s)")
    print(f"  ✓ Found {len(superusers)} superuser(s)")
    
    # Step 2: Delete all student-related data
    print("\n🗑️  STEP 2: Deleting student data...")
    
    count_students = Student.all_students.count()
    Student.all_students.all().delete()
    print(f"  ✓ Deleted {count_students} students")
    
    count_movements = StudentMovement.objects.count()
    StudentMovement.objects.all().delete()
    print(f"  ✓ Deleted {count_movements} student movements")
    
    count_balances = StudentBalance.objects.count()
    StudentBalance.objects.all().delete()
    print(f"  ✓ Deleted {count_balances} student balances")
    
    count_payments = Payment.objects.count()
    Payment.objects.all().delete()
    print(f"  ✓ Deleted {count_payments} payments")
    
    # Step 3: Delete academic structure
    print("\n📚 STEP 3: Deleting academic structure...")
    
    count_assignments = TeacherAssignmentHistory.objects.count()
    TeacherAssignmentHistory.objects.all().delete()
    print(f"  ✓ Deleted {count_assignments} teacher assignments")
    
    count_fees = TermFee.objects.count()
    TermFee.objects.all().delete()
    print(f"  ✓ Deleted {count_fees} term fees")
    
    count_classes = Class.objects.count()
    Class.objects.all().delete()
    print(f"  ✓ Deleted {count_classes} classes")
    
    count_terms = AcademicTerm.objects.count()
    AcademicTerm.objects.all().delete()
    print(f"  ✓ Deleted {count_terms} academic terms")
    
    count_years = AcademicYear.objects.count()
    AcademicYear.objects.all().delete()
    print(f"  ✓ Deleted {count_years} academic years")
    
    count_school = SchoolDetails.objects.count()
    SchoolDetails.objects.all().delete()
    print(f"  ✓ Deleted {count_school} school details")
    
    # Step 4: Reset auto-increment sequences
    print("\n🔄 STEP 4: Resetting ID sequences...")
    
    with connection.cursor() as cursor:
        # Models to reset (in order of dependencies)
        models_to_reset = [
            ('core_academicyear', 'id'),
            ('core_academicterm', 'id'),
            ('core_termfee', 'id'),
            ('core_class', 'id'),
            ('core_student', 'id'),
            ('core_studentbalance', 'id'),
            ('core_payment', 'id'),
            ('core_studentmovement', 'id'),
            ('core_teacherassignmenthistory', 'id'),
            ('core_schooldetails', 'id'),
        ]
        
        for table_name, id_col in models_to_reset:
            try:
                # For SQLite, reset the sequence
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
                print(f"  ✓ Reset {table_name} ID sequence")
            except Exception as e:
                print(f"  ⚠️  Could not reset {table_name}: {str(e)}")
    
    # Step 5: Verify admin accounts still exist
    print("\n✅ STEP 5: Verifying admin accounts...")
    
    remaining_admins = Administrator.objects.all()
    remaining_superusers = Administrator.objects.filter(is_superuser=True)
    
    print(f"  ✓ {remaining_admins.count()} admin account(s) preserved")
    for admin in remaining_admins:
        print(f"    - {admin.email}: {admin.first_name} {admin.last_name}")
    
    print(f"  ✓ {remaining_superusers.count()} superuser account(s) preserved")
    for user in remaining_superusers:
        print(f"    - {user.email}")
    
    print("\n" + "=" * 80)
    print("✅ SYSTEM RESET COMPLETE!")
    print("=" * 80)
    print("\n🆕 System is now in factory-fresh state")
    print("   All IDs will start from 1")
    print("   Admin accounts can log in normally")
    print("   Ready for fresh school setup!")
    
except Exception as e:
    print(f"\n❌ ERROR during reset: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
