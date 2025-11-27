import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Class, Student

print("=" * 70)
print("CURRENT SYSTEM STATE")
print("=" * 70)

print("\n2025 CLASSES:")
classes_2025 = Class.objects.filter(academic_year=2025).order_by('grade', 'section')
for cls in classes_2025:
    students = cls.students.all()
    print(f"  {cls}: {students.count()} students", end="")
    if students.count() > 0:
        for student in students:
            print(f" - {student.full_name}", end="")
    print()

print("\n2026 CLASSES:")
classes_2026 = Class.objects.filter(academic_year=2026).order_by('grade', 'section')
for cls in classes_2026:
    students = cls.students.all()
    print(f"  {cls}: {students.count()} students", end="")
    if students.count() > 0:
        for student in students:
            print(f" - {student.full_name}", end="")
    print()

print("\n" + "=" * 70)
print("WHEN ROLLOVER HAPPENS (2025 → 2026):")
print("=" * 70)

students = Student.objects.filter(is_active=True)
for student in students:
    if student.current_class:
        current_grade = student.current_class.grade
        current_section = student.current_class.section
        next_grade = current_grade + 1
        
        if next_grade <= 7:
            print(f"{student.full_name}:")
            print(f"  Current: Grade {current_grade}{current_section} (2025)")
            print(f"  Will move to: Grade {next_grade}{current_section} (2026)")
        else:
            print(f"{student.full_name}:")
            print(f"  Current: Grade {current_grade}{current_section} (2025)")
            print(f"  Will: GRADUATE")
