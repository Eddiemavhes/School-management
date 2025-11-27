#!/usr/bin/env python
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.models.fee import StudentBalance
from core.models.academic import Payment
from django.db.models import Sum

# Use ID 8 directly
michael = Student.objects.get(id=8)

print('MICHAEL JOHNSON - COMPLETE FINANCIAL HISTORY')
print('=' * 80)
print(f'Student ID: {michael.id}')
print(f'Name: {michael.first_name} {michael.surname}')
print(f'Current Class: Grade {michael.current_class.grade}')
print()

# Get all balances
balances = StudentBalance.objects.filter(student=michael).order_by('term__academic_year', 'term__term')

print('ALL STUDENT BALANCES:')
print(f'Count: {balances.count()}')
if balances.exists():
    for b in balances:
        print(f'\nTerm {b.term.term} ({b.term.academic_year}):')
        print(f'  Term Fee: ${b.term_fee}')
        print(f'  Previous Arrears: ${b.previous_arrears}')
        print(f'  Amount Paid: ${b.amount_paid}')
        print(f'  Current Balance: ${b.current_balance}')
else:
    print('ERROR: NO STUDENT BALANCES FOUND!')

# Get all payments
print('\nALL PAYMENTS:')
payments = Payment.objects.filter(student=michael).order_by('payment_date')
print(f'Count: {payments.count()}')
if payments.exists():
    for p in payments:
        print(f'{p.payment_date} - Term {p.term.term}: ${p.amount}')
else:
    print('No payments recorded')

print()
print('SUMMARY:')
total_due = balances.aggregate(total=Sum('term_fee'))['total']
total_paid = payments.aggregate(total=Sum('amount'))['total']
print(f'Total Due (all terms): ${total_due}')
print(f'Total Paid: ${total_paid}')
if total_due and total_paid:
    print(f'Outstanding: ${total_due - total_paid}')
elif total_due:
    print(f'Outstanding: ${total_due}')


