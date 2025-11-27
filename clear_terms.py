#!/usr/bin/env python
"""
Clear all academic terms and fees - start fresh
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm, TermFee

print("=" * 70)
print("🗑️  CLEARING ALL ACADEMIC TERMS AND FEES")
print("=" * 70)

# Get counts before deletion
terms_count = AcademicTerm.objects.count()
fees_count = TermFee.objects.count()

print(f"\n📍 BEFORE DELETION:")
print(f"  • Terms: {terms_count}")
print(f"  • Fees: {fees_count}")

if terms_count == 0 and fees_count == 0:
    print("\n✅ Nothing to delete - already clean!")
else:
    # Delete all fees first (they depend on terms)
    print(f"\n🗑️  Deleting {fees_count} Term Fees...")
    TermFee.objects.all().delete()
    
    # Delete all terms
    print(f"🗑️  Deleting {terms_count} Academic Terms...")
    AcademicTerm.objects.all().delete()
    
    # Verify
    print("\n📍 AFTER DELETION:")
    print(f"  • Terms: {AcademicTerm.objects.count()}")
    print(f"  • Fees: {TermFee.objects.count()}")
    
    print("\n" + "=" * 70)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 70)
    print("""
You can now:
1. Go to http://localhost:8000/settings/
2. Fill in new dates and fees for all 3 terms
3. Click "Save All Terms & Fees"
4. All terms will be created fresh!
""")
