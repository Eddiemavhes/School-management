# Step-by-Step Testing Guide - School Management System

This guide will walk you through testing all features of the school management system with a clean database.

## Part 1: Login & Setup (5 minutes)

### Step 1: Start the Server
1. Open PowerShell in your project directory
2. Run: `python manage.py runserver`
3. Open browser to: `http://localhost:8000`

### Step 2: Login with Admin Credentials
Use any of these admin emails (all set up with the system):
- **admin@admin.com** (recommended - simplest)
- ed@gmail.com
- edmavhe@hotmail.com
- Or any other email from the list shown after reset

Password: (Use your existing password - if unsure, you can set a new one)

Once logged in, you should see the **Dashboard** page.

---

## Part 2: Create Academic Structure (10 minutes)

### Step 3: Create Academic Years

1. **Navigate to Settings** → **Academic Years**
2. Click **"Add New Academic Year"** button
3. **Create Year 2026:**
   - Year: `2026`
   - Description: `Academic Year 2026`
   - Status: `Active`
   - Click **Save**

4. **Create Year 2027:**
   - Year: `2027`
   - Description: `Academic Year 2027`
   - Status: `Inactive`
   - Click **Save**

✅ **Verify:** You should see both years listed. 2026 should show as "Active", 2027 as "Inactive"

---

### Step 4: Create Academic Terms

1. **Navigate to Settings** → **Academic Terms**
2. Click **"Add New Term"** button
3. **Create Term 1 for 2026:**
   - Term Name: `First Term`
   - Academic Year: `2026`
   - Start Date: `2026-01-15`
   - End Date: `2026-04-10`
   - Click **Save**

4. **Create Term 2 for 2026:**
   - Term Name: `Second Term`
   - Academic Year: `2026`
   - Start Date: `2026-04-20`
   - End Date: `2026-08-15`
   - Click **Save**

5. **Create Term 3 for 2026:**
   - Term Name: `Third Term`
   - Academic Year: `2026`
   - Start Date: `2026-09-01`
   - End Date: `2026-11-30`
   - Click **Save**

✅ **Verify:** All three terms show under Academic Year 2026

---

### Step 5: Set Term Fees

1. **Navigate to Settings** → **Term Fees**
2. Click **"Set Term Fees"** button
3. **Set Fees for 2026:**
   - Academic Year: `2026`
   - First Term: `$1000`
   - Second Term: `$1000`
   - Third Term: `$1000`
   - Click **Save**

✅ **Verify:** Term fee amounts display for 2026

---

## Part 3: Create Classes (10 minutes)

### Step 6: Create Classes for 2026

1. **Navigate to Settings** → **Classes**
2. Click **"Add New Class"** button
3. **Create Class A (Form 1):**
   - Class Name: `Form 1A`
   - Academic Year: `2026`
   - Level: `Form 1`
   - Click **Save**

4. **Create Class B (Form 1):**
   - Class Name: `Form 1B`
   - Academic Year: `2026`
   - Level: `Form 1`
   - Click **Save**

5. **Create Class C (Form 2):**
   - Class Name: `Form 2A`
   - Academic Year: `2026`
   - Level: `Form 2`
   - Click **Save**

✅ **Verify:** All three classes appear in the classes list

---

## Part 4: Create and Enroll Students (15 minutes)

### Step 7: Create Students

1. **Navigate to Students** → **All Students**
2. Click **"Add Student"** button
3. **Create Student 1:**
   - First Name: `John`
   - Surname: `Doe`
   - Email: `john.doe@school.com`
   - Date of Birth: `2010-05-15`
   - Student ID: `S001`
   - Gender: `Male`
   - Class: `Form 1A`
   - Click **Save**

4. **Create Student 2:**
   - First Name: `Jane`
   - Surname: `Smith`
   - Email: `jane.smith@school.com`
   - Date of Birth: `2010-08-22`
   - Student ID: `S002`
   - Gender: `Female`
   - Class: `Form 1A`
   - Click **Save**

5. **Create Student 3:**
   - First Name: `Michael`
   - Surname: `Johnson`
   - Email: `michael.johnson@school.com`
   - Date of Birth: `2009-03-10`
   - Student ID: `S003`
   - Gender: `Male`
   - Class: `Form 2A`
   - Click **Save**

✅ **Verify:** Students appear in the student list

---

### Step 8: Verify Student Balances Display

1. **Go to Students** → **All Students**
2. **Look at the Balance column:**
   - John Doe: Should show **$1,000.00** (current term fee)
   - Jane Smith: Should show **$1,000.00** (current term fee)
   - Michael Johnson: Should show **$1,000.00** (current term fee)

✅ **Verify:** Balances display correctly (NOT $0.00) ✓ **THIS TESTS THE BALANCE DISPLAY FIX**

---

## Part 5: Record Payments (10 minutes)

### Step 9: Record Payments

1. **Navigate to Payments** → **Add Payment**
2. **Payment 1 - Partial Payment:**
   - Student: `John Doe`
   - Term: `First Term (2026)`
   - Amount: `$500`
   - Payment Method: `Bank Transfer`
   - Receipt/Reference: `BANK-001`
   - Click **Save**

3. **Payment 2 - Full Payment:**
   - Student: `Jane Smith`
   - Term: `First Term (2026)`
   - Amount: `$1000`
   - Payment Method: `Cash`
   - Receipt/Reference: `CASH-001`
   - Click **Save**

4. **Payment 3 - Another Payment:**
   - Student: `Michael Johnson`
   - Term: `First Term (2026)`
   - Amount: `$750`
   - Payment Method: `Cheque`
   - Receipt/Reference: `CHQ-001`
   - Click **Save**

✅ **Verify:** All payments are saved successfully

---

### Step 10: Verify Payment Form Dynamic Student Name Display

1. **Go to Payments** → **Add Payment**
2. **Test student name display:**
   - Click **Student dropdown**
   - Select **John Doe**
   - **VERIFY:** The text changes from "Select a student below" to **"John Doe"** ✓ **THIS TESTS THE PAYMENT FORM FIX**
   - **VERIFY:** The following details update automatically:
     - Term Fee: `$1,000.00`
     - Previous Arrears: `$0.00` (or correct amount)
     - Amount Paid: `$500.00` (he has paid $500)
     - Current Balance: `$500.00` (remaining to pay)

3. **Try another student:**
   - Select **Jane Smith**
   - **VERIFY:** Name updates to "Jane Smith"
   - **VERIFY:** Amount Paid shows `$1,000.00` (she paid full amount)
   - **VERIFY:** Current Balance shows `$0.00` (fully paid - will show in green)

---

### Step 11: Verify Payment Records Display Student Names

1. **Navigate to Payments** → **View Payments**
2. **Check the payment list:**
   - You should see entries like:
     - `John Doe | First Term | $500.00 | Bank Transfer | BANK-001`
     - `Jane Smith | First Term | $1,000.00 | Cash | CASH-001`
     - `Michael Johnson | First Term | $750.00 | Cheque | CHQ-001`

✅ **Verify:** Student names display in payment records (NOT class names) ✓ **THIS TESTS THE PAYMENT RECORDS FIX**

---

## Part 6: Verify Balance Updates After Payments (10 minutes)

### Step 12: Check Updated Student Balances

1. **Go to Students** → **All Students**
2. **Verify balances updated:**
   - **John Doe:** Should show **$500.00** (paid $500 of $1000)
   - **Jane Smith:** Should show **$0.00** (fully paid)
   - **Michael Johnson:** Should show **$250.00** (paid $750 of $1000)

✅ **Verify:** Balances accurately reflect payments

---

## Part 7: Test Year Rollover & Arrears Carryover (15 minutes)

### Step 13: Record More Payments in Different Terms

1. **Navigate to Payments** → **Add Payment**
2. **Payment for Second Term:**
   - Student: `John Doe`
   - Term: `Second Term (2026)`
   - Amount: `$800`
   - Payment Method: `Bank Transfer`
   - Receipt: `BANK-002`
   - Click **Save**

3. **Payment for Third Term:**
   - Student: `John Doe`
   - Term: `Third Term (2026)`
   - Amount: `$600`
   - Payment Method: `Bank Transfer`
   - Receipt: `BANK-003`
   - Click **Save**

---

### Step 14: Check Dashboard Statistics

1. **Go to Dashboard**
2. **Verify statistics section shows:**
   - Total Students: 3
   - Total Term Fees for current term: Should show correct amount
   - Amount Collected: Should show sum of all payments
   - Students with Arrears: Count of students who owe money

---

### Step 15: Create Terms for 2027 (for rollover testing)

1. **Navigate to Settings** → **Academic Terms**
2. **Create First Term for 2027:**
   - Term Name: `First Term`
   - Academic Year: `2027`
   - Start Date: `2027-01-15`
   - End Date: `2027-04-10`
   - Click **Save**

3. **Set Term Fees for 2027:**
   - Navigate to **Settings** → **Term Fees**
   - Academic Year: `2027`
   - First Term: `$1200` (increase the fee)
   - Click **Save**

---

### Step 16: Perform Year Rollover

1. **Navigate to Settings** → **Academic Years**
2. Find the **2026** year card
3. Click **"Rollover to New Year"** button
4. Select **2027** as target year
5. Click **Confirm Rollover**

**Wait for the operation to complete** - you should see a success message

---

### Step 17: Verify Arrears Carryover After Rollover

1. **Go to Payments** → **Add Payment**
2. **Test Student: John Doe**
   - Click **Student dropdown** and select **John Doe**
   - Look at the **"Previous Arrears"** field
   
   **John Doe should have:**
   - Term Fee: `$1,200` (new year's fee)
   - Previous Arrears: Should show the amount he owes from 2026
   - Amount Paid: Should show `$0` (no payments in 2027 yet)
   - Current Balance: Should be Total Due (fee + arrears)

✅ **Verify:** Unpaid balances from 2026 become "Previous Arrears" in 2027 ✓ **THIS TESTS THE ARREARS CARRYOVER FIX**

---

## Part 8: Dashboard Verification (5 minutes)

### Step 18: Final Dashboard Check

1. **Navigate to Dashboard**
2. **Verify the following sections:**
   - **Statistics Card:** Shows correct counts and totals
   - **Recent Payments:** Lists latest 5 payments with student names
   - **Students with Arrears:** Shows students who owe money with amounts
   - **Payment Status Distribution:** Shows pie chart of paid/partial/unpaid students

✅ **All sections should display accurately with student names and correct calculations**

---

## Summary: What Was Fixed & Tested

| Feature | Issue Before | Test Location | ✓ Status |
|---------|--------------|---------------|----------|
| **Student Balance Display** | Showed $0.00 instead of actual amount | Students → All Students | ✓ Part 4, Step 8 |
| **Payment Records Display** | Showed class names instead of student names | Payments → View Payments | ✓ Part 5, Step 11 |
| **Payment Form Student Name** | Didn't update when student selected | Payments → Add Payment | ✓ Part 5, Step 10 |
| **Arrears Carryover** | Unpaid balances not moving to next year | Rollover Test | ✓ Part 7, Step 17 |
| **Payment Form Details** | API endpoint missing/not working | Payments → Add Payment | ✓ Part 5, Step 10 |
| **Dashboard Statistics** | Incorrect calculations | Dashboard | ✓ Part 8, Step 18 |

---

## Troubleshooting

If you encounter issues:

### "Student balance shows $0.00"
- Ensure you're looking at the first term for the current academic year
- Check that term fees are set for that year

### "Payment form shows error when selecting student"
- Open browser console (F12) → Console tab
- Should see log messages showing API call
- Check that student exists and is in a valid class

### "Balance not updating after payment"
- Refresh the page
- Ensure payment was saved successfully (check Payments list)

### "Year rollover fails"
- Ensure target year (2027) exists with at least one term
- Ensure term fees are set for target year
- Check that source year (2026) has students

---

## Expected Data After Complete Testing

- **Students:** 3 (John Doe, Jane Smith, Michael Johnson)
- **Classes:** 3 (Form 1A, Form 1B, Form 2A)
- **Academic Years:** 2 (2026 with rollover, 2027 new)
- **Payments:** 4+ entries across multiple terms
- **Total Fees Collected:** Should match sum of individual payments

---

**🎉 If all tests pass, your school management system is working perfectly!**

For technical support, check console logs (F12) for detailed error messages.
