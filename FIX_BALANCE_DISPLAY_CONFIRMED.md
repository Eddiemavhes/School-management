# BALANCE DISPLAY FIX - ANALYSIS & SOLUTION

## Issue Identified

The student card display was showing **incorrect balance figures**:

### What was displayed (WRONG):
- **John Done**: Outstanding $70.00, Arrears $0.00  
- **Jane Smith**: Outstanding $0.00, Arrears $0.00  
- **Michael Johnson**: Outstanding $45.00, Arrears $0.00  

### What should be displayed (CORRECT):
- **John Done**: Outstanding $0.00, Arrears $40.00  
- **Jane Smith**: Outstanding $0.00, Arrears $0.00  
- **Michael Johnson**: Outstanding $5.00, Arrears $20.00  

## Root Cause Analysis

The issue was in `core/models/student.py` in the `previous_term_arrears` property:

### OLD CODE (WRONG):
```python
@property
def previous_term_arrears(self):
    """Calculate arrears from previous term"""
    previous_payments = self.get_previous_term_payments()
    return max(0, self.previous_term_fee - previous_payments)
```

**Problem**: This was calculating arrears based on the `previous_term_fee` field from the Student model, which was outdated and not synchronized with the actual `StudentBalance` records that track per-term, per-student balances.

### NEW CODE (FIXED):
```python
@property
def previous_term_arrears(self):
    """Get current term's previous arrears from StudentBalance model"""
    from .fee import StudentBalance
    current_term = AcademicTerm.get_current_term()
    if not current_term:
        return 0
    
    balance = StudentBalance.objects.filter(
        student=self,
        term=current_term
    ).first()
    
    if balance:
        return balance.previous_arrears
    
    # Fallback to old calculation if no StudentBalance exists
    previous_payments = self.get_previous_term_payments()
    return max(0, self.previous_term_fee - previous_payments)
```

**Solution**: Now reads directly from the `StudentBalance` model's `previous_arrears` field for the current term, which is the source of truth for balance tracking.

## Database Verification

The `StudentBalance` records show the correct values:

```
Student: John Done (ID 6), Term: Third Term 2026
  Fee: 120.00, Paid: 160.00, Arrears: 40.00
  Outstanding = Fee + Arrears - Paid = 120 + 40 - 160 = $0.00 ✓

Student: Jane Smith (ID 7), Term: Third Term 2026  
  Fee: 120.00, Paid: 120.00, Arrears: 0.00
  Outstanding = Fee + Arrears - Paid = 120 + 0 - 120 = $0.00 ✓

Student: Michael Johnson (ID 8), Term: Third Term 2026
  Fee: 120.00, Paid: 135.00, Arrears: 20.00
  Outstanding = Fee + Arrears - Paid = 120 + 20 - 135 = $5.00 ✓
```

## Changes Made

**File**: `core/models/student.py`  
**Method**: `Student.previous_term_arrears` property  
**Action**: Updated to fetch from StudentBalance model instead of calculating from historical payments

## Verification

Test confirms the fix works correctly:
```
John Done: 
  From DB - Arrears: 40.00, Balance: 0.00
  From Property - Arrears: 40.00, Balance: 0.00 ✓

Jane Smith:
  From DB - Arrears: 0.00, Balance: 0.00
  From Property - Arrears: 0.00, Balance: 0.00 ✓

Michael Johnson:
  From DB - Arrears: 20.00, Balance: 5.00
  From Property - Arrears: 20.00, Balance: 5.00 ✓
```

## Next Steps

The page template will automatically display the correct values on next page refresh, as it uses `student.previous_term_arrears` and `student.current_term_balance` properties which now return correct values from the StudentBalance model.
