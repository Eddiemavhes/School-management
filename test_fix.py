import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
import django
django.setup()

from core.models import Student, StudentBalance, AcademicTerm

students = Student.objects.filter(id__in=[6, 7, 8])

for s in students:
    # Get directly from database
    ct = AcademicTerm.get_current_term()
    sb = StudentBalance.objects.filter(student=s, term=ct).first()
    
    print(f"\n{s.full_name}:")
    if sb:
        print(f"  From DB - Fee: {sb.term_fee}, Arrears: {sb.previous_arrears}, Paid: {sb.amount_paid}, Balance: {sb.current_balance}")
    
    # Get from property
    print(f"  From Property - Arrears: {s.previous_term_arrears}, Balance: {s.current_term_balance}")
