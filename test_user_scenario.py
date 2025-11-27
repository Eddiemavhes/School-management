import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.fee import StudentBalance
from core.models.academic import Payment, AcademicTerm
from core.models.student import Student
from decimal import Decimal

# The user's exact scenario:
# "Carol had an arrear of 20 from term 2 and we moved to term three"
# "her total outstanding becomes 120 since 100+ 20 arrear is 120"
# "After that we paid hundred" 
# "now she is being put up as if she has no arrear"

print("\n" + "=" * 100)
print("REPRODUCING USER'S SCENARIO")
print("=" * 100)

carol = Student.objects.filter(first_name='Carol', surname='Cross').first()
current_term = AcademicTerm.get_current_term()

balance = StudentBalance.objects.get(student=carol, term=current_term)
print(f"\nCarol's {current_term.get_term_display()}:")
print(f"  previous_arrears: ${balance.previous_arrears}")
print(f"  term_fee: ${balance.term_fee}")
print(f"  total_due: ${balance.total_due}")
print(f"  amount_paid: ${balance.amount_paid}")
print(f"  current_balance: ${balance.current_balance}")
print(f"  payment_status: {balance.payment_status}")

# Now the issue: what if we check ONLY the term_fee remaining?
print(f"\n  term_fee_remaining: ${balance.term_fee_remaining}")
print(f"  arrears_remaining: ${balance.arrears_remaining}")

# The potential bug: Some code might be checking:
# "Did the student pay the term_fee? Yes ($100 >= $100)"
# And ignoring arrears

print(f"\n  BUG CHECK: Is amount_paid >= term_fee? {balance.amount_paid >= balance.term_fee}")
print(f"  This might make some code think: 'Fee is paid!'")
print(f"  But the student still owes ${balance.arrears_remaining} in arrears")
