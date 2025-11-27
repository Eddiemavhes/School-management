#!/usr/bin/env python
"""
Debug script to test creating academic terms
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicYear, AcademicTerm, TermFee
from datetime import datetime

# Check current state
print("=" * 60)
print("BEFORE CREATION")
print("=" * 60)

years = AcademicYear.objects.all()
print(f"\nAcademic Years: {years.count()}")
for y in years:
    print(f"  - {y.year} (Active={y.is_active})")

terms = AcademicTerm.objects.all()
print(f"\nAcademic Terms: {terms.count()}")
for t in terms:
    print(f"  - Term {t.term} {t.academic_year} (Current={t.is_current})")

fees = TermFee.objects.all()
print(f"\nTerm Fees: {fees.count()}")

# Create terms manually
print("\n" + "=" * 60)
print("CREATING TERMS")
print("=" * 60)

current_year = AcademicYear.objects.filter(is_active=True).first()
if not current_year:
    print("ERROR: No active academic year found!")
else:
    print(f"\nUsing active year: {current_year.year}")
    
    # Create Term 1
    term1, created1 = AcademicTerm.objects.update_or_create(
        academic_year=current_year.year,
        term=1,
        defaults={
            'start_date': '2026-01-01',
            'end_date': '2026-03-31',
            'is_current': True
        }
    )
    print(f"  ✓ Term 1 created: {created1}")
    
    # Create Term 2
    term2, created2 = AcademicTerm.objects.update_or_create(
        academic_year=current_year.year,
        term=2,
        defaults={
            'start_date': '2026-04-01',
            'end_date': '2026-08-31',
            'is_current': False
        }
    )
    print(f"  ✓ Term 2 created: {created2}")
    
    # Create Term 3
    term3, created3 = AcademicTerm.objects.update_or_create(
        academic_year=current_year.year,
        term=3,
        defaults={
            'start_date': '2026-09-01',
            'end_date': '2026-12-31',
            'is_current': False
        }
    )
    print(f"  ✓ Term 3 created: {created3}")

# Check final state
print("\n" + "=" * 60)
print("AFTER CREATION")
print("=" * 60)

terms = AcademicTerm.objects.all()
print(f"\nAcademic Terms: {terms.count()}")
for t in terms:
    print(f"  - Term {t.term} {t.academic_year}: {t.start_date} to {t.end_date} (Current={t.is_current})")
