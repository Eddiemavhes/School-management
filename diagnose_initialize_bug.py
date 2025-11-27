import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.fee import StudentBalance
from core.models.academic import Payment, AcademicTerm
from core.models.student import Student
from decimal import Decimal

# Fresh test: Get Carol's current state
carol = Student.objects.filter(first_name='Carol', surname='Cross').first()

print("\n" + "=" * 100)
print("SIMULATING THE EXACT BUG")
print("=" * 100)

terms = AcademicTerm.objects.filter(academic_year=2026).order_by('term')
balances_dict = {}

for term in terms:
    balance = StudentBalance.objects.get(student=carol, term=term)
    balances_dict[term.term] = balance
    print(f"\n{term.get_term_display()}:")
    print(f"  previous_arrears (DB): ${balance.previous_arrears}")
    print(f"  term_fee: ${balance.term_fee}")
    print(f"  amount_paid: ${balance.amount_paid}")
    print(f"  total_due: ${balance.total_due}")
    print(f"  current_balance: ${balance.current_balance}")

# Now simulate calling initialize_term_balance on each term
print("\n" + "=" * 100)
print("AFTER CALLING initialize_term_balance() ON EACH TERM")
print("=" * 100)

for term in terms:
    # This is what happens when a payment is recorded
    balance = StudentBalance.initialize_term_balance(carol, term)
    print(f"\n{term.get_term_display()}:")
    print(f"  previous_arrears (after init): ${balance.previous_arrears}")
    print(f"  term_fee: ${balance.term_fee}")
    print(f"  amount_paid: ${balance.amount_paid}")
    print(f"  current_balance: ${balance.current_balance}")
    
# Now check if they changed
print("\n" + "=" * 100)
print("DID ANYTHING CHANGE?")
print("=" * 100)

for term in terms:
    balance = StudentBalance.objects.get(student=carol, term=term)
    old_val = balances_dict[term.term].previous_arrears
    new_val = balance.previous_arrears
    if old_val != new_val:
        print(f"{term.get_term_display()}: previous_arrears changed from ${old_val} to ${new_val} ❌")
    else:
        print(f"{term.get_term_display()}: previous_arrears unchanged ✓")
