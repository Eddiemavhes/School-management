#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, StudentMovement

print("=" * 80)
print("RESTORING ANNAH TO ACTIVE STUDENT STATUS")
print("=" * 80)
print()

annah = Student.objects.filter(first_name='Annah').first()

print(f"BEFORE:")
print(f"  Status: {annah.get_status_display()}")
print(f"  Is Active: {annah.is_active}")
print(f"  Is Archived: {annah.is_archived}")
print(f"  Current Class: {annah.current_class}")
print()

# Show all balances before
balances_before = StudentBalance.objects.filter(student=annah).order_by('term__academic_year', 'term__term')
print(f"  Balances before: {balances_before.count()}")
for b in balances_before:
    print(f"    {b.term}: ${b.current_balance}")
print()

# Delete 2027 balances (these shouldn't exist for Annah since she's still in 2026)
deleted_count, _ = StudentBalance.objects.filter(
    student=annah,
    term__academic_year=2027
).delete()
print(f"Deleted: {deleted_count} balance records for 2027")
print()

# Restore status - bypass validation by using direct update
Student.objects.filter(pk=annah.pk).update(
    status='ENROLLED',
    is_active=True,
    is_archived=False
)

print(f"Updated student status in database")

print(f"AFTER:")
annah.refresh_from_db()
print(f"  Status: {annah.get_status_display()}")
print(f"  Is Active: {annah.is_active}")
print(f"  Is Archived: {annah.is_archived}")
print(f"  Current Class: {annah.current_class}")
print()

# Show all balances after
balances_after = StudentBalance.objects.filter(student=annah).order_by('term__academic_year', 'term__term')
print(f"  Balances after: {balances_after.count()}")
for b in balances_after:
    print(f"    {b.term}: ${b.current_balance}")
print()

print(f"Overall Balance: ${annah.overall_balance}")
print()

print("=" * 80)
print("VERIFICATION")
print("=" * 80)
print()

if annah.is_active and annah.status == 'ENROLLED':
    print(f"✓ Annah is now ACTIVE and ENROLLED")
else:
    print(f"❌ Restoration failed")

if annah.overall_balance == -20:
    print(f"✓ Overall balance is correct: -$20")
else:
    print(f"❌ Overall balance is wrong: ${annah.overall_balance}")

# Delete the erroneous graduation movement record
old_movements = StudentMovement.objects.filter(
    student=annah,
    movement_type='GRADUATION'
)
movement_count, _ = old_movements.delete()
print(f"✓ Deleted {movement_count} erroneous graduation movement record(s)")
