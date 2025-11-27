import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
import django
django.setup()

from core.models import StudentBalance, AcademicTerm
from decimal import Decimal

current_term = AcademicTerm.get_current_term()
print(f"Current Term: {current_term} (ID: {current_term.id})\n")

# Get all student balances for current term
balances = StudentBalance.objects.filter(term=current_term).select_related('student')

print("=== STUDENT BALANCES FOR CURRENT TERM ===")
total_expected = Decimal('0')
total_collected = Decimal('0')
total_arrears = Decimal('0')

for balance in balances:
    outstanding = balance.current_balance
    print(f"\n{balance.student.full_name}:")
    print(f"  Term Fee: ${balance.term_fee}")
    print(f"  Previous Arrears: ${balance.previous_arrears}")
    print(f"  Amount Paid: ${balance.amount_paid}")
    print(f"  Current Balance (Outstanding): ${outstanding}")
    
    # Calculate totals
    total_expected += balance.term_fee
    total_collected += balance.amount_paid
    total_arrears += balance.previous_arrears

print(f"\n=== DASHBOARD TOTALS ===")
print(f"Total Expected: ${total_expected}")
print(f"Total Collected: ${total_collected}")
print(f"Total Arrears (Sum of previous_arrears): ${total_arrears}")
print(f"Total Outstanding (Expected + Arrears - Collected): ${total_expected + total_arrears - total_collected}")
