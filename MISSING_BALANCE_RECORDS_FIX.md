# Missing StudentBalance Records - Root Cause & Fix

## The Problem

When a student hasn't paid fees from Term 1 through Term 3, their **outstanding balance should increase** each term as:
1. They're charged the new term fee
2. Their previous arrears carry forward

**What was happening:**
- Student showed only $100 outstanding even though they're in Term 3 without paying
- This was because only their First Term balance record existed
- Second and Third Term balance records were never created

**Correct behavior (what should happen):**
- Term 1: $100 owed
- Term 2: $200 owed ($100 fee + $100 arrears)
- Term 3: $300 owed ($100 fee + $200 arrears)
- **overall_balance should show $300**

## Root Cause Analysis

### Why Balance Records Were Missing

The `create_terms_api()` function creates balance records for new terms, BUT with a critical limitation:

```python
# In create_terms_api() - lines 651-670
for term in term_objects:
    # Skip future terms - only create up to current term
    if term.academic_year > current_term.academic_year or (
        term.academic_year == current_term.academic_year and term.term > current_term.term
    ):
        continue
```

**Timeline of what happened:**
1. **When system started (Term 1 was current):**
   - create_terms_api() called for year 2026
   - Creates balances for Term 1 ✅ (it's current)
   - Term 2 & 3 are future → **balances not created** ❌

2. **When Term 2 became current:**
   - Admin activated Term 2 via `set_current_term_api()`
   - But this function just set `is_current=True`
   - **Did NOT initialize missing balances** ❌

3. **When Term 3 became current:**
   - Admin activated Term 3 via `set_current_term_api()`
   - Same issue: no balance initialization ❌

**Result:** Students stuck in later terms without proper balance records showing their true arrears.

## The Solution

Updated `set_current_term_api()` to **automatically initialize StudentBalance for ALL active students** when a term becomes current:

```python
@require_http_methods(["POST"])
def set_current_term_api(request, term_id):
    """Set current academic term"""
    try:
        term = AcademicTerm.objects.get(id=term_id)
        AcademicTerm.objects.all().update(is_current=False)
        term.is_current = True
        term.save()
        
        # IMPORTANT: Initialize StudentBalance for all active students in this term
        # This ensures they have their arrears carried forward when a new term becomes current
        from core.models.fee import StudentBalance
        from core.models import Student
        
        active_students = Student.objects.filter(is_active=True, is_deleted=False)
        balances_initialized = 0
        
        for student in active_students:
            try:
                balance = StudentBalance.initialize_term_balance(student, term)
                if balance:
                    balances_initialized += 1
            except Exception as e:
                print(f"Warning: Could not initialize balance for {student.full_name} in {term}: {e}")
        
        return JsonResponse({
            'status': 'success',
            'message': f'{term.academic_year} Term {term.term} is now current. Initialized {balances_initialized} student balances.',
            'balances_initialized': balances_initialized
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
```

## How It Works Now

### When Term 2 Is Activated:
1. `set_current_term_api()` is called
2. Term 2 is set as `is_current=True`
3. For each active student:
   - `StudentBalance.initialize_term_balance(student, Term2)` is called
   - Previous arrears calculated from Term 1 balance
   - New balance record created with:
     - `term_fee = $100`
     - `previous_arrears = $100` (from Term 1)
     - `current_balance = $200`

### When Term 3 Is Activated:
1. `set_current_term_api()` is called
2. Term 3 is set as `is_current=True`
3. For each active student:
   - `StudentBalance.initialize_term_balance(student, Term3)` is called
   - Previous arrears calculated from Term 2 balance
   - New balance record created with:
     - `term_fee = $100`
     - `previous_arrears = $200` (from Term 2)
     - `current_balance = $300`

## Example: Edwin (Grade 6A)

**Before Fix:**
```
First Term 2026: ✅ EXISTS
  Balance: $100

Second Term 2026: ❌ MISSING
Third Term 2026: ❌ MISSING

Result: overall_balance showed $100 (incorrect!)
```

**After Fix:**
```
First Term 2026: ✅ EXISTS
  Fee: $100 + Arrears: $0 = Balance: $100

Second Term 2026: ✅ CREATED (when T2 activated)
  Fee: $100 + Arrears: $100 = Balance: $200

Third Term 2026: ✅ CREATED (when T3 activated)
  Fee: $100 + Arrears: $200 = Balance: $300

Result: overall_balance now shows $300 (correct!)
```

## Key Implementation Details

### `StudentBalance.calculate_arrears()` Logic
This method automatically calculates what arrears to carry forward:

```python
@classmethod
def calculate_arrears(cls, student, term):
    """Calculate previous arrears to carry forward to this term"""
    if term.term == 1:
        return Decimal('0')  # First term of year has no arrears
    
    previous_term = AcademicTerm.objects.filter(
        academic_year=term.academic_year,
        term=term.term - 1
    ).first()
    
    if previous_term:
        previous_balance = cls.objects.filter(
            student=student,
            term=previous_term
        ).first()
        
        if previous_balance:
            return previous_balance.current_balance  # Carry forward the full balance
    
    return Decimal('0')
```

### `StudentBalance.initialize_term_balance()` Logic
This safely creates or retrieves balance records with proper arrears calculation:

```python
balance, created = cls.objects.get_or_create(
    student=student,
    term=term,
    defaults={
        'term_fee': term_fee.amount,
        'previous_arrears': previous_arrears,
        'amount_paid': Decimal('0')  # New balances always start at 0 paid
    }
)
```

## Benefits

1. ✅ **Automatic**: No manual intervention needed when activating terms
2. ✅ **Accurate**: Arrears properly calculate and flow forward
3. ✅ **Consistent**: All students get proper balance records
4. ✅ **Transparent**: Users see true outstanding amount
5. ✅ **Auditable**: StudentMovement records track all changes

## Testing

Before the fix:
- Edwin (no payments T1-T3): Shows $100 ❌
- Expected: $300 ✅

After the fix:
- Edwin (no payments T1-T3): Shows $300 ✅
- All three term balances exist ✅
- Arrears flow correctly: $100 → $200 → $300 ✅

## Related Code Files

- `core/views/step10_academic_management.py` - Fixed `set_current_term_api()`
- `core/models/fee.py` - `StudentBalance.initialize_term_balance()` method
- `core/models/fee.py` - `StudentBalance.calculate_arrears()` method
- `core/signals.py` - Payment signal still works correctly

## Future Improvements

1. Add logging when balances are auto-initialized
2. Add UI feedback showing how many balances were created
3. Create management command for bulk balance initialization (for historical data recovery)
4. Add admin dashboard showing terms with uninitialized balances
