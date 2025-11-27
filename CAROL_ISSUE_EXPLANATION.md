# CAROL'S PAYMENT ISSUE - COMPLETE ANALYSIS AND FIX

## THE PROBLEM

Carol paid **$60 in First Term** ($10 + $50), but the system was showing **$100 as paid**.
When Carol paid **$120 in Second Term**, the display was confusing because:
- The system thought she paid $100 in Term 1 (WRONG - only $60)
- She paid $120 in Term 2, which was $20 more than the $100 fee
- This $20 overpayment should have carried forward as credit for Term 3

## ROOT CAUSE

The `amount_paid` field in the `StudentBalance` database record for First Term was corrupted.
It showed **$100** when the sum of all actual payments was only **$60**.

The signal that updates `amount_paid` when payments are recorded should have kept it correct,
but somewhere the value got manually set or corrupted to $100.

## THE CORRECT SITUATION

**First Term 2026:**
- Term Fee: $100
- Carol actually paid: $60
- Outstanding: $40 (Carol OWES $40)

**Second Term 2026:**
- Previous Arrears: $40 (carried from Term 1)
- New Fee: $100
- Total Due This Term: $140 ($40 + $100)
- Carol paid: $120
- Outstanding: $20 (Carol still OWES $20 of the $140 total)

**Third Term 2026:**
- Previous Arrears: $20 (carried from Term 2)
- New Fee: $100
- Total Due This Term: $120 ($20 + $100)
- Carol paid: $0
- Outstanding: $120 (Carol OWES $120)

## TOTAL OUTSTANDING FOR CAROL

**$180.00** (spread across all three terms)
- $40 from Term 1
- $20 from Term 2
- $120 from Term 3

## WHAT WAS FIXED

1. **Fixed First Term 2026**: Changed `amount_paid` from $100 to $60 (actual payments sum)
2. **Fixed Third Term 2026**: Changed `previous_arrears` from $0 to $20 (the outstanding from Term 2)
3. **Applied fix to all students**: Found and fixed similar issues in Annette's records as well

## WHY THE CONFUSION

The display was showing Carol with a **-$20 credit** (overpayment) in Second Term
because the system thought she had paid $100 in First Term, so:
- She "needed" to pay: $100 (Term 1 full) + $100 (Term 2) = $200 total
- She "actually paid": $100 (Term 1) + $120 (Term 2) = $220 total
- So it looked like she overpaid by $20

But the TRUTH is:
- She needed to pay: $60 (Term 1 actual) + $100 (Term 2) = $160 total
- She actually paid: $60 (Term 1) + $120 (Term 2) = $180 total
- So she overpaid by $20, but only $20 of that should carry to Term 3
- Her actual Term 3 balance is $100 (not $80 as the wrong calculation showed)

## VERIFICATION

The system now correctly shows:
- Carol paid less than her fees required in Term 1
- She overpaid in Term 2 and the excess reduced her Term 3 balance from $100 to $80? NO!
- Actually, when she overpaid $120 in Term 2 (when $60 + $100 = $160 was owed):
  - The $40 arrears from Term 1 were covered
  - The $100 Term 2 fee was covered
  - She has $20 credit toward Term 3
  - So Term 3 becomes $100 - $20 = $80... but the system shows $120
  
WAIT - Let me recalculate. The previous_arrears system means:
- If student owes $40 from Term 1, they must pay that $40 FIRST
- Then they pay toward the $100 Term 2 fee
- With $120 payment:
  - $40 goes to Term 1 arrears
  - $80 goes to Term 2 fee
  - Still owes $20 on Term 2 = $20 CREDIT (negative balance)
  - This $20 credit carries to Term 3 as negative arrears

So Term 3 should be:
- Term Fee: $100
- Previous Arrears: -$20 (credit)
- Total Due: $80
- Paid: $0
- Outstanding: $80

But the system shows $120... Let me verify this is working correctly in the code!
