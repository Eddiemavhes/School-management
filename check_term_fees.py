import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

from core.models import AcademicTerm, TermFee, StudentBalance, Student

# Check Term 1 2027
term_2027_1 = AcademicTerm.objects.filter(academic_year__year=2027, term=1).first()
print(f"Term 1 2027: {term_2027_1}")
if term_2027_1:
    print(f"  Is current: {term_2027_1.is_current}")
    print(f"  Term fees:")
    term_fees = TermFee.objects.filter(term=term_2027_1)
    if term_fees.exists():
        for tf in term_fees:
            print(f"    {tf.grade.name}: ${tf.amount}")
    else:
        print("    NO FEES SET UP")
    
    # Check if students have balances for this term
    print(f"\nStudent balances for Term 1 2027:")
    balances = StudentBalance.objects.filter(term=term_2027_1)
    if balances.exists():
        for balance in balances:
            print(f"  {balance.student.name}: ${balance.current_balance} (fee: ${balance.fee}, paid: ${balance.amount_paid})")
    else:
        print("  NO BALANCES CREATED")
else:
    print("Term 1 2027 not found")

# Check all students
print(f"\nAll active students:")
active_students = Student.objects.filter(is_active=True)
for student in active_students:
    print(f"  {student.name} (ID: {student.id}) - {student.status}")
