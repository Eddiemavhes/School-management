import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicYear, AcademicTerm, TermFee
from core.models.fee import StudentBalance

print("Performing Year Rollover...\n")

try:
    # Get the current active academic year
    current_year = AcademicYear.objects.filter(is_active=True).first()
    
    if not current_year:
        print("ERROR: No active academic year found!")
        exit(1)
    
    print(f"Current Academic Year: {current_year.year}")
    print(f"Starting rollover process...\n")
    
    # Check if next year already has terms - if so, clean it up
    next_year_obj = AcademicYear.objects.filter(year=current_year.year + 1).first()
    
    if next_year_obj:
        print(f"Academic Year {current_year.year + 1} already exists - removing to recreate it properly...")
        existing_terms = AcademicTerm.objects.filter(academic_year=current_year.year + 1)
        if existing_terms.exists():
            print(f"  Cleaning up {existing_terms.count()} existing terms")
            # Delete StudentBalance first (they reference terms)
            StudentBalance.objects.filter(term__academic_year=current_year.year + 1).delete()
            # Delete TermFees (they reference terms)
            TermFee.objects.filter(term__academic_year=current_year.year + 1).delete()
            # Then delete the terms
            existing_terms.delete()
        # Delete the academic year itself
        next_year_obj.delete()
        print("  Removed Academic Year {}\n".format(current_year.year + 1))
    
    # Perform rollover
    print("Executing rollover...")
    new_year = current_year.rollover_to_new_year()
    
    print("\n" + "=" * 60)
    print("✓ ROLLOVER SUCCESSFUL!")
    print("=" * 60)
    print(f"\nNew Academic Year Created: {new_year.year}")
    
    # Show the new terms
    new_terms = AcademicTerm.objects.filter(academic_year=new_year.year)
    print(f"\nTerms Created ({new_terms.count()}):")
    for term in new_terms:
        print(f"  - {term}: {term.start_date} to {term.end_date}")
    
    # Show promoted students
    from core.models import Student
    promoted_students = Student.objects.filter(current_class__academic_year=new_year.year)
    print(f"\nStudents Promoted: {promoted_students.count()}")
    for student in promoted_students[:10]:
        print(f"  - {student.full_name} → {student.current_class}")
    
except Exception as e:
    print(f"\nERROR during rollover: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
