#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, AcademicTerm, StudentBalance
from decimal import Decimal

student = Student.objects.get(first_name='Edwin', surname='Mavhe')
current_term = AcademicTerm.objects.filter(is_current=True).first()

print(f"Current Term: {current_term}")
print(f"Student: {student.first_name} {student.surname}")
print()

# Check if balance already exists
try:
    balance = StudentBalance.objects.get(student=student, term=current_term)
    print(f"Balance already exists for {current_term}")
    print(f"Fee: {balance.term_fee}, Arrears: {balance.previous_arrears}, Current: {balance.current_balance}")
except StudentBalance.DoesNotExist:
    print(f"Creating balance for {current_term}...")
    
    # Get previous term balance
    previous_term = AcademicTerm.objects.filter(academic_year=current_term.academic_year, term=1).first()
    if previous_term:
        try:
            prev_balance = StudentBalance.objects.get(student=student, term=previous_term)
            arrears = prev_balance.current_balance
            print(f"Previous term ({previous_term}) balance: {prev_balance.current_balance}")
        except StudentBalance.DoesNotExist:
            arrears = Decimal('0.00')
            print(f"No previous term balance found, using 0 arrears")
    else:
        arrears = Decimal('0.00')
        print(f"Could not find previous term, using 0 arrears")
    
    # Get the term fee
    from core.models import TermFee
    try:
        term_fee_obj = TermFee.objects.get(term=current_term)
        term_fee = term_fee_obj.amount
    except TermFee.DoesNotExist:
        term_fee = Decimal('100.00')
        print(f"No TermFee found, using default $100")
    
    print(f"Term Fee: {term_fee}")
    print(f"Arrears to carry forward: {arrears}")
    print(f"Expected total due: {term_fee + arrears}")
    
    # Create the balance
    balance = StudentBalance.objects.create(
        student=student,
        term=current_term,
        term_fee=term_fee,
        previous_arrears=arrears
    )
    print(f"✅ Balance created!")
    print(f"   Fee: {balance.term_fee}")
    print(f"   Arrears: {balance.previous_arrears}")
    print(f"   Total: {balance.total_due}")

print()
print(f"Overall Balance: {student.overall_balance}")
print()

# Show all balances
print('All Balance Records After Fix:')
balances = StudentBalance.objects.filter(student=student).order_by('term__academic_year', 'term__term')
for b in balances:
    print(f'  {b.term}: Fee {b.term_fee} + Arrears {b.previous_arrears} = {b.total_due} (Balance: {b.current_balance})')
