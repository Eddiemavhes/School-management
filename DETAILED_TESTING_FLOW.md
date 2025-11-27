# COMPLETE SYSTEM FLOW - DETAILED STEP BY STEP GUIDE

## PREPARATION
**System Status**: Clean database with only admin login credentials
- Teachers: DELETED ✓
- Students: DELETED ✓
- Classes: DELETED ✓
- Academic Years: DELETED ✓
- Terms: DELETED ✓
- Payments: DELETED ✓

**Admin Account**: Your login credentials are preserved
- Use your existing admin email and password to login

---

## SECTION 1: LOGIN & AUTHENTICATION
### Step 1.1: Access Login Page
1. Open browser and go to: `http://127.0.0.1:8000/login/`
2. **Expected Screen**: Login form with:
   - Email field
   - Password field
   - Login button
   - Links to admin dashboard (if already logged in)

### Step 1.2: Login with Admin Credentials
1. Enter your admin email
2. Enter your admin password
3. Click "Login" button
4. **Expected Result**: 
   - Redirected to `/dashboard/`
   - See greeting: "Welcome, [Your Name]"
   - Main navigation menu visible at top

### Step 1.3: Verify Dashboard Access
1. Should see dashboard with:
   - Quick stats (if any data exists)
   - Menu options for:
     - Academic Management
     - Classes
     - Teachers
     - Students
     - Payments & Fees
     - Settings
   - Your profile in top right corner

---

## SECTION 2: ACADEMIC YEAR SETUP (MANDATORY FIRST)
### Step 2.1: Navigate to Academic Year Management
1. Click "Settings" in main menu or dashboard
2. Look for "Academic Year Management" or "Academic Years"
3. Click "Academic Years" or similar option
4. **Expected Screen**: List of academic years (should be empty)

### Step 2.2: Create First Academic Year (2026)
1. Click "Create Academic Year" button
2. **Form Fields to Fill**:
   ```
   Year: 2026
   Description: Academic Year 2026
   Start Date: 01/01/2026 (MM/DD/YYYY format)
   End Date: 12/31/2026 (MM/DD/YYYY format)
   ```
3. Click "Save" or "Create" button
4. **Expected Result**:
   - Success message appears
   - Year "2026" appears in list
   - Status shows: "Not Active" or similar

### Step 2.3: Activate Academic Year 2026
1. In the academic years list, find 2026
2. Click "Set as Active" or similar button next to 2026
3. **Expected Result**:
   - Status changes to "Active"
   - Only one year can be active
   - System now uses 2026 for all operations

---

## SECTION 3: ACADEMIC TERMS SETUP (REQUIRES ACTIVE YEAR)
### Step 3.1: Navigate to Terms Management
1. Click "Settings" in main menu
2. Find "Academic Terms" or "Term Management"
3. Click to access terms list
4. **Expected Screen**: List of terms (should be empty or show from previous year)

### Step 3.2: Create First Term - "First Term 2026"
1. Click "Create Term" button
2. **Form Fields**:
   ```
   Academic Year: 2026 (dropdown - select the year you activated)
   Term Name: First Term 2026
   Term Number: 1 (or "First")
   Start Date: 01/15/2026
   End Date: 04/15/2026
   Default Fee: 120.00
   Is Current: [CHECK THIS BOX] ✓
   ```
3. Click "Save" or "Create"
4. **Expected Result**:
   - Term created successfully
   - First Term 2026 shows in list
   - Shows as "Current Term"

### Step 3.3: Create Second Term - "Second Term 2026"
1. Click "Create Term" again
2. **Form Fields**:
   ```
   Academic Year: 2026
   Term Name: Second Term 2026
   Term Number: 2 (or "Second")
   Start Date: 05/01/2026
   End Date: 08/15/2026
   Default Fee: 120.00
   Is Current: [DO NOT CHECK] ☐
   ```
3. Click "Save"
4. **Expected Result**: Second term created, not marked as current

### Step 3.4: Create Third Term - "Third Term 2026"
1. Click "Create Term" again
2. **Form Fields**:
   ```
   Academic Year: 2026
   Term Name: Third Term 2026
   Term Number: 3 (or "Third")
   Start Date: 09/01/2026
   End Date: 12/15/2026
   Default Fee: 120.00
   Is Current: [DO NOT CHECK] ☐
   ```
3. Click "Save"
4. **Expected Result**: 
   - All three terms now visible in list
   - First Term 2026 marked as current/active
   - Summary shows: "First Term 2026" as active term

---

## SECTION 4: CLASSES CREATION
### Step 4.1: Navigate to Classes Management
1. Click "Classes" in main navigation menu
2. **Expected Screen**: 
   - Classes list (empty initially)
   - "Create Class" button at top

### Step 4.2: Create Class 1 - Grade 1, Section A
1. Click "Create Class" button
2. **Form Fields**:
   ```
   Grade: 1 (from dropdown)
   Section: A (from dropdown)
   Academic Year: 2026 (auto-filled from active year)
   Teacher: [Leave BLANK for now]
   ```
3. Click "Create Class" button
4. **Expected Result**:
   - Success message: "Class 1A created successfully"
   - Returns to classes list
   - "Grade 1A (2026)" appears in list

### Step 4.3: Create Class 2 - Grade 1, Section B
1. Click "Create Class" button
2. **Form Fields**:
   ```
   Grade: 1
   Section: B
   Academic Year: 2026
   Teacher: [Leave BLANK]
   ```
3. Click "Create Class"
4. **Expected Result**: "Grade 1B (2026)" appears in list

### Step 4.4: Create Class 3 - Grade 2, Section A
1. Click "Create Class"
2. **Form Fields**:
   ```
   Grade: 2
   Section: A
   Academic Year: 2026
   Teacher: [Leave BLANK]
   ```
3. Click "Create Class"

### Step 4.5: Create Class 4 - Grade 2, Section B
1. Click "Create Class"
2. **Form Fields**:
   ```
   Grade: 2
   Section: B
   Academic Year: 2026
   Teacher: [Leave BLANK]
   ```
3. Click "Create Class"

### Step 4.6: Create Class 5 - Grade 3, Section A
1. Click "Create Class"
2. **Form Fields**:
   ```
   Grade: 3
   Section: A
   Academic Year: 2026
   Teacher: [Leave BLANK]
   ```
3. Click "Create Class"

### Step 4.7: Verify All Classes Created
1. On Classes page, you should see:
   ```
   Grade 1A (2026) - No Teacher
   Grade 1B (2026) - No Teacher
   Grade 2A (2026) - No Teacher
   Grade 2B (2026) - No Teacher
   Grade 3A (2026) - No Teacher
   ```
2. Each class should show count of students (0 for new classes)

---

## SECTION 5: TEACHERS CREATION & ASSIGNMENT
### Step 5.1: Navigate to Teachers Management
1. Click "Teachers" in main navigation menu
2. **Expected Screen**:
   - Teachers list (empty after deletion)
   - "Create Teacher" button at top

### Step 5.2: Create Teacher 1 - John Smith
1. Click "Create Teacher" button
2. **Form Fields** (ALL REQUIRED unless marked optional):
   ```
   First Name: John
   Last Name: Smith
   Email: john.smith@school.com
   Password: Teacher@123 (or secure password)
   Phone: 1234567890
   Specialization: Mathematics
   Qualification: B.Ed
   Joining Date: 01/15/2026
   Teacher ID: T001
   Bio: (Optional) Mathematics teacher with 5 years experience
   ```
3. Click "Save" or "Create Teacher"
4. **Expected Result**:
   - Success message
   - Redirects to teacher detail page
   - Shows "John Smith" with all details
   - Shows "No class assigned" or similar
   - Has "Assign Class" button

### Step 5.3: Assign John Smith to Grade 1A
1. On John Smith's detail page, click "Assign Class" button
2. **Form Fields**:
   ```
   Class: Grade 1A (2026) (from dropdown)
   Academic Year: 2026 (should be auto-filled)
   ```
3. Click "Assign" or "Save"
4. **Expected Result**:
   - Success message
   - Shows "Assigned to Grade 1A (2026)"
   - Returns to teacher list showing assignment

### Step 5.4: Create Teacher 2 - Jane Wilson
1. Go to Teachers page, click "Create Teacher"
2. **Form Fields**:
   ```
   First Name: Jane
   Last Name: Wilson
   Email: jane.wilson@school.com
   Password: Teacher@123
   Phone: 1234567891
   Specialization: English
   Qualification: M.A
   Joining Date: 01/15/2026
   Teacher ID: T002
   ```
3. Click "Save Teacher"
4. On detail page, click "Assign Class"
5. Select "Grade 1B (2026)"
6. Click "Assign"

### Step 5.5: Create Teacher 3 - Michael Brown
1. Go to Teachers, click "Create Teacher"
2. **Form Fields**:
   ```
   First Name: Michael
   Last Name: Brown
   Email: michael.brown@school.com
   Password: Teacher@123
   Phone: 1234567892
   Specialization: Science
   Qualification: B.Sc
   Joining Date: 01/15/2026
   Teacher ID: T003
   ```
3. Save and assign to "Grade 2A (2026)"

### Step 5.6: Create Teacher 4 - Sarah Davis
1. Go to Teachers, click "Create Teacher"
2. **Form Fields**:
   ```
   First Name: Sarah
   Last Name: Davis
   Email: sarah.davis@school.com
   Password: Teacher@123
   Phone: 1234567893
   Specialization: History
   Qualification: B.A
   Joining Date: 01/15/2026
   Teacher ID: T004
   ```
3. Save and assign to "Grade 2B (2026)"

### Step 5.7: Create Teacher 5 - Robert Taylor
1. Go to Teachers, click "Create Teacher"
2. **Form Fields**:
   ```
   First Name: Robert
   Last Name: Taylor
   Email: robert.taylor@school.com
   Password: Teacher@123
   Phone: 1234567894
   Specialization: Physical Education
   Qualification: B.Ed
   Joining Date: 01/15/2026
   Teacher ID: T005
   ```
3. Save and assign to "Grade 3A (2026)"

### Step 5.8: Verify All Teachers Assigned
1. Go to Teachers page
2. You should see all 5 teachers with their assignments:
   ```
   John Smith - Assigned to Grade 1A (2026)
   Jane Wilson - Assigned to Grade 1B (2026)
   Michael Brown - Assigned to Grade 2A (2026)
   Sarah Davis - Assigned to Grade 2B (2026)
   Robert Taylor - Assigned to Grade 3A (2026)
   ```

---

## SECTION 6: STUDENTS CREATION & ASSIGNMENT
### Step 6.1: Navigate to Students Management
1. Click "Students" in main navigation menu
2. **Expected Screen**: 
   - Students list (empty)
   - "Create Student" button
   - Filter options (by class, grade, etc.)

### Step 6.2: Create Students for Grade 1A (3 students)
#### Student 1A-1: Aisha Ahmed
1. Click "Create Student"
2. **Form Fields**:
   ```
   First Name: Aisha
   Last Name: Ahmed
   Roll Number: 001
   Class: Grade 1A (2026) (from dropdown)
   Academic Year: 2026 (auto-filled)
   Date of Birth: 03/15/2015
   Gender: Female
   Parent/Guardian Name: Ahmed Ali
   Parent Phone: 9876543210
   Address: (Optional) Student address
   Status: Active (checkbox - should be checked)
   ```
3. Click "Save Student"
4. **Expected Result**:
   - Student created successfully
   - Shows detail page for Aisha
   - Displays "Grade 1A (2026)" as current class
   - Shows "Active" status

#### Student 1A-2: Bilal Hassan
1. Click "Create Student" again
2. **Form Fields**:
   ```
   First Name: Bilal
   Last Name: Hassan
   Roll Number: 002
   Class: Grade 1A (2026)
   Academic Year: 2026
   Date of Birth: 04/20/2015
   Gender: Male
   Parent/Guardian Name: Hassan Mohammed
   Parent Phone: 9876543211
   Status: Active ✓
   ```
3. Save

#### Student 1A-3: Clara Singh
1. Click "Create Student"
2. **Form Fields**:
   ```
   First Name: Clara
   Last Name: Singh
   Roll Number: 003
   Class: Grade 1A (2026)
   Academic Year: 2026
   Date of Birth: 05/10/2015
   Gender: Female
   Parent/Guardian Name: Singh Rajesh
   Parent Phone: 9876543212
   Status: Active ✓
   ```
3. Save

### Step 6.3: Create Students for Grade 1B (3 students)
#### Student 1B-1: David Lee
1. **Form Fields**:
   ```
   First Name: David
   Last Name: Lee
   Roll Number: 001
   Class: Grade 1B (2026)
   Date of Birth: 06/15/2015
   Gender: Male
   Parent/Guardian Name: Lee Chen
   Parent Phone: 9876543213
   Status: Active ✓
   ```

#### Student 1B-2: Emma Johnson
1. **Form Fields**:
   ```
   First Name: Emma
   Last Name: Johnson
   Roll Number: 002
   Class: Grade 1B (2026)
   Date of Birth: 07/20/2015
   Gender: Female
   Parent/Guardian Name: Johnson Mark
   Parent Phone: 9876543214
   Status: Active ✓
   ```

#### Student 1B-3: Fatima Khan
1. **Form Fields**:
   ```
   First Name: Fatima
   Last Name: Khan
   Roll Number: 003
   Class: Grade 1B (2026)
   Date of Birth: 08/10/2015
   Gender: Female
   Parent/Guardian Name: Khan Malik
   Parent Phone: 9876543215
   Status: Active ✓
   ```

### Step 6.4: Create Students for Grade 2A (3 students)
#### Student 2A-1: Grace Martinez
1. **Form Fields**:
   ```
   First Name: Grace
   Last Name: Martinez
   Roll Number: 001
   Class: Grade 2A (2026)
   Date of Birth: 09/15/2014
   Gender: Female
   Parent/Guardian Name: Martinez Juan
   Parent Phone: 9876543216
   Status: Active ✓
   ```

#### Student 2A-2: Henry Patel
1. **Form Fields**:
   ```
   First Name: Henry
   Last Name: Patel
   Roll Number: 002
   Class: Grade 2A (2026)
   Date of Birth: 10/20/2014
   Gender: Male
   Parent/Guardian Name: Patel Vijay
   Parent Phone: 9876543217
   Status: Active ✓
   ```

#### Student 2A-3: Iris Thompson
1. **Form Fields**:
   ```
   First Name: Iris
   Last Name: Thompson
   Roll Number: 003
   Class: Grade 2A (2026)
   Date of Birth: 11/10/2014
   Gender: Female
   Parent/Guardian Name: Thompson Robert
   Parent Phone: 9876543218
   Status: Active ✓
   ```

### Step 6.5: Create Students for Grade 2B (3 students)
#### Student 2B-1: Jack Wilson
1. **Form Fields**:
   ```
   First Name: Jack
   Last Name: Wilson
   Roll Number: 001
   Class: Grade 2B (2026)
   Date of Birth: 12/15/2014
   Gender: Male
   Parent/Guardian Name: Wilson George
   Parent Phone: 9876543219
   Status: Active ✓
   ```

#### Student 2B-2: Karen White
1. **Form Fields**:
   ```
   First Name: Karen
   Last Name: White
   Roll Number: 002
   Class: Grade 2B (2026)
   Date of Birth: 01/20/2015
   Gender: Female
   Parent/Guardian Name: White Paul
   Parent Phone: 9876543220
   Status: Active ✓
   ```

#### Student 2B-3: Leo Garcia
1. **Form Fields**:
   ```
   First Name: Leo
   Last Name: Garcia
   Roll Number: 003
   Class: Grade 2B (2026)
   Date of Birth: 02/10/2015
   Gender: Male
   Parent/Guardian Name: Garcia Carlos
   Parent Phone: 9876543221
   Status: Active ✓
   ```

### Step 6.6: Verify All Students Created
1. Go to Students page
2. Should show 12 students total:
   - 3 in Grade 1A
   - 3 in Grade 1B
   - 3 in Grade 2A
   - 3 in Grade 2B
3. Each student shows:
   - Name, Roll, Class, Status
   - Can click to view details

---

## SECTION 7: VERIFY SYSTEM STATE BEFORE PAYMENTS
### Step 7.1: Check Dashboard Statistics
1. Go to Dashboard
2. Verify displayed stats:
   - Total Students: 12
   - Total Classes: 5
   - Total Teachers: 5
   - Active Year: 2026
   - Current Term: First Term 2026

### Step 7.2: Check Classes Page
1. Go to Classes
2. Each class should show:
   ```
   Grade 1A - Teacher: John Smith - Students: 3
   Grade 1B - Teacher: Jane Wilson - Students: 3
   Grade 2A - Teacher: Michael Brown - Students: 3
   Grade 2B - Teacher: Sarah Davis - Students: 3
   Grade 3A - Teacher: Robert Taylor - Students: 0
   ```

### Step 7.3: Check Fee Dashboard (Before Payments)
1. Go to Fees dashboard (`/fees/`)
2. Should show:
   - Total Students: 12
   - Total Fee: 1,440.00 (12 × 120)
   - Total Paid: 0.00 (no payments yet)
   - Total Outstanding: 1,440.00
   - For each student:
     - Fee: 120.00
     - Paid: 0.00
     - Outstanding: 120.00
     - Arrears: 0.00

---

## SECTION 8: PAYMENT RECORDING (FIRST TERM)
### Step 8.1: Navigate to Payments
1. Click "Payments" in main menu
2. Or go to Fees → "Record Payment"
3. Click "Create Payment" or "New Payment"

### Step 8.2: Record Payment 1 - Aisha Ahmed FULL PAYMENT
1. **Form Fields**:
   ```
   Student: Aisha Ahmed (search/select)
   Class: Grade 1A (2026) (auto-filled)
   Academic Year: 2026 (auto-filled)
   Term: First Term 2026 (auto-filled)
   Amount: 120.00 (full fee)
   Payment Date: 02/01/2026
   Payment Method: Cash / Check / Bank Transfer (your choice)
   Reference Number: PAY001
   Notes: (Optional) Full payment
   Status: Completed (should default)
   ```
2. Click "Save Payment" or "Record Payment"
3. **Expected Result**:
   - Payment created successfully
   - Receipt number generated
   - Shows "Payment recorded for Aisha Ahmed"
   - Amount reflects in system

### Step 8.3: Record Payment 2 - Bilal Hassan PARTIAL PAYMENT
1. Click "Create Payment"
2. **Form Fields**:
   ```
   Student: Bilal Hassan
   Class: Grade 1A (2026)
   Term: First Term 2026
   Amount: 80.00 (partial - 40 remaining)
   Payment Date: 02/05/2026
   Reference Number: PAY002
   Status: Completed
   ```
3. Save
4. **Expected Result**: 
   - Payment recorded
   - Outstanding for Bilal: 40.00 (120 - 80)

### Step 8.4: Record Payment 3 - Clara Singh NO PAYMENT
- Skip recording payment for Clara (will show as unpaid)

### Step 8.5: Record Payment 4 - David Lee FULL PAYMENT
1. **Form Fields**:
   ```
   Student: David Lee
   Term: First Term 2026
   Amount: 120.00
   Payment Date: 02/10/2026
   Reference Number: PAY003
   Status: Completed
   ```

### Step 8.6: Record Payment 5 - Emma Johnson FULL PAYMENT
1. **Form Fields**:
   ```
   Student: Emma Johnson
   Term: First Term 2026
   Amount: 120.00
   Payment Date: 02/12/2026
   Reference Number: PAY004
   Status: Completed
   ```

### Step 8.7: Record Payment 6 - Fatima Khan NO PAYMENT
- Skip (will show as unpaid)

### Step 8.8: Record Payment 7 - Grace Martinez FULL PAYMENT
1. **Form Fields**:
   ```
   Student: Grace Martinez
   Term: First Term 2026
   Amount: 120.00
   Payment Date: 02/15/2026
   Reference Number: PAY005
   Status: Completed
   ```

### Step 8.9: Record Payment 8 - Henry Patel PARTIAL PAYMENT
1. **Form Fields**:
   ```
   Student: Henry Patel
   Term: First Term 2026
   Amount: 60.00
   Payment Date: 02/18/2026
   Reference Number: PAY006
   Status: Completed
   ```
2. Outstanding: 60.00

### Step 8.10: Record Payment 9 - Iris Thompson FULL PAYMENT
1. **Form Fields**:
   ```
   Student: Iris Thompson
   Term: First Term 2026
   Amount: 120.00
   Payment Date: 02/20/2026
   Reference Number: PAY007
   Status: Completed
   ```

### Step 8.11: Record Payment 10 - Jack Wilson NO PAYMENT
- Skip (will show unpaid)

### Step 8.12: Record Payment 11 - Karen White PARTIAL PAYMENT
1. **Form Fields**:
   ```
   Student: Karen White
   Term: First Term 2026
   Amount: 100.00
   Payment Date: 02/22/2026
   Reference Number: PAY008
   Status: Completed
   ```
2. Outstanding: 20.00

### Step 8.13: Record Payment 12 - Leo Garcia FULL PAYMENT
1. **Form Fields**:
   ```
   Student: Leo Garcia
   Term: First Term 2026
   Amount: 120.00
   Payment Date: 02/25/2026
   Reference Number: PAY009
   Status: Completed
   ```

### Step 8.14: Verify Payment Summary (First Term)
1. Go to Fees Dashboard
2. **Expected Summary**:
   ```
   Total Students: 12
   Total Fee: 1,440.00
   Total Paid: 1,040.00
   Total Outstanding: 400.00
   
   Breakdown:
   - Paid Full: 7 students (Aisha, David, Emma, Grace, Iris, Leo)
   - Paid Partial: 3 students (Bilal: 80/120, Henry: 60/120, Karen: 100/120)
   - Unpaid: 2 students (Clara, Fatima, Jack)
   ```

### Step 8.15: View Student Payment Details
1. Click on "Aisha Ahmed" from students list
2. Click "Payment History" or "Payments" tab
3. **Expected**:
   - Shows payment PAY001
   - Date: 02/01/2026
   - Amount: 120.00
   - Status: Completed
   - Receipt/Reference Number visible

---

## SECTION 9: TERM TRANSITION & ARREARS
### Step 9.1: Create Second Term (Already created in Step 3.3, but verify)
1. Go to Settings → Terms
2. Verify "Second Term 2026" exists:
   ```
   Name: Second Term 2026
   Dates: 05/01/2026 - 08/15/2026
   Fee: 120.00
   Current: ☐ (not current yet)
   ```

### Step 9.2: Set Second Term as Current
1. Go to Settings → Terms or Active Terms
2. Find "Second Term 2026"
3. Click "Set as Current" or similar button
4. **Expected Result**:
   - Second Term marked as current
   - First Term marked as previous/inactive
   - System switches to use Second Term

### Step 9.3: Check Arrears Calculation (IMPORTANT TEST)
1. Go to Fees Dashboard
2. Look at "Bilal Hassan" (who owed 40.00 from Term 1):
   ```
   Expected display:
   - Previous Term Arrears: 40.00 (from Term 1)
   - Current Term Fee: 120.00 (Term 2)
   - Total Outstanding: 160.00 (120 + 40)
   - Paid (Term 2): 0.00
   ```
3. Look at "Henry Patel" (who owed 60.00 from Term 1):
   ```
   Expected display:
   - Previous Term Arrears: 60.00 (from Term 1)
   - Current Term Fee: 120.00 (Term 2)
   - Total Outstanding: 180.00 (120 + 60)
   - Paid (Term 2): 0.00
   ```
4. Look at "Karen White" (who owed 20.00 from Term 1):
   ```
   Expected display:
   - Previous Term Arrears: 20.00 (from Term 1)
   - Current Term Fee: 120.00 (Term 2)
   - Total Outstanding: 140.00 (120 + 20)
   - Paid (Term 2): 0.00
   ```

### Step 9.4: Record Arrears Payment for Bilal Hassan
1. Go to Create Payment
2. **Form Fields**:
   ```
   Student: Bilal Hassan
   Term: Second Term 2026
   Amount: 160.00 (covers both arrears + current term fee)
   Payment Date: 05/15/2026
   Reference Number: PAY010
   Status: Completed
   ```
3. Click Save
4. **Expected Result**:
   - Payment recorded
   - Outstanding for Bilal: 0.00
   - Arrears: 0.00

### Step 9.5: Verify Corrected Balances (After Payment)
1. Go to Fees Dashboard
2. **Bilal Hassan** should now show:
   ```
   - Previous Arrears: 0.00 (paid)
   - Current Fee: 120.00
   - Paid: 160.00
   - Outstanding: 0.00
   ```
3. **Henry Patel** still owes:
   ```
   - Previous Arrears: 60.00
   - Current Fee: 120.00
   - Paid: 0.00
   - Outstanding: 180.00
   ```

---

## SECTION 10: STUDENT MOVEMENT
### Step 10.1: Navigate to Student Movement
1. Go to Students page
2. Find a student (e.g., Aisha Ahmed from Grade 1A)
3. Click on the student name to view details
4. Look for "Move Student" or "Student Movement" button/option

### Step 10.2: Promote Single Student (Grade 1A → Grade 2A)
1. Select Aisha Ahmed from Grade 1A
2. Click "Student Movement" or "Move to Next Grade"
3. **Form Fields**:
   ```
   Current Class: Grade 1A (2026) (display only)
   New Class: Grade 2A (2026) (from dropdown)
   Reason: Promotion (dropdown option)
   Effective Date: 04/20/2026 (end of term)
   Notes: (Optional) Promoted to next grade
   ```
4. Click "Confirm" or "Move"
5. **Expected Result**:
   - Success message
   - Aisha now shows in Grade 2A
   - Grade 1A shows 2 students (was 3)
   - Grade 2A shows 4 students (was 3)
   - Movement recorded in history

### Step 10.3: View Student Movement History
1. Click on Aisha Ahmed
2. Find "Movement History" or "Transfer History" tab
3. **Expected Display**:
   ```
   Date: 04/20/2026
   From: Grade 1A (2026)
   To: Grade 2A (2026)
   Type: Promotion
   Notes: Promoted to next grade
   ```

### Step 10.4: Demote a Student (Grade 2A → Grade 1A)
1. Go to Students, find Henry Patel in Grade 2A
2. Click on Henry
3. Click "Student Movement" or "Move"
4. **Form Fields**:
   ```
   Current Class: Grade 2A (2026)
   New Class: Grade 1B (2026) (select different class)
   Reason: Demotion
   Effective Date: 04/20/2026
   ```
5. Click "Confirm"
6. **Expected Result**: 
   - Henry transferred to Grade 1B
   - Grade 2A count decreased
   - Grade 1B count increased

---

## SECTION 11: PAYMENTS & FEES VERIFICATION
### Step 11.1: View Fee Dashboard Summary
1. Go to Fees Dashboard
2. **Display Should Show**:
   - Title: "Fee Management Dashboard"
   - Stats boxes:
     - Total Students: [count]
     - Total Fee: [total amount]
     - Total Paid: [total paid]
     - Total Outstanding: [remaining]
   - Table with all students showing:
     - Name
     - Class
     - Roll
     - Fee
     - Paid
     - Outstanding
     - Arrears
     - Action buttons (View, History, etc.)

### Step 11.2: Export Fee Data as CSV
1. On Fee Dashboard, find "Export" button
2. Click "Export as CSV" or "Download Report"
3. **Expected Result**:
   - CSV file downloads
   - File named something like: `fees_2026_term1.csv` or similar
   - Contains columns: Student, Class, Fee, Paid, Outstanding, Arrears

### Step 11.3: View Individual Payment History
1. Go to Students page
2. Click on any student (e.g., David Lee)
3. Click "Payment History" tab
4. **Expected Display**:
   ```
   Payment: PAY003
   Date: 02/10/2026
   Amount: 120.00
   Status: Completed
   Reference: PAY003
   ```
5. Should show "Download Receipt" or similar option

### Step 11.4: Export Student Payment History
1. On payment history page, find "Export" button
2. Click to download CSV
3. **Expected**: CSV with payment details

---

## SECTION 12: SEARCH & FILTERING
### Step 12.1: Search by Student Name
1. Go to Dashboard or Students page
2. Find "Search" bar at top
3. Type "Aisha"
4. **Expected Result**:
   - Shows "Aisha Ahmed" in results
   - Can click to view details
   - Shows class and other info

### Step 12.2: Filter Students by Class
1. Go to Students page
2. Find "Filter by Class" dropdown
3. Select "Grade 1A"
4. **Expected Result**:
   - Shows only Grade 1A students
   - Count shows 2 or 3 (depending on movements)
   - Other classes hidden

### Step 12.3: Filter by Status
1. Go to Students page
2. Find "Filter by Status" dropdown (if available)
3. Select "Active"
4. **Expected Result**:
   - Shows all active students
   - Any inactive students hidden

### Step 12.4: Global Search
1. On Dashboard, find "Global Search" feature
2. Search for "John Smith" (teacher name)
3. **Expected Result**:
   - Shows John Smith teacher profile
   - Shows Grade 1A (2026) assignment
   - Shows option to view details

---

## SECTION 13: ERROR HANDLING TESTS
### Step 13.1: Test Duplicate Prevention
1. Go to Create Student
2. Try creating student with:
   ```
   First Name: Aisha
   Last Name: Ahmed
   Roll: 001
   Class: Grade 2A (where Aisha is now)
   ```
3. Try to Save
4. **Expected Result**: 
   - Error message: "Student with this roll number already exists in this class"
   - Student NOT created

### Step 13.2: Test Teacher Assignment Constraint
1. Go to Teacher John Smith
2. Try to "Assign Class" to Grade 2A (while already assigned to Grade 1A)
3. **Expected Result**:
   - Error message: "Teacher can only teach one class per year"
   - Assignment NOT changed

### Step 13.3: Test Negative Payment Amount
1. Go to Create Payment
2. Enter:
   ```
   Student: Any student
   Amount: -100.00 (negative)
   ```
3. Try to Save
4. **Expected Result**:
   - Error message: "Amount must be positive"
   - Payment NOT recorded

### Step 13.4: Test Missing Required Fields
1. Go to Create Class
2. Leave "Grade" field empty
3. Try to Save
4. **Expected Result**:
   - Error message: "Grade is required"
   - Form NOT submitted

---

## SECTION 14: DATA EXPORT & REPORTING
### Step 14.1: Export Academic Calendar
1. Go to Settings → Academic Calendar (if available)
2. Click "Export Calendar"
3. **Expected**: CSV or PDF with all terms and dates

### Step 14.2: Export Fee Structure
1. Go to Settings → Fee Configuration
2. Click "Export Structure"
3. **Expected**: File with all term fees

### Step 14.3: Generate Report (if available)
1. Look for "Reports" section in admin menu
2. Select report type (e.g., "Student Fee Report")
3. Select parameters (Year, Term, Class)
4. Click "Generate"
5. **Expected**: Report displays or downloads

---

## SECTION 15: SYSTEM CLEANUP & FINAL VERIFICATION
### Step 15.1: Review All Data
1. Dashboard should show:
   ```
   Total Students: 12
   Total Classes: 5
   Total Teachers: 5
   Total Payments: ~10
   Total Fees: 1,440.00 + (payments in Term 2)
   ```

### Step 15.2: Verify No Errors
1. Check browser console (F12 → Console)
2. Should have NO red error messages
3. Only warnings/info logs acceptable

### Step 15.3: Test Logout
1. Click profile icon or "Logout" in menu
2. **Expected**: 
   - Redirected to login page
   - Cannot access protected pages without login

### Step 15.4: Test Re-login
1. On login page, login again with admin credentials
2. **Expected**: 
   - Logged in successfully
   - All data still present
   - Can access all pages

---

## FINAL CHECKLIST

- [ ] Section 1: Login & Authentication working
- [ ] Section 2: Academic Year created and activated
- [ ] Section 3: Three terms created with First Term as current
- [ ] Section 4: Five classes created
- [ ] Section 5: Five teachers created and assigned to classes
- [ ] Section 6: 12 students created in their respective classes
- [ ] Section 7: System state verified (dashboard, classes, fees)
- [ ] Section 8: Payments recorded for various scenarios
- [ ] Section 9: Term transition works, arrears calculated correctly
- [ ] Section 10: Student movement (promotion/demotion) works
- [ ] Section 11: Fees dashboard displays and exports work
- [ ] Section 12: Search and filtering work
- [ ] Section 13: Error handling validates correctly
- [ ] Section 14: Data export and reporting works
- [ ] Section 15: System clean up and logout/login works

---

## QUICK REFERENCE - KEY FORMULAS

**Outstanding Balance Calculation:**
```
Outstanding = Current Term Fee + Previous Term Arrears - Current Payments
```

**Example - Bilal Hassan after payment in Term 2:**
```
Outstanding = 120 + 40 - 160 = 0.00 ✓
```

**Example - Henry Patel without payment in Term 2:**
```
Outstanding = 120 + 60 - 0 = 180.00
```

---

## TROUBLESHOOTING

**If students not appearing in class:**
- Verify student is assigned to correct class
- Check academic year matches (2026)
- Try refreshing page (Ctrl+F5)

**If fees showing as 0:**
- Verify term fee is set (120.00)
- Check student is marked Active
- Verify term is marked as Current

**If payments not recording:**
- Check student exists
- Verify term is selected
- Ensure payment date is within term dates
- Amount must be positive

**If teacher cannot assign to class:**
- Teacher must be created first
- Class must exist in same year
- Teacher cannot teach 2 classes in same year

---

## NEXT STEPS AFTER COMPLETE TESTING

1. **Document any bugs found** with:
   - URL where error occurred
   - Steps to reproduce
   - Expected vs actual result
   - Screenshot if possible

2. **Record performance observations**:
   - Page load times
   - Slow operations
   - UI/UX improvements needed

3. **Verify all calculations** match expected formulas

4. **Test with different admin accounts** if available

5. **Load test** by creating more data:
   - 50+ students
   - Multiple years/terms
   - Large payments history

