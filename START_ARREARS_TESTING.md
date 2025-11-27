# **NEXT STEPS - ARREARS-FIRST PAYMENT SYSTEM TESTING**

## **What's Been Implemented**

Your school management system now has a complete **Arrears-First Payment System** where:

✅ Students must pay arrears (past unpaid balances) BEFORE paying current term fees
✅ Payment form shows a clear priority message (RED for arrears, YELLOW for current, GREEN for paid)
✅ Arrears automatically calculate and carry forward to each new term
✅ Year rollover preserves all unpaid amounts as arrears for the new year

---

## **Quick Reference - What to Do**

### **Current Status**
- You have 3 students with payments in **Term 1**
- You're currently in **Term 1** of 2026
- You've already tested the balance display
- You've already recorded payments for Term 1

### **Next: MOVE TO TERM 2**

**Step 1: Run this command to set Term 2 as current:**

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
"
```

**Step 2: Run this command to initialize Term 2 balances:**

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

**Step 3: Test the payment form:**

1. Go to **Payments → Add Payment**
2. Select **John Done** from dropdown
3. **LOOK FOR:**
   - Red alert saying: "Must pay $70.00 in ARREARS first"
   - Previous Arrears: $70.00
   - Current Balance: $190.00

This means John must pay his $70 from Term 1 BEFORE paying the $120 current term fee.

**Step 4: Read the complete guide:**

Open `ARREARS_TESTING_GUIDE.md` in your editor for detailed step-by-step testing.

---

## **Complete Testing Flowchart**

```
Term 1 (2026) - ALREADY DONE ✓
  ├─ Set as current ✓
  ├─ Record payments ✓
  └─ Verify balances ✓

Term 2 (2026) - DO THIS NEXT
  ├─ Set as current (command above)
  ├─ Initialize balances (command above)
  ├─ TEST: Check payment priority (Step 3 above)
  ├─ Record payments (following arrears-first rule)
  └─ Verify balances updated correctly

Term 3 (2026) - THEN THIS
  ├─ Set as current (similar command)
  ├─ Initialize balances (similar command)
  ├─ TEST: Check payment priority
  ├─ Record payments (arrears-first)
  └─ Verify final balances

Year Rollover (2026 → 2027) - FINALLY THIS
  ├─ Create Term for 2027
  ├─ Set term fees for 2027
  ├─ Perform rollover operation
  ├─ Set 2027 Term 1 as current
  ├─ TEST: Verify arrears carried over
  │   ├─ John should show $120 arrears
  │   ├─ Michael should show $30 arrears  
  │   └─ Jane should show $0 arrears
  └─ DONE! System working perfectly ✓
```

---

## **What to Watch For - Key Tests**

### **TEST #1: Payment Priority Message**
When you select a student, the form should show:
- 🔴 **RED** if they have arrears to pay
- 🟡 **YELLOW** if arrears are cleared but current fee remains
- 🟢 **GREEN** if fully paid

### **TEST #2: Arrears Calculation**
After each term, the previous unpaid balance should appear as `previous_arrears` in the next term.

### **TEST #3: Year Rollover**
After rolling over to 2027, students should see their total 2026 arrears in the 2027 balance.

---

## **Quick Test Command**

To verify all balances at any time, run:

```powershell
cd "c:\Users\Admin\Desktop\School management"
python test_arrears.py
```

This shows:
- Each student's current balance
- How much they've paid
- How much they still owe
- What their payment priority is

---

## **Example Output**

When you run `test_arrears.py` for Term 2, you should see:

```
Student: John, Done
  Current Term: Second Term 2026
    - Term Fee: $120.00
    - Previous Arrears: $70.00 (from Term 1)
    - Amount Paid: $150.00 (paid $70 arrears + $80 fee)
    - Arrears Remaining: $0.00
    - Term Fee Remaining: $40.00
    - Current Balance: $40.00
    - Payment Priority: $40.00 remaining for current term fee
```

---

## **Need Help?**

**If payment priority doesn't show:**
- Make sure JavaScript is enabled in your browser
- Check browser console (F12) for errors
- Refresh the page

**If arrears calculations are wrong:**
- Run `test_arrears.py` to see actual values
- Check that StudentBalance records were created
- Verify payments were recorded correctly

**If terms don't update:**
- Verify you ran the commands to set current term
- Check that the term year/number is correct

---

## **Final Summary**

You now have:
✅ Proper arrears tracking  
✅ Clear payment guidance for students  
✅ Automatic arrears carryover  
✅ Visual feedback in payment form  
✅ Complete payment history tracking  

**Start with Term 2 testing and work through the guide. Let me know if you hit any issues!**
