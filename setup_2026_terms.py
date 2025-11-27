#!/usr/bin/env python
"""
Quick Setup Script - Creates complete academic structure for testing
This creates 2026 with all 3 terms and appropriate dates
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicYear, AcademicTerm, TermFee
from datetime import datetime

print("=" * 70)
print("🎓 QUICK SETUP - Creating Academic Structure for 2026")
print("=" * 70)

# Check if 2026 already exists
year_2026 = AcademicYear.objects.filter(year=2026).first()
if not year_2026:
    print("\n❌ Academic Year 2026 not found!")
    print("   Please create it manually first in Django Admin")
    exit(1)

print(f"\n✓ Using Active Year: 2026 (Active={year_2026.is_active})")

# Delete existing terms to start fresh
existing_terms = AcademicTerm.objects.filter(academic_year=2026)
if existing_terms.exists():
    print(f"\n⚠ Removing {existing_terms.count()} existing terms for 2026...")
    existing_terms.delete()

# Create the three terms
print("\n📍 Creating Academic Terms...\n")

terms_data = [
    (1, '2026-01-01', '2026-03-31', 1000, True),  # Term 1 as current
    (2, '2026-04-01', '2026-08-31', 1000, False),
    (3, '2026-09-01', '2026-12-31', 1000, False),
]

for term_num, start, end, fee_amount, is_current in terms_data:
    term = AcademicTerm.objects.create(
        academic_year=2026,
        term=term_num,
        start_date=start,
        end_date=end,
        is_current=is_current
    )
    
    # Create fee for the term
    term_fee = TermFee.objects.create(
        term=term,
        amount=fee_amount,
        due_date=end
    )
    
    current_mark = "🔴 CURRENT" if is_current else "⚪"
    print(f"  ✓ CREATED: Term {term_num}")
    print(f"           {start} to {end}")
    print(f"           Fee: ${fee_amount} | {current_mark}")
    print()

# Verify
print("=" * 70)
print("✅ VERIFICATION - Final State")
print("=" * 70)

terms = AcademicTerm.objects.filter(academic_year=2026).order_by('term')
print(f"\nTotal Terms: {terms.count()}")
for t in terms:
    current_indicator = "🔴 CURRENT" if t.is_current else "⚪ INACTIVE"
    print(f"\n  Term {t.term}:")
    print(f"    Dates: {t.start_date} → {t.end_date}")
    print(f"    Status: {current_indicator}")
    
    # Show fee
    fee = TermFee.objects.filter(term=t).first()
    if fee:
        print(f"    Fee: ${fee.amount}")

print("\n" + "=" * 70)
print("✨ SETUP COMPLETE!")
print("=" * 70)
print("""
You can now:
1. Login to the system: http://localhost:8000/
2. Go to Dashboard → Settings
3. See all terms and fees displayed
4. Add students and start testing!

📝 Next Steps:
   → Create classrooms (Grade 1-7, Sections A-B)
   → Add students
   → Test bulk promotion
""")
