# Quick Test Guide - Payment System Fixes

## Test 1: Record David's Payment (Graduated Student)

1. **Navigate to:** Payments → Record Payment
2. **Select Student:** David (he's graduated but NOT archived)
3. **Enter Amount:** $100
4. **Check Result:**
   - ✅ Payment saves successfully  
   - ✅ Balance updates from $600 to $500
   - ✅ David appears in Payment History

## Test 2: Verify Balance Display

1. **Navigate to:** Students → David (Detail View)
2. **Check Outstanding Balance:** Should show **$600**
   - NOT $2100 (historical sum)
   - NOT $2700 (all terms sum)
3. **From API Test Script:**
   ```bash
   python diagnose_david_payment.py
   ```
   - Latest balance current_balance: **$600.00**

## Test 3: Test Overpayment Logic

1. **Navigate to:** Payments → Record Payment
2. **Select Student:** Any active student with $100 fee remaining
3. **Enter Amount:** $200 (overpayment)
4. **Check Result:**
   - ✅ Payment saves successfully
   - ✅ Current balance shows negative (overpaid)
   - ✅ Next term's "previous_arrears" shows as negative (credit)

## Test 4: Delete Payment & Verify Recalculation

1. **Navigate to:** Payments → Payment History
2. **Find a recent payment you created**
3. **Delete the payment**
4. **Verify:**
   - ✅ Balance is recalculated immediately
   - ✅ amount_paid removes the payment amount
   - ✅ No stale data remains

## Test 5: Run All Tests Programmatically

```bash
# Test David's payment system
python test_david_payment_creation.py

# Test payment deletion signal
python test_payment_delete_signal.py

# Test overpayment logic
python test_overpayment_logic.py

# Comprehensive test of all fixes
python comprehensive_payment_test.py
```

All should output: ✅ TEST PASSED

---

## Expected Behavior Summary

| Scenario | Before Fix | After Fix |
|----------|-----------|-----------|
| Graduated student tries to pay | ❌ Blocked | ✅ Allowed |
| David's balance displays | 2100 or wrong | ✅ **$600** |
| Overpayment ($200, $100 fee) | ❓ Unclear | ✅ $100 credit next term |
| Delete payment | Amount not updated | ✅ Recalculates correctly |

---

## Important Notes

1. **Graduated vs Archived:**
   - **Graduated** (not archived): Can still pay arrears ✅
   - **Archived** (graduated + all paid): Cannot pay ❌

2. **Balance Calculation:**
   - Always uses latest term's balance
   - Includes all arrears via `previous_arrears` field
   - No double-counting or summing

3. **Credits (Overpayments):**
   - Negative `previous_arrears` = student credit
   - Credit reduces next term's fee
   - Works across academic years

---

## Troubleshooting

**Q: David still can't make payments?**
- A: Check David's `is_archived` field - it must be False
- If False and is_active=False, he's a graduated student and SHOULD be able to pay

**Q: Balance shows wrong amount?**
- A: Check `student.overall_balance` property
- Run: `python diagnose_david_payment.py`
- Should show latest balance, not sum of all

**Q: Payment didn't record?**
- A: Check if payment.save() was called
- Check signal is firing (look for `update_student_balance_on_payment`)
- Verify `recorded_by` field is set

**Q: Overpayment credit not working?**
- A: Check next term's `previous_arrears` field
- Should be negative of the excess amount
- Run: `python test_overpayment_logic.py`
