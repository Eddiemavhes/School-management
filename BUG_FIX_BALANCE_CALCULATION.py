"""
CRITICAL BUG FIX: Balance Calculation Issue
============================================

ISSUE IDENTIFIED:
- API was returning total_outstanding: $1180.00 (WRONG)
- Should be: $1080.00 (CORRECT)
- Root cause: Including 2030 T1 balance ($100) which doesn't belong in current year outstanding

ANALYSIS:
- David Duck has StudentBalance records for 2026-2030
- Current term is: 2029 T3
- 2029 balances:
  - 2029 T1: $1080.00 outstanding ✓ SHOULD BE INCLUDED
  - 2029 T3: -$1080.00 (overpaid/credit, filtered out by > 0)
- 2030 balances:
  - 2030 T1: $100.00 ✗ SHOULD NOT BE INCLUDED (future year)

ROOT CAUSE:
The filter used `term__academic_year__gte=current_year` which means ">=2029"
This incorrectly included 2030 T1 in the calculation:
  $1080 (2029 T1) + $100 (2030 T1) = $1180 ❌ WRONG

THE FIX:
Changed filter from:
  StudentBalance.objects.filter(student=student, term__academic_year__gte=current_year)
To:
  StudentBalance.objects.filter(student=student, term__academic_year=current_year)

Result with fix:
  Only 2029 balances included
  $1080 (2029 T1) = $1080 ✓ CORRECT

AFFECTED FILES:
1. core/views/payment_views.py - Line 77
   Function: student_payment_details_api()
   
2. core/views/payment_views.py - Line 218
   Function: PaymentCreateView.get_context_data()

VERIFICATION:
Both API and view now return consistent total_outstanding values.
The 3-second auto-refresh JavaScript in payment_form.html will now display
the correct $1080.00 total outstanding (instead of $1180.00).

IMPACT:
- API endpoint: /api/student-balance/64/ returns correct value
- Payment recording form displays accurate outstanding balance
- All payment calculations now include ONLY current year debt
"""
print(__doc__)
