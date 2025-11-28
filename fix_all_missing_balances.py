import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.fee import StudentBalance
from core.models.academic import AcademicTerm

current_term = AcademicTerm.get_current_term()
print(f"Current Term: {current_term}\n")

# Find all ACTIVE, ENROLLED students
active_students = Student.objects.filter(is_active=True, status='ENROLLED', is_deleted=False)

print(f"Checking {active_students.count()} active enrolled students...\n")

missing_balance = []
for student in active_students:
    balance = StudentBalance.objects.filter(student=student, term=current_term).first()
    if not balance:
        missing_balance.append(student)
        print(f"❌ {student.full_name} ({student.current_class}) - NO balance in {current_term}")

print(f"\n\nTotal with missing balance: {len(missing_balance)}")

if len(missing_balance) > 0:
    print("\nInitializing missing balances...")
    for student in missing_balance:
        balance = StudentBalance.initialize_term_balance(student, current_term)
        print(f"  ✅ {student.full_name}: balance = ${balance.current_balance}")
