# **UPDATED TESTING GUIDE - ARREARS-FIRST PAYMENT SYSTEM**

This guide tests the complete payment system with proper arrears handling across multiple terms.

---

## **QUICK SETUP (What's Already Done)**

✅ Database cleaned and reset  
✅ 3 Students created (Jane Smith, John Done, Michael Johnson)  
✅ 3 Classes created (Grade 1A, Grade 1A, Grade 2A)  
✅ Academic Years created (2026, 2027)  
✅ Terms created for 2026 (First, Second, Third)  
✅ Term Fees set ($120 per term)  
✅ StudentBalance records initialized  
✅ Payments recorded for Term 1  
✅ **NEW: Payment priority system implemented** (Arrears MUST be paid before current term fees)

---

## **CURRENT STATUS - Term 1 (2026)**

Current balances after Term 1 payments:
- **Jane Smith:** $0.00 (Paid $120 in full)
- **John Done:** $70.00 (Paid $50, owes $70 for Term 1)
- **Michael Johnson:** $45.00 (Paid $75, owes $45 for Term 1)

---

## **NOW: MOVE TO TERM 2 (2026)**

### **Step 1: Set Term 2 as Current Term**

Run this command in PowerShell:

```powershell
cd "c:\Users\Admin\Desktop\School management"
python manage.py shell -c "
from core.models.academic import AcademicTerm
term = AcademicTerm.objects.filter(academic_year=2026, term=2).first()
if term:
    AcademicTerm.objects.all().update(is_current=False)
    term.is_current = True
    term.save()
    print(f'✓ Current term set to: {term}')
else:
    print('ERROR: 2026 Second Term not found')
"
```

You should see: `✓ Current term set to: Second Term 2026`

---

### **Step 2: Initialize Term 2 StudentBalance Records**

Run this command:

```powershell
cd "c:\Users\Admin\Desktop\School management"
python manage.py shell -c "
from core.models import Student
from core.models.academic import AcademicTerm
from core.models.fee import StudentBalance

term = AcademicTerm.objects.filter(academic_year=2026, term=2).first()
students = Student.objects.filter(is_active=True)

for student in students:
    StudentBalance.initialize_term_balance(student, term)

print(f'✓ Initialized {students.count()} balances for Term 2')
"
```

You should see: `✓ Initialized 3 balances for Term 2`

---

### **Step 3: ✅ TEST - Check Payment Form Shows Payment Priority**

1. Go to **Payments → Add Payment**
2. Click **Student dropdown** and select **John Done**

**YOU SHOULD NOW SEE:**
- **Student Name:** John Done
- **Payment Priority Alert (RED):** "Must pay $70.00 in ARREARS first"
- **Current Term Fee:** $120.00
- **Previous Arrears:** $70.00 (from Term 1 unpaid balance)
- **Amount Paid:** $0.00 (hasn't paid in Term 2 yet)
- **Current Balance:** $190.00 ($120 + $70 arrears)

**MEANING:** John MUST pay the $70 he owes from Term 1 BEFORE paying for Term 2's $120 fee.

3. Try **Jane Smith:**

**YOU SHOULD SEE:**
- **Payment Priority Alert (GREEN):** "Fully paid up"
- **Previous Arrears:** $0.00 (she paid everything in Term 1)
- **Current Balance:** $120.00 (only the new term fee)

4. Try **Michael Johnson:**

**YOU SHOULD SEE:**
- **Payment Priority Alert (RED):** "Must pay $45.00 in ARREARS first"
- **Previous Arrears:** $45.00 (what he owes from Term 1)
- **Current Balance:** $165.00 ($120 + $45)

**✅ TEST PASSED IF:** Payment priority messages show correctly with correct amounts

---

### **Step 4: Record Payments for Term 2**

**NOTE:** Students with arrears must pay those FIRST. Let's follow the rule:

1. **John Done's Payment (Pay Arrears First):**
   - Go to **Payments → Add Payment**
   - Student: `John Done`
   - Term: `Second Term (2026)`
   - Amount: `70` ← Pay his $70 arrears first!
   - Payment Method: `Bank Transfer`
   - Receipt: `TERM2-JOHN-ARREARS`
   - Click **Save**

2. **Michael Johnson's Payment (Pay Arrears First):**
   - Go to **Add Payment** again
   - Student: `Michael Johnson`
   - Term: `Second Term (2026)`
   - Amount: `45` ← Pay his $45 arrears first!
   - Payment Method: `Cash`
   - Receipt: `TERM2-MICHAEL-ARREARS`
   - Click **Save**

3. **Jane Smith's Payment (Pay Current Term):**
   - Go to **Add Payment** again
   - Student: `Jane Smith`
   - Term: `Second Term (2026)`
   - Amount: `120` ← Pay the full current term fee
   - Payment Method: `Check`
   - Receipt: `TERM2-JANE-FEE`
   - Click **Save**

4. **John Done's 2nd Payment (Now Pay Current Term):**
   - Go to **Add Payment** again
   - Student: `John Done`
   - Term: `Second Term (2026)`
   - Amount: `80` ← Now pay part of the current term fee
   - Payment Method: `Bank Transfer`
   - Receipt: `TERM2-JOHN-FEE`
   - Click **Save**

5. **Michael Johnson's 2nd Payment (Now Pay Current Term):**
   - Go to **Add Payment** again
   - Student: `Michael Johnson`
   - Term: `Second Term (2026)`
   - Amount: `100` ← Pay part of the current term fee
   - Payment Method: `Cash`
   - Receipt: `TERM2-MICHAEL-FEE`
   - Click **Save**

---

### **Step 5: ✅ TEST - Verify Term 2 Balances Updated Correctly**

Run this command:

```powershell
cd "c:\Users\Admin\Desktop\School management"
python test_arrears.py
```

**YOU SHOULD SEE FOR TERM 2 (Second Term 2026):**

**Jane Smith:**
- Term Fee: $120.00
- Amount Paid: $120.00
- Current Balance: $0.00
- Status: ✓ PAID

**John Done:**
- Previous Arrears: $70.00
- Term Fee: $120.00
- Amount Paid: $150.00 ($70 arrears + $80 for current fee)
- Current Balance: $40.00 (still owes $40 of the current term fee)

**Michael Johnson:**
- Previous Arrears: $45.00
- Term Fee: $120.00
- Amount Paid: $145.00 ($45 arrears + $100 for current fee)
- Current Balance: $20.00 (still owes $20 of the current term fee)

**✅ TEST PASSED IF:** Balances show correctly with arrears paid first

---

## **NOW: MOVE TO TERM 3 (2026)**

### **Step 6: Set Term 3 as Current Term**

```powershell
cd "c:\Users\Admin\Desktop\School management"
python manage.py shell -c "
from core.models.academic import AcademicTerm
term = AcademicTerm.objects.filter(academic_year=2026, term=3).first()
if term:
    AcademicTerm.objects.all().update(is_current=False)
    term.is_current = True
    term.save()
    print(f'✓ Current term set to: {term}')
else:
    print('ERROR: 2026 Third Term not found')
"
```

---

### **Step 7: Initialize Term 3 StudentBalance Records**

```powershell
cd "c:\Users\Admin\Desktop\School management"
python manage.py shell -c "
from core.models import Student
from core.models.academic import AcademicTerm
from core.models.fee import StudentBalance

term = AcademicTerm.objects.filter(academic_year=2026, term=3).first()
students = Student.objects.filter(is_active=True)

for student in students:
    StudentBalance.initialize_term_balance(student, term)

print(f'✓ Initialized {students.count()} balances for Term 3')
"
```

---

### **Step 8: ✅ TEST - Verify Term 3 Payment Priority**

Go to **Payments → Add Payment** and select each student:

**Jane Smith:**
- Payment Priority: "Fully paid up" (GREEN)
- Previous Arrears: $0.00
- Current Balance: $120.00 (just the new fee)

**John Done:**
- Payment Priority: "Must pay $40.00 in ARREARS first" (RED)
- Previous Arrears: $40.00 (from Term 2)
- Current Balance: $160.00 ($120 new fee + $40 arrears)

**Michael Johnson:**
- Payment Priority: "Must pay $20.00 in ARREARS first" (RED)
- Previous Arrears: $20.00 (from Term 2)
- Current Balance: $140.00 ($120 new fee + $20 arrears)

**✅ TEST PASSED IF:** Arrears from Term 2 correctly shown as Priority in Term 3

---

### **Step 9: Record Payments for Term 3**

1. **John Done (Pay Arrears First):**
   - Amount: `40` (his Term 2 arrears)
   - Receipt: `TERM3-JOHN-ARREARS`

2. **Michael Johnson (Pay Arrears First):**
   - Amount: `20` (his Term 2 arrears)
   - Receipt: `TERM3-MICHAEL-ARREARS`

3. **Jane Smith (Pay Current):**
   - Amount: `120`
   - Receipt: `TERM3-JANE-FEE`

4. **John Done (Pay Current):**
   - Amount: `60`
   - Receipt: `TERM3-JOHN-FEE`

5. **Michael Johnson (Pay Current):**
   - Amount: `90`
   - Receipt: `TERM3-MICHAEL-FEE`

---

### **Step 10: Verify Final Term 3 Balances**

Run:
```powershell
python test_arrears.py
```

**Final Status (All Terms Complete for 2026):**

**John Done - Total for 2026:**
- Term 1: Paid $50, Owed $70
- Term 2: Paid $150, Owed $40
- Term 3: Paid $100, Owed $60
- **Total Paid:** $300 of $360
- **Total Owes:** $120

**Jane Smith - Total for 2026:**
- Term 1: Paid $120, Owed $0
- Term 2: Paid $120, Owed $0
- Term 3: Paid $120, Owed $0
- **Total Paid:** $360 of $360
- **Total Owes:** $0 ✓

**Michael Johnson - Total for 2026:**
- Term 1: Paid $75, Owed $45
- Term 2: Paid $145, Owed $20
- Term 3: Paid $110, Owed $10
- **Total Paid:** $330 of $360
- **Total Owes:** $30

---

## **FINAL TEST: YEAR ROLLOVER TO 2027**

### **Step 11: Create Term for 2027**

1. Go to **Settings → Academic Terms**
2. Click **Add Term**
3. Fill:
   - Term Name: `First Term`
   - Academic Year: `2027`
   - Start Date: `2027-01-15`
   - End Date: `2027-04-10`
4. Click **Save**

---

### **Step 12: Set Term Fees for 2027**

1. Go to **Settings → Term Fees**
2. Click **Set Term Fees**
3. Fill:
   - Academic Year: `2027`
   - First Term Fee: `150` (increase from $120)
4. Click **Save**

---

### **Step 13: Perform Year Rollover**

1. Go to **Settings → Academic Years**
2. Find 2026 year card
3. Click **Rollover to New Year** button
4. Select 2027 as target
5. Click **Confirm**

**Wait for success message**

---

### **Step 14: Set 2027 Term 1 as Current**

```powershell
cd "c:\Users\Admin\Desktop\School management"
python manage.py shell -c "
from core.models.academic import AcademicTerm
term = AcademicTerm.objects.filter(academic_year=2027, term=1).first()
if term:
    AcademicTerm.objects.all().update(is_current=False)
    term.is_current = True
    term.save()
    print(f'✓ Current term set to: {term}')
else:
    print('ERROR: 2027 First Term not found')
"
```

---

### **Step 15: ✅ FINAL TEST - Verify Arrears Carried Over**

Go to **Payments → Add Payment** and select each student:

**Jane Smith (2027 Term 1):**
- Payment Priority: "Fully paid up" (GREEN)
- Term Fee: $150.00
- Previous Arrears: $0.00
- Current Balance: $150.00

**John Done (2027 Term 1):**
- Payment Priority: "Must pay $120.00 in ARREARS first" (RED)
- Term Fee: $150.00
- Previous Arrears: $120.00 (what he owes from 2026)
- Current Balance: $270.00 ($150 + $120)

**Michael Johnson (2027 Term 1):**
- Payment Priority: "Must pay $30.00 in ARREARS first" (RED)
- Term Fee: $150.00
- Previous Arrears: $30.00 (what he owes from 2026)
- Current Balance: $180.00 ($150 + $30)

**✅ CRITICAL TEST PASSED IF:**
- ✅ John Done shows $120 in Previous Arrears (from all 3 terms of 2026)
- ✅ Michael Johnson shows $30 in Previous Arrears (from 2026)
- ✅ Jane Smith shows $0 in Previous Arrears (paid everything)
- ✅ Payment Priority messages are correct and color-coded

---

## **SUMMARY - All Tests Completed**

If you can see:
1. ✅ Payment priority messages showing correctly across all terms
2. ✅ Arrears paid first before current term fees
3. ✅ Correct arrears amounts carried over to next year
4. ✅ All balances calculating correctly

**Then your school management system is working perfectly with the complete arrears-first payment system!**
