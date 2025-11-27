import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Class, AcademicYear

print('\n' + '='*70)
print('CLASS INVENTORY BY ACADEMIC YEAR')
print('='*70)

# Get active year
active_year = AcademicYear.objects.filter(is_active=True).first()
print(f'\nActive Year: {active_year.year if active_year else "None"}')

# Count all classes
all_classes = Class.objects.all()
print(f'\nTotal Classes in System: {all_classes.count()}')

# Show classes by year
print('\nClasses by Academic Year:')
for year in AcademicYear.objects.order_by('-year'):
    classes = Class.objects.filter(academic_year=year.year)
    status = 'ACTIVE' if year.is_active else 'inactive'
    print(f'  {year.year} ({status}): {classes.count()} class(es)')
    for cls in classes:
        teacher = cls.teacher.full_name if cls.teacher else 'None'
        print(f'    - Grade {cls.grade}{cls.section} (Teacher: {teacher})')

# Show what form will display
if active_year:
    form_classes = Class.objects.filter(academic_year=active_year.year)
    print(f'\nClasses showing in Student Create Form: {form_classes.count()}')
    if form_classes.count() > 0:
        for cls in form_classes.order_by('grade', 'section'):
            print(f'  - Grade {cls.grade}{cls.section}')
    else:
        print('  WARNING: No classes available for active year!')

print('\n' + '='*70 + '\n')
