# Grade 7 Auto-Graduation System - Complete Documentation

## Core Requirement
"IF A STUDENT HAS FINISHED GRADE 7 THE STUDENT SHOULD BE PUT IN ALUMNI"

## Grade 7 Student Lifecycle

### Scenario 1: Grade 7 Student PAYS and Clears Arrears
**Flow:**
- Student is Grade 7, enrolled (is_active=True)
- Student has outstanding balance (e.g., $600 from previous terms)
- Payment received → `payment_signal` triggered
- Signal calls `student.auto_graduate_if_eligible()`
- Check: Grade 7 + ENROLLED + current_balance == 0
- **Result:** Auto-graduated to Alumni
  - is_active → False
  - is_archived → True
  - StudentMovement created with reason "Auto-graduated"
- Next term: No new fees (is_active=False check prevents it)

### Scenario 2: Grade 7 Student DOESN'T PAY in Same Year
**Flow:**
- Student is Grade 7, enrolled (is_active=True)
- Student still owes from current year (e.g., $300)
- Term 2 comes → New balance created
  - Arrears carry forward ($300)
  - New fee added ($100)
  - Total: $400
- **Result:** Student stays Grade 7, accumulates fees within same year

### Scenario 3: Grade 7 Student Doesn't Pay - ENTERS NEW ACADEMIC YEAR
**Flow:**
- Student is Grade 7 in 2027, hasn't paid
- Final 2027 balance: $600 (arrears)
- 2028 Term 1 becomes current
- New balance would be created, but...
- **Grade 7 New Year Check:**
  - Is this Term 1 of new academic year? ✓
  - Is student Grade 7+? ✓
  - Does student have outstanding balance from previous year? ✓
  - **Action:** DON'T add new fee, only carry forward arrears
  - 2028 T1 balance: Fee=$0, Arrears=$600, Total=$600
- **Result:** Student stays Grade 7 with only arrears, no accumulation

## Implementation Details

### Auto-Graduation Trigger
**File:** `core/signals.py` (Payment post_save handler)
```python
# After payment processed and amount_paid updated:
student.refresh_from_db()
if student.auto_graduate_if_eligible():
    # StudentMovement created, is_active set to False
```

### Grade 7 New Year Logic
**File:** `core/models/fee.py` (initialize_term_balance method)
```python
if term.term == 1 and student.current_class:  # New academic year
    if int(student.current_class.grade) >= 7:  # Grade 7 or higher
        # Check previous year's last balance
        if previous_year_last_balance and previous_year_last_balance.current_balance > 0:
            # NO new fee, only arrears
            term_fee = Decimal('0')  # $0
            previous_arrears = previous_year_last_balance.current_balance
```

### Auto-Initialization on Term Activation
**File:** `core/signals.py` (AcademicTerm post_save handler)
```python
# When is_current=True:
for student in active_students:
    StudentBalance.initialize_term_balance(student, term)
    # This applies all logic including Grade 7 new year check
```

## Test Cases

### Test 1: Edwin Grade 7A Scenario (User's Case)
- **2027 T1:** Fee $100, Arrears $300 → Total $400
- **2027 T2:** Fee $100, Arrears $400 → Total $500  
- **2027 T3:** Fee $100, Arrears $500 → Total $600
- **2028 T1:** Fee $0, Arrears $600 → Total $600 ✓ (NO $700)

### Test 2: Grade 7 with Zero Balance
- Grade 7 student has $0 balance at end of term
- Payment triggers auto-graduation
- Next year: NO balance created (is_active=False)

### Test 3: Grade 7 Pays Partial Arrears
- Grade 7 student owes $600
- Pays $200 → Balance now $400
- Doesn't reach $0 → No auto-graduation yet
- Next year: $0 fee + $400 arrears = $400

## Key Distinctions

| Scenario | Grade 7 in Same Year | Grade 7 in New Year | Result |
|----------|---------------------|-------------------|--------|
| Has arrears, no payment | Accumulate fees | NO new fees | Stays Grade 7 |
| Clears balance ($0) | N/A | Auto-graduate to Alumni | No 2028 fees |
| Partially pays | New fees added | NO new fees | Stays Grade 7, lower balance |

## Prevention of Issues

### Signal for Term Activation
Auto-initializes all student balances when term becomes current, applying Grade 7 logic automatically.

### Grade 7 Check in Same Academic Year
Within a year, Grade 7 students get normal fees if they have arrears (allows them to clear it).

### Grade 7 Check for New Academic Year
When entering new year, Grade 7 students with outstanding balance DON'T get new fees to prevent unlimited accumulation.

## Edge Cases Handled

1. ✓ Grade 7 student with $0 balance → Auto-graduates
2. ✓ Grade 7 student with arrears in same year → Gets new fees (can clear)
3. ✓ Grade 7 student with arrears entering new year → NO new fees (only arrears)
4. ✓ Grade 6 moving to Grade 7 → Treated as Grade 7 from that term onward
5. ✓ Graduated student (is_active=False) → No new balances created

## Current Status
- Edwin Grade 7A: $600 outstanding (2027 arrears, NO 2028 fee) ✓
- Auto-graduation working: Grade 7 → Alumni when balance = $0 ✓
- New year Grade 7 protection: Active ✓
