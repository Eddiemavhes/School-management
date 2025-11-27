import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicYear, AcademicTerm, Class, Student

print("=" * 60)
print("DATABASE STATUS")
print("=" * 60)

# Check Academic Years
academic_years = AcademicYear.objects.all()
print(f"\nAcademic Years: {academic_years.count()}")
for year in academic_years:
    print(f"  - {year.year}: Active={year.is_active}")

# Check Terms
terms = AcademicTerm.objects.all()
print(f"\nAcademic Terms: {terms.count()}")
for term in terms:
    print(f"  - {term} (Year {term.academic_year})")

# Check Classes
classes = Class.objects.all()
print(f"\nClasses: {classes.count()}")
for cls in classes[:10]:  # Show first 10
    print(f"  - {cls}")
if classes.count() > 10:
    print(f"  ... and {classes.count() - 10} more")

# Check Students
students = Student.objects.all()
print(f"\nStudents: {students.count()}")
for student in students[:5]:  # Show first 5
    print(f"  - {student.full_name} in {student.current_class}")
if students.count() > 5:
    print(f"  ... and {students.count() - 5} more")

print("\n" + "=" * 60)
