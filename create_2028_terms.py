#!/usr/bin/env python
"""
Create academic terms for 2028 year
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.academic_year import AcademicYear
from core.models.academic import AcademicTerm
from datetime import date

# Get 2028 year
year_2028 = AcademicYear.objects.filter(year=2028).first()

if not year_2028:
    print("❌ Year 2028 not found!")
    exit(1)

print(f"📅 Creating terms for {year_2028}...")

# Define term dates for 2028
terms_data = [
    {
        'term': 1,
        'start_date': date(2028, 1, 10),
        'end_date': date(2028, 4, 10),
    },
    {
        'term': 2,
        'start_date': date(2028, 4, 20),
        'end_date': date(2028, 8, 10),
    },
    {
        'term': 3,
        'start_date': date(2028, 8, 20),
        'end_date': date(2028, 11, 30),
    },
]

for term_data in terms_data:
    term, created = AcademicTerm.objects.get_or_create(
        academic_year=2028,
        term=term_data['term'],
        defaults={
            'start_date': term_data['start_date'],
            'end_date': term_data['end_date'],
        }
    )
    
    if created:
        print(f"✅ Created {term.get_term_display()} ({term_data['start_date']} to {term_data['end_date']})")
    else:
        print(f"⏭️  {term.get_term_display()} already exists")

# Verify
terms = AcademicTerm.objects.filter(academic_year=2028).count()
print(f"\n✨ Total terms created: {terms}")
if terms == 3:
    print("🎉 All 3 terms created successfully!")
    print("\nYou can now set fees and dates in the Fee Configuration page.")
else:
    print(f"⚠️  Expected 3 terms, found {terms}")
