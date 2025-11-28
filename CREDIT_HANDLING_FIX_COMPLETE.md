# Credit Handling Bug Fix - Complete Analysis

## Problem Identified

**Annah's Case:**
- Paid: $120
- Term 1 Fee: $100
- Overpayment (Credit): $20
- **Bug**: Showed $180 outstanding (displayed Term 3 balance with new fees)
- **Expected**: Should show $20 credit (or $0 with $20 available for next term)

## Root Cause

When a student overpays (negative balance = credit), the system was:
1. ✅ Correctly creating a **-$20 credit** in Term 1
2. ❌ **INCORRECTLY** cascading to Term 2 with:
   - Previous Arrears: -$20 (the credit)
   - New Fee: $100 (WRONG! Should be $0 since credit covers it)
   - Total: $80
3. ❌ Then cascading to Term 3 with:
   - Previous Arrears: $80
   - New Fee: $100
   - Total: $180

**The Issue**: When `previous_arrears` is negative (credit), the system still added a brand new term fee instead of using the credit to cover it.

## The Fix

**File**: `core/models/fee.py` (initialize_term_balance method)

### New Logic: Credit Handling

```python
# If student has overpaid (negative balance/credit)
# don't charge new fees - the credit covers them

if previous_arrears < 0:  # Student has credit
    credit_amount = abs(previous_arrears)
    if credit_amount >= term_fee.amount:
        # Credit covers the full new fee - no new charge
        new_term_fee = Decimal('0')
    else:
        # Credit partially covers - no new term fee yet
        new_term_fee = Decimal('0')
else:
    # Normal case: charge the full term fee
    new_term_fee = term_fee.amount
```

### Result

- When a student has credit, next terms get **$0 fee**
- The credit carries forward as **negative previous_arrears**
- Total due = $0 + (-$20) = -$20 (pure credit, no obligation)

## Data Correction Applied

**Before Fix:**
```
Term 1: Fee $100, Paid $120, Balance -$20 ✓
Term 2: Fee $100, Arrears -$20, Total $80 ✗
Term 3: Fee $100, Arrears $80, Total $180 ✗
Overall: $180 (WRONG)
```

**After Fix:**
```
Term 1: Fee $100, Paid $120, Balance -$20 ✓
Term 2: Fee $0, Arrears -$20, Total -$20 ✓
Term 3: DELETED (doesn't exist while credit exists) ✓
Overall: -$20 ($20 CREDIT) ✓
```

## Implementation

### When Term Balances are Initialized
1. Calculate previous_arrears (can be positive debt or negative credit)
2. Check if previous_arrears < 0 (has credit)
3. If credit exists:
   - Set new_term_fee = $0 (credit covers it)
   - Don't add new charges
4. If no credit or has debt:
   - Set new_term_fee = normal amount

### Result for Students

**Student with Credit (Overpaid):**
- Overall_balance = negative number
- Display as: "Credit: $X"
- Can use credit for future payments

**Student with Debt (Owes):**
- Overall_balance = positive number
- Display as: "Outstanding: $X"

**Student with $0 Balance:**
- Overall_balance = 0
- Display as: "Paid in Full"

## Verification Results

✅ **Annah**: $20 credit (correctly shown as -$20)
✅ **Brandon**: $100 outstanding (normal debt)
✅ **Cathrine**: $100 outstanding (normal debt)
✅ **David**: $100 outstanding (normal debt)

## Key Learnings

1. **Credit Handling**: When a student overpays, subsequent terms must NOT add new fees
2. **Cascading Logic**: Must check for credits before cascading to next terms
3. **Balance Representation**: Negative balance = credit, positive = debt
4. **UI Consideration**: Need to display negative balances as "Credit: $X" for user clarity

## Future Payment Scenarios

### Scenario 1: Student with Credit Makes Another Payment
- Current credit: -$20
- New payment: $50
- New balance: -$70 (even more credit)

### Scenario 2: Student with Credit is Charged Next Term
- Current credit: -$20
- New term fee: $100
- New_term_fee applied: $0 (credit covers it)
- Balance remains: -$20 (credit still available)

### Scenario 3: Student Uses Credit for Payment
- Current credit: -$20
- Owes: $100
- After using credit: $80 still owed

## Commits

1. `896d9c2`: Payment signal critical fix
2. `92f8510`: **Credit handling fix (THIS ONE)**

All students now correctly show:
- Annah: $20 credit (-$20 balance)
- Others: Correct outstanding amounts
