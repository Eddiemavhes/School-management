#!/usr/bin/env python
"""
Database Reset Script - Keeps Administrator Login (Clean Version)
Removes all data except the admin user credentials, and removes teacher role
"""

import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import (
    Administrator, Class, Student, AcademicTerm, 
    Payment, TermFee, StudentBalance, AcademicYear, 
    TeacherAssignmentHistory
)

def reset_database():
    """Reset database keeping only Administrator login - clean version"""
    
    print("=" * 60)
    print("DATABASE RESET - CLEAN VERSION")
    print("=" * 60)
    
    try:
        # Delete all data in order (respecting foreign keys)
        print("\n📍 Deleting data...\n")
        
        # 1. Delete StudentBalance
        count = StudentBalance.objects.all().delete()[0]
        print(f"  ✓ Deleted {count} StudentBalance records")
        
        # 2. Delete TermFee
        count = TermFee.objects.all().delete()[0]
        print(f"  ✓ Deleted {count} TermFee records")
        
        # 3. Delete Payment
        count = Payment.objects.all().delete()[0]
        print(f"  ✓ Deleted {count} Payment records")
        
        # 4. Delete TeacherAssignmentHistory
        count = TeacherAssignmentHistory.objects.all().delete()[0]
        print(f"  ✓ Deleted {count} TeacherAssignmentHistory records")
        
        # 5. Delete Student
        count = Student.objects.all().delete()[0]
        print(f"  ✓ Deleted {count} Student records")
        
        # 6. Delete Class
        count = Class.objects.all().delete()[0]
        print(f"  ✓ Deleted {count} Class records")
        
        # 7. Delete AcademicTerm
        count = AcademicTerm.objects.all().delete()[0]
        print(f"  ✓ Deleted {count} AcademicTerm records")
        
        # 8. Delete AcademicYear
        count = AcademicYear.objects.all().delete()[0]
        print(f"  ✓ Deleted {count} AcademicYear records")
        
        # 9. Clean up Administrator roles - only keep main admin
        print(f"\n📍 Cleaning up Administrator roles...\n")
        
        # Get the main admin (admin@admin.com)
        main_admin = Administrator.objects.get(email='admin@admin.com')
        print(f"  ✓ Main admin: {main_admin.email}")
        
        # Update other admins - remove teacher role
        other_admins = Administrator.objects.exclude(email='admin@admin.com')
        for admin in other_admins:
            admin.is_teacher = False
            admin.specialization = ''
            admin.qualification = ''
            admin.teacher_id = ''
            admin.phone_number = ''
            admin.joining_date = None
            admin.bio = ''
            admin.save()
            print(f"  ✓ Cleaned up: {admin.email} (removed teacher role)")
        
        remaining_admins = Administrator.objects.count()
        print(f"\n  ✓ Kept {remaining_admins} Administrator user(s)")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE RESET COMPLETE!")
        print("=" * 60)
        print("\n📝 ADMIN LOGIN PRESERVED:")
        for admin in Administrator.objects.all():
            status = "🔐 Main Admin" if admin.email == 'admin@admin.com' else "👤 Regular"
            print(f"   {status}: {admin.email} ({admin.full_name})")
        print("\n✨ All other data removed. All teacher roles removed.")
        print("🚀 System is ready for fresh testing!\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("Please ensure Django is properly configured.")
        return False
    
    return True

if __name__ == '__main__':
    reset_database()
