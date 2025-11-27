# PERMANENT FIX: Arrears Carryover System

## Problem
The system was incorrectly calculating arrears when creating new term balance records. This caused two issues:

1. **Manual calculations in multiple places**: Each place that created StudentBalance records (step10_academic_management.py, student_movement.py, academic_year.py) had its own custom logic for calculating previous_arrears. This was error-prone and inconsistent.

2. **Overwriting existing arrears**: When `initialize_term_balance()` was called on an existing balance, it would recalculate and overwrite the `previous_arrears` field. This could change the arrears multiple times.

3. **Ignoring credits**: The system didn't properly handle negative balances (credits from overpayment), which should carry forward as negative arrears to reduce the next term's dues.

## Solution

### 1. Unified Arrears Calculation
Created a single source of truth: `StudentBalance.calculate_arrears(student, term)`

This method:
- For Terms 2 & 3: Gets the previous term's `current_balance` 
- For Term 1: Gets the previous year's Term 3's `current_balance`
- Returns positive values for arrears (debt) and negative values for credits (overpayment)

### 2. Proper Initialization
`StudentBalance.initialize_term_balance(student, term)` now:
- **On creation**: Calculates arrears once and sets it in the defaults
- **On update**: Only updates `term_fee` if it changed, NEVER touches `previous_arrears`
- Uses `calculate_arrears()` consistently

This ensures arrears are set correctly once and remain stable.

### 3. Updated all Creation Points
Replaced manual balance creation in:
- `core/views/step10_academic_management.py` (lines 640-728)
- `core/views/student_movement.py` (lines 376-403)  
- `core/models/academic_year.py` (lines 300-308)

All now use `StudentBalance.initialize_term_balance()` instead of manual calculations.

## How It Works

**Example: Carol's Payment History**
```
2026 T1 (Fee $100):
  - Paid: $60
  - Arrears from prior: $0
  - Balance owed: $40 ✓

2026 T2 (Fee $100):
  - Paid: $120 
  - Arrears from T1: $40 (calculated as T1's balance)
  - Balance owed: $20 ✓

2026 T3 (Fee $100):
  - Paid: $110
  - Arrears from T2: $20 (calculated as T2's balance)
  - Balance owed: $10 ✓

2027 T1 (Fee $100):
  - Paid: $105
  - Arrears from T3 2026: $10 (calculated as T3's balance)
  - Balance owed: $5 ✓

2027 T2 (Fee $100):
  - Paid: $95
  - Arrears from T1: $5 (calculated as T1's balance)
  - Balance owed: $10 ✓

2027 T3 (CURRENT):
  - Fee: $100
  - Arrears from T2: $10 (calculated as T2's balance)
  - **DISPLAYS: $110** ✓
```

## Testing

Run `test_arrears_fix.py` to verify:
1. `calculate_arrears()` correctly gets previous term balances
2. `initialize_term_balance()` creates balances with correct arrears
3. Balances remain stable when called multiple times
4. Credits (negative balances) carry forward properly

## Going Forward

**For future term creation:**
Always use `StudentBalance.initialize_term_balance(student, term)` - never manually create StudentBalance records.

**The method handles:**
- ✅ Correct arrears calculation from previous terms
- ✅ Credits/overpayment carryover (negative arrears)
- ✅ Year-to-year transitions
- ✅ Graduated student handling
- ✅ Active/inactive student logic
- ✅ Stable balances (won't change on recalculation)

**This means the system will now automatically:**
- Carry forward student balances between terms
- Include credits from overpayments
- Calculate correct "amount owed" for dashboard display
- Never require manual fixes for arrears again
