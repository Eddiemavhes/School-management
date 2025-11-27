from core.models.student import Student

# Search for Edna
ednas = Student.objects.filter(first_name__icontains='Edna')

if ednas.exists():
    for student in ednas:
        print(f"\n{'='*60}")
        print(f"Student: {student.full_name}")
        print(f"Status: {student.status}")
        print(f"Is Active: {student.is_active}")
        print(f"Is Archived: {student.is_archived}")
        print(f"Overall Balance: ${student.overall_balance:.2f}")
        print(f"Current Class: {student.current_class}")
        print(f"{'='*60}")
else:
    print("No student named Edna found")
