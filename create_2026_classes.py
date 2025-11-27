import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Class, AcademicYear

print('\n' + '='*70)
print('CREATING CLASSES FOR 2026')
print('='*70)

# Get active year
active_year = AcademicYear.objects.filter(is_active=True).first()
if not active_year:
    print('ERROR: No active academic year')
    exit(1)

print(f'\nActive Year: {active_year.year}')

# Define all grades and sections that should exist
grades = [1, 2, 3, 4, 5, 6, 7]
sections = ['A', 'B']

created_count = 0
skipped_count = 0

print(f'\nCreating classes for grades 1-7, sections A & B...\n')

for grade in grades:
    for section in sections:
        try:
            # Check if class already exists
            existing = Class.objects.filter(
                grade=grade,
                section=section,
                academic_year=active_year.year
            ).exists()
            
            if existing:
                print(f'  ✓ Grade {grade}{section} (2026) - Already exists')
                skipped_count += 1
            else:
                # Create new class
                new_class = Class.objects.create(
                    grade=grade,
                    section=section,
                    academic_year=active_year.year,
                    teacher=None  # No teacher assigned yet
                )
                print(f'  ✓ Grade {grade}{section} (2026) - CREATED')
                created_count += 1
        except Exception as e:
            print(f'  ✗ Grade {grade}{section} - ERROR: {e}')

print(f'\n' + '='*70)
print(f'Summary:')
print(f'  Created: {created_count}')
print(f'  Already Existed: {skipped_count}')
print(f'  Total in 2026: {Class.objects.filter(academic_year=active_year.year).count()}')
print('='*70 + '\n')

# Verify
total = Class.objects.filter(academic_year=active_year.year).count()
expected = len(grades) * len(sections)
if total == expected:
    print(f'✅ SUCCESS! All {expected} classes are now available for year {active_year.year}')
else:
    print(f'⚠️  WARNING: Expected {expected} classes but have {total}')

print('\n')
