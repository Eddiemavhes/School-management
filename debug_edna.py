from core.models.student import Student

# Check all students
print("\n" + "="*70)
print("ALL STUDENTS IN DATABASE")
print("="*70)

for student in Student.objects.all().order_by('surname'):
    print(f"\nStudent ID: {student.id}")
    print(f"  Name: {student.full_name} (First: {student.first_name}, Surname: {student.surname})")
    print(f"  Status: {student.status}")
    print(f"  Is Active: {student.is_active}")
    print(f"  Is Archived: {student.is_archived}")
    print(f"  Overall Balance: ${student.overall_balance:.2f}")
    print(f"  Current Class: {student.current_class}")
    print(f"  Payments: {student.payments.count()}")

print("\n" + "="*70)
print("ANALYSIS")
print("="*70)

# Find students that should be archived
should_archive = []
for student in Student.objects.all():
    if not student.is_active and student.status == 'GRADUATED' and not student.is_archived and student.overall_balance <= 0:
        should_archive.append(student)

print(f"\nStudents that should be archived: {len(should_archive)}")
for s in should_archive:
    print(f"  - {s.full_name}")

print("\nStudents that are inactive but NOT graduated:")
for student in Student.objects.filter(is_active=False):
    print(f"  - {student.full_name}: Status={student.status}, Balance=${student.overall_balance:.2f}")
