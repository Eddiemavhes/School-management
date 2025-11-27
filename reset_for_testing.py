#!/usr/bin/env python
"""
Reset database - keep admin users, clear everything else
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

# Delete in order of dependencies (reverse of creation order)
print("🧹 Clearing all data except administrators...\n")

# Disable foreign key constraints temporarily
cursor = connection.cursor()

# Delete in dependency order
models_to_clear = [
    'core_payment',
    'core_studentbalance',
    'core_termfee',
    'core_academicterm',
    'core_student',
    'core_class',
    'core_academicyear',
    'core_teacherassignmenthistory',
]

for table in models_to_clear:
    try:
        cursor.execute(f"DELETE FROM {table}")
        print(f"  ✓ Cleared {table}")
    except Exception as e:
        print(f"  ⚠ {table}: {str(e)[:50]}")

connection.commit()
print("\n" + "="*60)
print("DATABASE RESET COMPLETE - Ready for Testing")
print("="*60)
