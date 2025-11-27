# FINAL CLARIFICATION: CAROL'S PAYMENT BREAKDOWN

## What Actually Happened

Carol has three term balances:

### Term 1 (2026):
- Term Fee: **$100**
- Previous Arrears: $0 (first term, no prior balance)
- **Carol Paid: $60** (two payments: $50 + $10)
- **Carol OWES: $40** (shortfall from Term 1)

### Term 2 (2026):
- Term Fee: **$100**
- Previous Arrears: **$40** (carried from Term 1 - Carol still owes this)
- **Total Due This Term: $140** ($100 fee + $40 owed from Term 1)
- **Carol Paid: $120**
  - First $40 of this payment goes toward the Term 1 arrears
  - Remaining $80 goes toward the Term 2 fee
  - **Still owes $20 on Term 2** ($100 - $80)

### Term 3 (2026):
- Term Fee: **$100**
- Previous Arrears: **$20** (Carol's outstanding from Term 2 carries forward)
- **Total Due This Term: $120** ($100 fee + $20 owed from Term 2)
- **Carol Paid: $0**
- **Carol OWES: $120**

## Total Outstanding Across All Terms: **$180**

Breakdown by term:
- Term 1: $40 (completely unpaid)
- Term 2: $20 (partially unpaid - she paid $80 of $100)
- Term 3: $120 (completely unpaid)

## What the System Display Shows

On the Payment History page, you see these SEPARATE term records, each showing:

**Term 1 2026:**
- Total Due: $100
- Amount Paid: $60
- Status: PARTIAL (red color - still owes)
- Outstanding: $40

**Term 2 2026:**
- Total Due: $140 (this includes the $40 from Term 1)
- Amount Paid: $120
- Status: PARTIAL (red color - still owes $20)
- Outstanding: $20

**Term 3 2026:**
- Total Due: $120 (this includes the $20 from Term 2)
- Amount Paid: $0
- Status: UNPAID (red color)
- Outstanding: $120

## The Fix Applied

**BEFORE** the fix:
- Term 1 showed `amount_paid = $100` (WRONG - it was actually $60)
- This made it appear Carol had fully paid Term 1
- Term 2's $120 payment was incorrectly crediting back to Term 1
- Term 3 had no previous arrears (WRONG - should carry $20 from Term 2)

**AFTER** the fix:
- Term 1 correctly shows `amount_paid = $60`
- Term 1 correctly shows `$40 owed`
- Term 2's $120 payment correctly applies as: $40 (arrears) + $80 (fee) = $100 of the $140 due
- Term 2 correctly shows `$20 still owed`
- Term 3 correctly carries `$20 previous_arrears`
- Term 3 correctly shows `$120 total owed` ($100 new + $20 carried)

## Why This Matters

The system now correctly tracks that Carol's payment history was:
1. Paid $60 in Term 1, owed $40
2. Paid $120 in Term 2 against a $140 total due ($100 + $40 arrears), still owes $20
3. Owes $120 in Term 3

If Carol pays $20 next, it will close out Term 2 and leave Term 3's outstanding as $120.
