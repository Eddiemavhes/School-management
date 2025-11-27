import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.fee import StudentBalance
from core.models.academic import Payment
from core.models.student import Student
from decimal import Decimal

print("=" * 80)
print("COMPREHENSIVE FIX FOR ALL STUDENTS - PAYMENT AND ARREARS")
print("=" * 80)

# Get all students
all_students = Student.objects.all().order_by('id')

issues_found = []
issues_fixed = 0

for student in all_students:
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    balances_list = list(balances)
    
    if not balances_list:
        continue
    
    student_has_issues = False
    
    # Fix 1: Correct amount_paid
    for balance in balances_list:
        # Get actual payments for this term
        payments = Payment.objects.filter(student=student, term=balance.term)
        actual_paid = sum(p.amount for p in payments)
        
        if actual_paid != balance.amount_paid:
            if not student_has_issues:
                issues_found.append(f"\n{student.full_name} (ID: {student.id})")
                print(f"\n{student.full_name} (ID: {student.id})")
                student_has_issues = True
            
            print(f"  {balance.term.get_term_display()} {balance.term.academic_year}")
            print(f"    amount_paid: ${balance.amount_paid} → ${actual_paid}")
            balance.amount_paid = actual_paid
            balance.save(update_fields=['amount_paid'])
            issues_fixed += 1
    
    # Fix 2: Correct previous_arrears carryover
    for i, balance in enumerate(balances_list):
        if i == 0:
            calculated_arrears = Decimal('0')
        else:
            prev_balance = balances_list[i-1]
            calculated_arrears = prev_balance.current_balance
        
        if calculated_arrears != balance.previous_arrears:
            if not student_has_issues:
                issues_found.append(f"\n{student.full_name} (ID: {student.id})")
                print(f"\n{student.full_name} (ID: {student.id})")
                student_has_issues = True
            
            print(f"  {balance.term.get_term_display()} {balance.term.academic_year}")
            print(f"    previous_arrears: ${balance.previous_arrears} → ${calculated_arrears}")
            balance.previous_arrears = calculated_arrears
            balance.save(update_fields=['previous_arrears'])
            issues_fixed += 1

print(f"\n" + "=" * 80)
print(f"SUMMARY: {issues_fixed} issues fixed")
print("=" * 80)

# Final verification for Carol
print("\n" + "=" * 80)
print("CAROL'S FINAL STATE")
print("=" * 80)

carol = Student.objects.filter(first_name='Carol', surname='Cross').first()
if carol:
    balances = StudentBalance.objects.filter(student=carol).order_by('term__academic_year', 'term__term')
    for balance in balances:
        print(f"\n{balance.term.get_term_display()} {balance.term.academic_year}")
        print(f"  Fee: ${balance.term_fee} | Arrears: ${balance.previous_arrears} | Total Due: ${balance.total_due}")
        print(f"  Paid: ${balance.amount_paid} | Outstanding: ${balance.current_balance}")
