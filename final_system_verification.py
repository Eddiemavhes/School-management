import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.fee import StudentBalance
from core.models.academic import AcademicTerm

print("="*70)
print("FINAL VERIFICATION - COMPLETE SYSTEM CHECK")
print("="*70 + "\n")

current_term = AcademicTerm.get_current_term()
print(f"Current Term: {current_term}\n")

# Get Edwin
edwin = Student.objects.filter(first_name='Edwin', is_active=True).first()

if not edwin:
    print("❌ Edwin not found")
    exit()

print(f"Student: {edwin.full_name}")
print(f"Grade: {edwin.current_class}")
print(f"Status: {edwin.status}")
print(f"Overall Balance: ${edwin.overall_balance}\n")

# Get all balances
all_balances = StudentBalance.objects.filter(student=edwin).order_by('term__academic_year', 'term__term')

print(f"Balance Records ({all_balances.count()} total):\n")
for balance in all_balances:
    print(f"  {balance.term}: Fee ${balance.term_fee} + Arrears ${balance.previous_arrears} = ${balance.current_balance}")

print(f"\n" + "="*70)
print(f"VALIDATION CHECKS")
print(f"="*70 + "\n")

checks = {
    "Has 4 balance records": len(all_balances) == 4,
    "2026 T1 balance = $100": all_balances[0].current_balance == 100,
    "2026 T2 balance = $200": all_balances[1].current_balance == 200,
    "2026 T3 balance = $300": all_balances[2].current_balance == 300,
    "2027 T1 balance = $400": all_balances[3].current_balance == 400,
    "overall_balance = $400": edwin.overall_balance == 400,
    "2026 T3 arrears = $200": all_balances[2].previous_arrears == 200,
    "2027 T1 arrears = $300": all_balances[3].previous_arrears == 300,
}

all_passed = True
for check_name, result in checks.items():
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
    if not result:
        all_passed = False

print(f"\n" + "="*70)
if all_passed:
    print(f"✅✅✅ ALL CHECKS PASSED! System working correctly.")
else:
    print(f"❌ Some checks failed. Please review above.")
print(f"="*70)
