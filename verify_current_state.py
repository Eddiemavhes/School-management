#!/usr/bin/env python
"""
Verify current academic year, term, and classroom structure.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicYear, AcademicTerm, Class, Student

print("=" * 70)
print("ACADEMIC YEAR VERIFICATION")
print("=" * 70)

# Check academic years
years = AcademicYear.objects.all().order_by('year')
print(f"\nAcademic Years in Database: {years.count()}")
for year in years:
    print(f"  • {year.year}: Active={year.is_active}, Start={year.start_date}, End={year.end_date}")

print("\n" + "=" * 70)
print("ACADEMIC TERMS")
print("=" * 70)

for year in years:
    terms = AcademicTerm.objects.filter(academic_year=year.year).order_by('term')
    print(f"\n{year.year}: {terms.count()} terms")
    for term in terms:
        print(f"  • Term {term.term}: {term.get_term_display()} (Active={term.is_current})")
        print(f"    Dates: {term.start_date} to {term.end_date}")

print("\n" + "=" * 70)
print("CLASSROOM STRUCTURE")
print("=" * 70)

for year in years:
    classes = Class.objects.filter(academic_year=year.year).order_by('grade', 'section')
    print(f"\n{year.year}: {classes.count()} classrooms")
    by_grade = {}
    for cls in classes:
        grade = cls.grade
        if grade not in by_grade:
            by_grade[grade] = []
        by_grade[grade].append(cls)
    
    for grade in sorted(by_grade.keys()):
        sections = ", ".join([f"{cls.section}" for cls in by_grade[grade]])
        print(f"  Grade {grade}: {sections}")

print("\n" + "=" * 70)
print("STUDENT DISTRIBUTION")
print("=" * 70)

for year in years:
    students = Student.objects.filter(current_class__academic_year=year.year, is_active=True).count()
    print(f"\n{year.year}: {students} active students")
    
    # Show breakdown by class
    classes = Class.objects.filter(academic_year=year.year).order_by('grade', 'section')
    for cls in classes:
        count = cls.students.filter(is_active=True).count()
        if count > 0:
            students_list = ", ".join([s.full_name for s in cls.students.filter(is_active=True)])
            print(f"  {cls}: {count} student(s) - {students_list}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
