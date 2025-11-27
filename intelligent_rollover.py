import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicYear, Class, Student
from django.db import transaction

print("Performing INTELLIGENT Year Rollover...\n")
print("This will reuse existing classes by promoting their grades")
print("=" * 60)

try:
    # Get current and next years
    current_year = AcademicYear.objects.filter(is_active=True, year=2025).first()
    next_year = AcademicYear.objects.filter(year=2026).first()
    
    if not current_year or not next_year:
        print("ERROR: Could not find 2025 or 2026 academic years!")
        exit(1)
    
    print(f"\nCurrent Year: {current_year.year}")
    print(f"Next Year: {next_year.year}\n")
    
    with transaction.atomic():
        # Step 1: Get all classes in current year sorted by grade (descending)
        # We process from highest grade down to avoid conflicts
        classes_by_grade = Class.objects.filter(
            academic_year=current_year.year
        ).order_by('-grade')  # Process from highest grade first
        
        print(f"Processing {classes_by_grade.count()} classes for promotion...\n")
        
        promoted_classes = []
        grade_1_classes = []  # These stay in place for new students
        
        for cls in classes_by_grade:
            if cls.grade < 7:  # Classes before the final grade get promoted
                # Update the class to next grade in new academic year
                old_grade = cls.grade
                old_year = cls.academic_year
                
                cls.grade = cls.grade + 1
                cls.academic_year = next_year.year
                cls.save()
                
                promoted_classes.append(f"Grade {old_grade}{cls.section} ({old_year}) → Grade {cls.grade}{cls.section} ({cls.academic_year})")
                print(f"✓ Promoted: Grade {old_grade}{cls.section} ({old_year}) → Grade {cls.grade}{cls.section} ({cls.academic_year})")
            else:
                # Grade 7 students graduate
                print(f"✓ Grade {cls.grade}{cls.section} - Students graduating, class remains as is")
        
        print(f"\n" + "=" * 60)
        print(f"Class Promotions Complete!")
        print(f"Total classes promoted: {len(promoted_classes)}")
        
        # Now students automatically move with their classes
        # Update student records for proper display
        students = Student.objects.filter(is_active=True)
        promoted_students = 0
        graduated_students = 0
        
        print(f"\nUpdating student records...")
        for student in students:
            if student.current_class:
                if student.current_class.grade == 7:
                    # Student is graduating
                    student.is_active = False
                    student.save()
                    graduated_students += 1
                    print(f"✓ {student.full_name} graduated from {student.current_class}")
                else:
                    promoted_students += 1
                    print(f"✓ {student.full_name} promoted to {student.current_class}")
        
        print(f"\n" + "=" * 60)
        print("ROLLOVER SUCCESSFUL!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  Classes promoted: {len(promoted_classes)}")
        print(f"  Students promoted: {promoted_students}")
        print(f"  Students graduated: {graduated_students}")
        
        # Show final state
        print(f"\nClasses now in 2026:")
        for cls in Class.objects.filter(academic_year=2026).order_by('grade', 'section'):
            student_count = cls.students.count()
            print(f"  - {cls} ({student_count} student{'s' if student_count != 1 else ''})")

except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
