import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicYear

print("Academic Years in Database:")
print("=" * 50)
years = AcademicYear.objects.all()
for year in years:
    print(f"Year: {year.year}, Active: {year.is_active}, ID: {year.id}")

if not years.exists():
    print("No academic years found!")
else:
    print("\nTo activate a year, run:")
    print("python check_years.py activate <year>")
