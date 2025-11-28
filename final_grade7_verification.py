#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm, StudentBalance

student = Student.objects.get(first_name='Edwin', surname='Mavhe')
current_term = AcademicTerm.objects.filter(is_current=True).first()

print("=" * 80)
print("FINAL SYSTEM VERIFICATION - GRADE 7 LOGIC")
print("=" * 80)
print()

print(f"Current Term: {current_term}")
print(f"Student: {student.first_name} {student.surname}")
print(f"Grade: {student.current_class}")
print(f"Status: {'ENROLLED' if student.is_active else 'ARCHIVED'}")
print(f"Overall Balance: ${student.overall_balance}")
print()

print("Balance History:")
print("-" * 80)
balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
for b in balances:
    year = b.term.academic_year
    term_num = b.term.get_term_display()
    fee = b.term_fee
    arrears = b.previous_arrears
    total = b.total_due
    marker = " ← CURRENT TERM" if b.term.is_current else ""
    print(f"  {year} {term_num:15} | Fee ${fee:>6} + Arrears ${arrears:>6} = ${total:>6}{marker}")

print()
print("Verification Checks:")
print("-" * 80)

# Check 1: 2026 progression
checks = []
b_2026_t1 = balances.filter(term__academic_year=2026, term__term=1).first()
checks.append(("2026 T1 = $100", b_2026_t1 and b_2026_t1.total_due == 100))

b_2026_t3 = balances.filter(term__academic_year=2026, term__term=3).first()
checks.append(("2026 T3 = $300", b_2026_t3 and b_2026_t3.total_due == 300))

# Check 2: 2027 progression
b_2027_t1 = balances.filter(term__academic_year=2027, term__term=1).first()
checks.append(("2027 T1 = $400", b_2027_t1 and b_2027_t1.total_due == 400))

b_2027_t3 = balances.filter(term__academic_year=2027, term__term=3).first()
checks.append(("2027 T3 = $600", b_2027_t3 and b_2027_t3.total_due == 600))

# Check 3: 2028 NO NEW FEE (Grade 7 logic)
b_2028_t1 = balances.filter(term__academic_year=2028, term__term=1).first()
checks.append(("2028 T1 Fee = $0", b_2028_t1 and b_2028_t1.term_fee == 0))
checks.append(("2028 T1 Arrears = $600", b_2028_t1 and b_2028_t1.previous_arrears == 600))
checks.append(("2028 T1 Total = $600", b_2028_t1 and b_2028_t1.total_due == 600))

# Check 4: Overall balance shows latest term
checks.append(("Overall balance = $600", student.overall_balance == 600))

for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"  {status} {check_name}")

print()
print("=" * 80)
all_passed = all(result for _, result in checks)
if all_passed:
    print("✅✅✅ ALL CHECKS PASSED! System is correct.")
else:
    print("❌ SOME CHECKS FAILED! Review the system.")
print("=" * 80)
