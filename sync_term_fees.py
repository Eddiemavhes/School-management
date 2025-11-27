import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.fee import TermFee
from core.models.academic import AcademicTerm

# Get Second Term 2027
term2 = AcademicTerm.objects.filter(academic_year=2027, term=2).first()

if term2:
    term_fee = TermFee.objects.filter(term=term2).first()
    if term_fee:
        print(f"Found Term 2 Fee: ${term_fee.amount}")
        print(f"Updating to: $120.00")
        term_fee.amount = 120.00
        term_fee.save()
        print(f"✅ Updated! New amount: ${term_fee.amount}")
    else:
        print("Term Fee not found for Term 2 2027")
else:
    print("Term not found")
