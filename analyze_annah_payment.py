#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance, Payment

# Find Annah
student = Student.objects.filter(first_name='Annah').first()
if not student:
    # Try alternate spellings
    student = Student.objects.filter(surname__icontains='annah').first()

if student:
    print("=" * 80)
    print(f"ANALYZING: {student.first_name} {student.surname}")
    print("=" * 80)
    print()
    
    print(f"Overall Balance Displayed: ${student.overall_balance}")
    print()
    
    print("ALL PAYMENTS:")
    print("-" * 80)
    payments = Payment.objects.filter(student=student).order_by('payment_date')
    if payments.exists():
        total_paid = 0
        for p in payments:
            total_paid += p.amount
            print(f"  {p.payment_date}: ${p.amount} for {p.term}")
        print(f"  TOTAL PAID: ${total_paid}")
    else:
        print("  No payments found")
    print()
    
    print("ALL BALANCES:")
    print("-" * 80)
    balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
    for b in balances:
        print(f"  {b.term}:")
        print(f"    Term Fee: ${b.term_fee}")
        print(f"    Previous Arrears: ${b.previous_arrears}")
        print(f"    Total Due: ${b.total_due}")
        print(f"    Amount Paid: ${b.amount_paid}")
        print(f"    Current Balance: ${b.current_balance}")
        
        # Check for issues
        if b.current_balance < 0:
            print(f"    ⚠️  CREDIT: ${abs(b.current_balance)} (OVERPAID)")
        if b.amount_paid > b.total_due:
            print(f"    ⚠️  OVERPAID: Paid ${b.amount_paid} but only owed ${b.total_due}")
        print()
    
    print()
    print("ANALYSIS:")
    print("-" * 80)
    
    # Latest balance
    latest_balance = balances.last()
    if latest_balance:
        print(f"Latest Term: {latest_balance.term}")
        print(f"  Fee: ${latest_balance.term_fee}")
        print(f"  Arrears from previous: ${latest_balance.previous_arrears}")
        print(f"  Total owed: ${latest_balance.total_due}")
        print(f"  Amount paid: ${latest_balance.amount_paid}")
        print(f"  Current balance: ${latest_balance.current_balance}")
        print()
        
        if latest_balance.amount_paid > latest_balance.term_fee:
            overpayment = latest_balance.amount_paid - latest_balance.term_fee
            print(f"  ❗ PAYMENT LOGIC ISSUE:")
            print(f"     Paid: ${latest_balance.amount_paid}")
            print(f"     Fee: ${latest_balance.term_fee}")
            print(f"     Arrears: ${latest_balance.previous_arrears}")
            print(f"     Expected balance: ${latest_balance.total_due - latest_balance.amount_paid}")
            print(f"     Actual balance: ${latest_balance.current_balance}")
            
            if latest_balance.current_balance != (latest_balance.total_due - latest_balance.amount_paid):
                print(f"     🔴 MISMATCH: Balance calculation is wrong!")
else:
    print("❌ Student 'Annah' not found")
