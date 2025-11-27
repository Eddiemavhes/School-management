# ULTRA DETAILED TESTING FLOW - COMPLETE SYSTEM

## PREPARATION - VERIFY CLEAN STATE
**Before starting, verify:**
- Database reset ✓
- Teachers deleted ✓
- Students deleted ✓
- Classes deleted ✓
- Academic years deleted ✓
- Payments deleted ✓
- Only Admin login credentials preserved ✓

---

## PHASE 0: SCHOOL SETUP (NEW - DO THIS FIRST!)
### Step 0.1: Navigate to School Details Settings
1. Login to system with admin credentials
2. On Dashboard, find "Settings" in menu
3. Click "Settings" → should see options like:
   - School Details
   - Profile
   - Admin Management
4. Click "School Details" or "Configure School"

### Step 0.2: Fill School Details Form
**This is CRITICAL - school name will appear in header**

#### SECTION 1: Basic Information
```
Field: School Name *
Value: "Green Valley International School"
Type: Text
Description: This is your official school name - will appear in header

Field: School Code *
Value: "GV2026"
Type: Text
Description: Unique code for your school

Field: School Motto
Value: "Excellence Through Education"
Type: Text
Description: School's mission statement

Field: School Type
Value: "COMBINED"
Type: Dropdown (PRIMARY, SECONDARY, HIGHER_SECONDARY, COMBINED)

Field: Established Year
Value: 2010
Type: Number
```

#### SECTION 2: Contact Information
```
Field: Principal Name
Value: "Dr. James Wilson"

Field: Email Address
Value: "principal@greenvalley.edu"

Field: Primary Phone
Value: "+1-555-123-4567"

Field: Alternate Phone
Value: "+1-555-123-4568"
```

#### SECTION 3: Address Information
```
Field: Street Address
Value: "456 Education Boulevard"

Field: City
Value: "Springfield"

Field: State/Province
Value: "Illinois"

Field: Postal Code
Value: "62701"

Field: Country
Value: "United States"
```

#### SECTION 4: Branding & Colors
```
Field: Header Color
Value: "#1e40af" (Dark Blue)
Note: Can use color picker or type hex code
Visual Check: After saving, header should show this color

Field: Accent Color
Value: "#0891b2" (Teal)
Note: Used for buttons and highlights

Field: Logo URL
Value: "https://example.com/school-logo.png" (optional)
```

#### SECTION 5: Registration & Affiliation
```
Field: Board Affiliation
Value: "CBSE"
Options: Any board (CBSE, ICSE, State Board, etc.)

Field: Registration Number
Value: "REG/GV/2010/00001"

Field: Tax ID / PAN
Value: "AAXPT5055K"

Field: Working Days Per Week
Value: "6 Days"
Options: 5 Days or 6 Days

Field: Enable Online Payments
Value: UNCHECKED ☐ (for now)

Field: Payment Gateway
Value: "None"
Options: None, Stripe, Razorpay, PayPal
```

### Step 0.3: Save School Details
1. Click "Save School Details" button (bottom of form)
2. **Expected Result**:
   - Green success message: "School details updated successfully!"
   - Returns to settings page
   - School name should now appear in system header

### Step 0.4: Verify School Name in Header
1. Go to any page (Dashboard, Classes, Students, etc.)
2. Look at top of page
3. **Expected**: Page header should show:
   ```
   GREEN VALLEY INTERNATIONAL SCHOOL
   Excellence Through Education
   ```
4. Colors should match what you set (header color)

### Step 0.5: Verify School Details Display
1. Go back to Settings → School Details
2. All fields should show your entered data
3. Colors should display with color picker showing correct color
4. **Expected**: All information preserved and displayed correctly

---

## SECTION 1: LOGIN & AUTHENTICATION (EXACT STEPS)
### Step 1.1: Open Browser and Navigate to Login
1. **Action**: Open your web browser (Chrome, Firefox, Edge, etc.)
2. **URL**: Type in address bar: `http://127.0.0.1:8000/login/`
3. **Expected Screen**:
   ```
   ┌─────────────────────────────────────────┐
   │  School Management System               │
   │  [School Logo - if configured]          │
   │                                         │
   │  Email: [____________]                  │
   │  Password: [____________]               │
   │                                         │
   │  [ Login ]                              │
   │                                         │
   │  Forgot Password? | Sign Up             │
   └─────────────────────────────────────────┘
   ```

### Step 1.2: Enter Admin Credentials
1. **Email Field**:
   - Click on email input box
   - Type: Your admin email (e.g., `admin@school.com`)
   - Cursor should move through text as you type

2. **Password Field**:
   - Click on password input box
   - Type: Your admin password
   - Characters should appear as dots (••••••••)

3. **Verify Before Submit**:
   - Email shows: "admin@school.com" (or your actual email)
   - Password field shows dots (don't reveal actual password)

### Step 1.3: Submit Login Form
1. Click "Login" button
2. **Expected Behavior** (should take 1-2 seconds):
   - Login button may show loading state (gray, disabled)
   - Browser processes your request
   - Redirects to `/dashboard/`

3. **Expected Result Screen**:
   ```
   Dashboard - School Management System
   
   Welcome, [Your Name]!
   
   Quick Stats:
   - Total Classes: 0
   - Total Students: 0
   - Total Teachers: 0
   - Pending Fees: $0.00
   
   Recent Activities:
   [Will be empty initially]
   
   Navigation Menu:
   - Academic Management
   - Classes
   - Teachers
   - Students
   - Payments & Fees
   - Settings
   ```

### Step 1.4: Verify You Can Access All Menu Items
1. Click "Classes" in menu → Should open `/classes/`
2. Click "Teachers" in menu → Should open `/teachers/`
3. Click "Students" in menu → Should open `/students/`
4. Click "Dashboard" → Should return to dashboard
5. **Expected**: All pages load without errors, show empty lists initially

### Step 1.5: Verify User Profile
1. Look for profile icon/menu in top right corner
2. **Expected Options**:
   - View Profile
   - Edit Profile
   - Change Password
   - Logout
3. Click "View Profile"
4. **Expected**: Shows:
   - Your name
   - Email address
   - Role (Admin)
   - Date joined
   - Login attempts (should be fresh)

### Step 1.6: Logout Test (SKIP FOR NOW - Continue Testing)
- Don't logout yet, we'll do this at the end

---

## SECTION 2: ACADEMIC YEAR SETUP (REQUIRED - DO NOT SKIP)

### Step 2.1: Access Academic Years Settings
1. Click **Settings** in the top menu
2. Navigate to **Academic Year Management** or **Academic Configuration**
3. Click **Academic Years**

**Expected Screen**: Academic Years management page with year list and create button

### Step 2.2: Create Academic Year 2026

**Navigate to**: `http://127.0.0.1:8000/settings/academic-years/`

**Click "Create New Year" button on the left panel**

**Complete the form with:**

```html
<div class="settings-container">
  <div class="currently-active-section">
    <div class="badge">CURRENTLY ACTIVE</div>
    <h2>2026</h2>
    <p>January 1, 2026 — December 31, 2026</p>
  </div>

  <div class="main-content">
    <!-- LEFT PANEL: CREATE FORM -->
    <div class="create-year-panel">
      <h3>Create New Year</h3>
      
      <div class="form-group">
        <label>Year</label>
        <input type="number" placeholder="e.g., 2028" value="2028" />
      </div>

      <div class="form-group">
        <label>Start Date</label>
        <input type="date" placeholder="Pick date" />
      </div>

      <div class="form-group">
        <label>End Date</label>
        <input type="date" placeholder="Pick date" />
      </div>

      <div class="form-group checkbox">
        <input type="checkbox" id="setActive" />
        <label for="setActive">Set as Active</label>
      </div>

      <button class="btn-create">Create Year</button>
    </div>

    <!-- RIGHT PANEL: ALL ACADEMIC YEARS LIST -->
    <div class="years-list-panel">
      <h3>All Academic Years</h3>
      
      <div class="year-card">
        <div class="year-header">
          <h4>2026</h4>
          <span class="badge-active">ACTIVE NOW</span>
        </div>
        <p>Jan 01, 2026 — Dec 31, 2026</p>
      </div>
    </div>
  </div>
</div>
```

3. Fill in the fields:
   - **Year**: 2028
   - **Start Date**: (Select date)
   - **End Date**: (Select date)
   - **Set as Active**: ☐ (Leave unchecked)

4. Click **Create Year**
5. **Expected**: 
   - ✓ Success message appears
   - ✓ New year appears in the right panel list
   - ✓ Status shows "Not Active" until activated

### Step 2.3: Activate Academic Year 2026

1. On the academic years list, find the **2026** entry
2. Click the **Activate** button or **Set as Active** link
3. **Expected Results**:
   - ✓ Status changes to **ACTIVE NOW** (green badge)
   - ✓ 2026 becomes the working year
   - ✓ System defaults to 2026 for all new records

### Step 2.4: Verify Active Year on Dashboard
1. Navigate to Dashboard
2. **Expected**: "CURRENTLY ACTIVE" badge displays with "2026" and date range
3. ✓ 2026 shows as active year

---

## SECTION 3: ACADEMIC TERMS SETUP (DETAILED - 3 TERMS)
### Step 3.1: Navigate to Terms Management
1. Click "Settings" in menu
2. Find "Academic Terms" or "Term Management"
3. Look for "Active Terms" or "Current Term"
4. Click to access terms page
5. **Expected URL**: `/settings/active-year-term/` or `/settings/academic-terms/`
6. **Expected Screen**:
   ```
   Academic Terms (2026)
   
   Current Term: [dropdown or display]
   
   [Create New Term] button
   
   Terms List:
   - Column 1: Term Name
   - Column 2: Dates
   - Column 3: Fee
   - Column 4: Status
   - Column 5: Actions
   ```

### Step 3.2: Create First Term - "First Term 2026"
1. Click "Create Term" or "New Term" button
2. **Form Fields** (Fill in exact order):

   **Field 1: Academic Year**
   - Type: Dropdown
   - Value: 2026
   - **Action**: Click dropdown, select 2026
   - Should be auto-populated since 2026 is active

   **Field 2: Term Name**
   - Type: Text field
   - Value: `First Term 2026`
   - **Action**: Click field, type exactly as shown
   
   **Field 3: Term Number** (if separate field)
   - Type: Number or Dropdown
   - Value: `1` or `First`
   - **Action**: Select appropriate option

   **Field 4: Start Date**
   - Type: Date picker
   - Value: `01/15/2026` (January 15, 2026)
   - **Action**: Click date picker, navigate to January 2026, click 15th
   - Alternative: Type `15/01/2026` or `2026-01-15` depending on format

   **Field 5: End Date**
   - Type: Date picker
   - Value: `04/15/2026` (April 15, 2026)
   - **Action**: Click date picker, navigate to April 2026, click 15th

   **Field 6: Default Fee**
   - Type: Currency field (number with 2 decimals)
   - Value: `120.00`
   - **Action**: Click field, clear if needed, type 120.00
   - Note: This is the fee each student must pay

   **Field 7: Is Current Term** (Checkbox)
   - Type: Checkbox ☑ or ☐
   - Action: CHECK THIS BOX ✓
   - Reason: We want First Term to be the active/current term
   - Visual: Look for checkmark after clicking

3. **Click "Save Term" or "Create"**
4. **Expected Results**:
   - Success message: "First Term 2026 created successfully"
   - Redirected to terms list
   - Shows entry:
     ```
     Term Name: First Term 2026
     Dates: 01/15/2026 - 04/15/2026
     Fee: 120.00
     Status: CURRENT ✓
     ```

### Step 3.3: Create Second Term - "Second Term 2026"
1. Click "Create Term" again
2. **Form Fields**:
   ```
   Academic Year: 2026
   Term Name: Second Term 2026
   Term Number: 2 (or Second)
   Start Date: 05/01/2026 (May 1, 2026)
   End Date: 08/15/2026 (August 15, 2026)
   Default Fee: 120.00
   Is Current Term: ☐ UNCHECK (leave unchecked)
   ```
3. Click "Save Term"
4. **Expected Results**:
   - Second Term created
   - Shows in list as "Not Current" or similar

### Step 3.4: Create Third Term - "Third Term 2026"
1. Click "Create Term"
2. **Form Fields**:
   ```
   Academic Year: 2026
   Term Name: Third Term 2026
   Term Number: 3 (or Third)
   Start Date: 09/01/2026 (September 1, 2026)
   End Date: 12/15/2026 (December 15, 2026)
   Default Fee: 120.00
   Is Current Term: ☐ UNCHECK
   ```
3. Click "Save Term"

### Step 3.5: Verify All Terms Created
1. On Terms page, you should now see:
   ```
   ┌─────────────────────────────────────────────┐
   │ Academic Terms for 2026                     │
   ├─────────────────────────────────────────────┤
   │ Term Name           Dates      Fee   Status │
   ├─────────────────────────────────────────────┤
   │ First Term 2026    01/15-04/15  120  CURRENT✓
   │ Second Term 2026   05/01-08/15  120  -
   │ Third Term 2026    09/01-12/15  120  -
   └─────────────────────────────────────────────┘
   ```

2. Check marks/status indicators:
   - First Term: Should show as "CURRENT" or have checkmark
   - Other terms: Should show as "Not Current" or empty

3. All fees should show "120.00"

### Step 3.6: Verify in System
1. Go to Dashboard
2. Look for display: "Current Term: First Term 2026"
3. Or find dropdown that shows active term
4. **Expected**: First Term 2026 should be selected/highlighted

---

## SECTION 4: CLASSES CREATION (5 CLASSES)
### Step 4.1: Navigate to Classes Page
1. Click "Classes" in main navigation menu
2. **Expected URL**: `/classes/`
3. **Expected Screen**:
   ```
   CLASS MANAGEMENT
   [Search Box] [Filters] [Create Class]
   
   Classes List (Empty initially):
   Grade | Section | Year | Teacher | Students | Actions
   ```

### Step 4.2: Create Class 1 - Grade 1, Section A
**Detailed Steps:**

1. Click "Create Class" button (usually top right or top left)
2. **Expected**: Form page opens
3. **URL should be**: `/classes/create/`

4. **Form Fields** (Fill in order):

   **Field 1: Grade**
   - Type: Dropdown
   - Value: Select `1` (Grade 1)
   - **Action**: Click dropdown arrow, scroll if needed, click "1" or "Grade 1"
   - Visual: After selection, "1" should appear in field

   **Field 2: Section**
   - Type: Dropdown
   - Value: Select `A`
   - **Action**: Click dropdown arrow, options usually limited (A, B, C, D)
   - Visual: "A" should appear in field

   **Field 3: Academic Year**
   - Type: Number or Dropdown (usually auto-filled)
   - Value: `2026`
   - **Action**: Should auto-populate since 2026 is active
   - If not auto-filled, manually select or type 2026
   - Check: Verify "2026" shows in field

   **Field 4: Teacher** (Optional - Leave BLANK for now)
   - Type: Dropdown with search
   - Value: [Leave EMPTY]
   - **Action**: Do NOT select anything, leave blank
   - Reason: We'll assign teachers later in bulk
   - Visual: Field should appear empty

5. **Click "Create Class"**
6. **Expected Results**:
   - Success message: "Class 1A created successfully"
   - Green alert notification
   - Returns to classes list
   - Shows new entry:
     ```
     Grade: 1
     Section: A
     Year: 2026
     Teacher: None
     Students: 0
     [Edit] [Delete] [View]
     ```

### Step 4.3: Create Class 2 - Grade 1, Section B
1. Click "Create Class" again
2. **Form Fields**:
   ```
   Grade: 1
   Section: B
   Academic Year: 2026
   Teacher: [Leave blank]
   ```
3. Click "Create Class"
4. **Verify**: "Grade 1B (2026)" appears in list

### Step 4.4: Create Class 3 - Grade 2, Section A
1. Click "Create Class"
2. **Form Fields**:
   ```
   Grade: 2
   Section: A
   Academic Year: 2026
   Teacher: [Leave blank]
   ```
3. Click "Create Class"

### Step 4.5: Create Class 4 - Grade 2, Section B
1. Click "Create Class"
2. **Form Fields**:
   ```
   Grade: 2
   Section: B
   Academic Year: 2026
   Teacher: [Leave blank]
   ```
3. Click "Create Class"

### Step 4.6: Create Class 5 - Grade 3, Section A
1. Click "Create Class"
2. **Form Fields**:
   ```
   Grade: 3
   Section: A
   Academic Year: 2026
   Teacher: [Leave blank]
   ```
3. Click "Create Class"

### Step 4.7: Final Verification - All Classes Present
1. On Classes page, verify you see all 5:
   ```
   ✓ Grade 1, Section A - 0 students - No Teacher
   ✓ Grade 1, Section B - 0 students - No Teacher
   ✓ Grade 2, Section A - 0 students - No Teacher
   ✓ Grade 2, Section B - 0 students - No Teacher
   ✓ Grade 3, Section A - 0 students - No Teacher
   ```

2. Count verification:
   - Total should show "5 Classes"
   - Each section should have 0 students initially
   - No teachers assigned yet

3. Sorting verification:
   - Classes should be sorted by Grade then Section
   - Grade 1A, 1B should appear before Grade 2A, 2B

---

## SECTION 5: TEACHERS CREATION & ASSIGNMENT
### Step 5.1: Navigate to Teachers Page
1. Click "Teachers" in main navigation menu
2. **Expected URL**: `/teachers/`
3. **Expected Screen**:
   ```
   TEACHER MANAGEMENT
   [Search Box] [Filters] [Create Teacher]
   
   Teachers List (Empty initially):
   Name | Specialization | Email | Status | Actions
   ```

### Step 5.2: Create Teacher 1 - John Smith
**Detailed Form Filling:**

1. Click "Create Teacher" button
2. **URL**: `/teachers/create/`
3. **Form appears with these fields**:

   **Field 1: First Name**
   - Label: "First Name *" (red asterisk = required)
   - Type: Text input
   - Value: `John`
   - **Action**: Click field, type "John"

   **Field 2: Last Name**
   - Label: "Last Name *"
   - Type: Text input
   - Value: `Smith`
   - **Action**: Click field, type "Smith"

   **Field 3: Email**
   - Label: "Email *"
   - Type: Email input
   - Value: `john.smith@school.com`
   - **Action**: Click field, type email
   - Validation: System should check for valid email format

   **Field 4: Password**
   - Label: "Password *"
   - Type: Password input (text shows as dots)
   - Value: `Teacher@123`
   - **Action**: Click field, type password
   - Note: Save this for later if teacher will login

   **Field 5: Phone Number**
   - Label: "Phone (Optional)"
   - Type: Text input
   - Value: `1234567890`
   - Format: Should accept digits, hyphens, + sign
   - **Action**: Click field, type

   **Field 6: Specialization**
   - Label: "Specialization (Optional)"
   - Type: Text input
   - Value: `Mathematics`
   - **Action**: Click field, type

   **Field 7: Qualification**
   - Label: "Qualification (Optional)"
   - Type: Text input
   - Value: `B.Ed`
   - **Action**: Click field, type

   **Field 8: Joining Date** (Optional)
   - Label: "Joining Date"
   - Type: Date picker
   - Value: `01/15/2026`
   - **Action**: Click date picker, select

   **Field 9: Teacher ID** (Optional)
   - Label: "Teacher ID"
   - Type: Text input
   - Value: `T001`
   - **Action**: Click field, type

   **Field 10: Bio** (Optional)
   - Label: "Bio / Additional Information"
   - Type: Text area
   - Value: `Experienced mathematics teacher with 5 years of experience`
   - **Action**: Click field, type

4. **Click "Save Teacher"**
5. **Expected Results**:
   - Success message: "Teacher John Smith created successfully"
   - Redirected to teacher detail page
   - Shows:
     ```
     John Smith
     Email: john.smith@school.com
     Specialization: Mathematics
     Phone: 1234567890
     Status: Active
     Current Class: Not assigned
     [Assign Class] [Edit] [Delete]
     ```

### Step 5.3: Assign Teacher 1 to Class 1A
1. On John Smith's detail page, click "Assign Class" button
2. **Form appears**:
   - **Class Dropdown**: Select "Grade 1A (2026)"
   - **Academic Year**: Should auto-fill as 2026
3. Click "Assign"
4. **Expected Results**:
   - Success message: "John Smith assigned to Grade 1A successfully"
   - Detail page updates:
     ```
     Current Class: Grade 1A (2026)
     [Change Assignment] [Remove Assignment]
     ```

### Step 5.4: Create & Assign Teachers 2-5
**Teacher 2: Jane Wilson**
```
Details:
- First Name: Jane
- Last Name: Wilson
- Email: jane.wilson@school.com
- Password: Teacher@123
- Phone: 1234567891
- Specialization: English
- Qualification: M.A
- Teacher ID: T002

Assign to: Grade 1B (2026)
```

**Teacher 3: Michael Brown**
```
Details:
- First Name: Michael
- Last Name: Brown
- Email: michael.brown@school.com
- Password: Teacher@123
- Phone: 1234567892
- Specialization: Science
- Qualification: B.Sc
- Teacher ID: T003

Assign to: Grade 2A (2026)
```

**Teacher 4: Sarah Davis**
```
Details:
- First Name: Sarah
- Last Name: Davis
- Email: sarah.davis@school.com
- Password: Teacher@123
- Phone: 1234567893
- Specialization: History
- Qualification: B.A
- Teacher ID: T004

Assign to: Grade 2B (2026)
```

**Teacher 5: Robert Taylor**
```
Details:
- First Name: Robert
- Last Name: Taylor
- Email: robert.taylor@school.com
- Password: Teacher@123
- Phone: 1234567894
- Specialization: Physical Education
- Qualification: B.Ed
- Teacher ID: T005

Assign to: Grade 3A (2026)
```

### Step 5.5: Verify All Teachers Assigned
1. Go to Teachers page
2. **Verify display**:
   ```
   ┌────────────────────────────────────────────┐
   │ TEACHERS LIST                              │
   ├────────────────────────────────────────────┤
   │ Name     │ Spec       │ Email       │Class │
   ├────────────────────────────────────────────┤
   │ John S.  │ Math       │ john.s..    │1A   │
   │ Jane W.  │ English    │ jane.w...   │1B   │
   │ Michael B│ Science    │ michael.b.. │2A   │
   │ Sarah D. │ History    │ sarah.d..   │2B   │
   │ Robert T.│ PE         │ robert.t..  │3A   │
   └────────────────────────────────────────────┘
   ```

3. Count verification: All 5 teachers should be visible
4. Each should show their assigned class
5. Status should show "Active" for all

---

## [CONTINUING WITH SECTIONS 6-15 IN NEXT PART DUE TO LENGTH]

**This guide continues with:**
- Section 6: Students Creation (12 students across 4 classes)
- Section 7: System Verification
- Section 8: Payment Recording
- Section 9: Term Transition & Arrears
- Section 10: Student Movement
- Section 11: Fee Dashboard
- Section 12: Search & Filtering
- Section 13: Error Handling
- Section 14: Data Export
- Section 15: Cleanup & Verification

**Continue with DETAILED_TESTING_FLOW.md for Sections 6-15**

---

## SECTION 6: STUDENTS CREATION (12 STUDENTS - DETAILED)

### Step 6.1: Navigate to Students Page
1. Click "Students" in main navigation menu
2. **Expected URL**: `/students/`
3. **Expected Screen**:
   ```
   STUDENT MANAGEMENT
   [Search Box] [Filters] [Create Student]
   
   Students List (Empty initially):
   Roll No | Name | Class | Father Name | Status | Actions
   ```

### Step 6.2: Create Student 1 - Grade 1A
**Detailed Form Filling:**

1. Click "Create Student" button
2. **URL**: `/students/create/`
3. **Form appears with these fields**:

   **Field 1: First Name**
   - Label: "First Name *"
   - Type: Text input
   - Value: `Arun`
   - **Action**: Click field, type "Arun"

   **Field 2: Last Name**
   - Label: "Last Name *"
   - Type: Text input
   - Value: `Kumar`
   - **Action**: Click field, type "Kumar"

   **Field 3: Email** (Optional)
   - Type: Email input
   - Value: `arun.kumar@example.com`
   - **Action**: Click field, type email

   **Field 4: Date of Birth**
   - Label: "Date of Birth"
   - Type: Date picker
   - Value: `15/06/2019` (Age ~7 years, appropriate for Grade 1)
   - **Action**: Click date picker, navigate to June 2019, select 15th

   **Field 5: Phone Number** (Optional)
   - Type: Text input
   - Value: `9876543210`
   - **Action**: Click field, type

   **Field 6: Class**
   - Label: "Class *"
   - Type: Dropdown
   - Value: Select `Grade 1A (2026)`
   - **Action**: Click dropdown, scroll, select "Grade 1A (2026)"
   - Verify: "Grade 1A (2026)" appears in field

   **Field 7: Roll Number** (Optional)
   - Type: Number input
   - Value: `1`
   - **Action**: Click field, type "1"

   **Field 8: Father's Name**
   - Type: Text input
   - Value: `Rajesh Kumar`
   - **Action**: Click field, type

   **Field 9: Mother's Name**
   - Type: Text input
   - Value: `Priya Kumar`
   - **Action**: Click field, type

   **Field 10: Father's Phone**
   - Type: Text input
   - Value: `9876543200`
   - **Action**: Click field, type

   **Field 11: Father's Occupation** (Optional)
   - Type: Text input
   - Value: `Engineer`
   - **Action**: Click field, type

   **Field 12: Address** (Optional)
   - Type: Text area
   - Value: `123 Main Street, City`
   - **Action**: Click field, type

4. **Click "Save Student"**
5. **Expected Results**:
   - Success message: "Student Arun Kumar created successfully"
   - Redirected to student detail page
   - Shows:
     ```
     Arun Kumar
     Roll: 1
     Class: Grade 1A (2026)
     DOB: 15/06/2019
     Father: Rajesh Kumar
     Status: Active
     Outstanding Fee: 120.00 (from First Term)
     [Edit] [Delete] [Transfer] [Pay Fee]
     ```

### Step 6.3: Create Students 2-3 for Grade 1A
**Student 2: Deepak Singh**
```
Details:
- First Name: Deepak
- Last Name: Singh
- DOB: 20/07/2019
- Class: Grade 1A (2026)
- Roll Number: 2
- Father's Name: Vikram Singh
- Mother's Name: Anjali Singh
- Father's Phone: 9876543201
- Father's Occupation: Doctor
- Email: deepak.singh@example.com
- Phone: 9876543211
```

**Student 3: Maya Sharma**
```
Details:
- First Name: Maya
- Last Name: Sharma
- DOB: 10/08/2019
- Class: Grade 1A (2026)
- Roll Number: 3
- Father's Name: Arjun Sharma
- Mother's Name: Neha Sharma
- Father's Phone: 9876543202
- Father's Occupation: Lawyer
- Email: maya.sharma@example.com
- Phone: 9876543212
```

### Step 6.4: Create Students for Grade 1B (2 Students)
**Student 4: Ravi Patel**
```
Details:
- First Name: Ravi
- Last Name: Patel
- DOB: 05/05/2019
- Class: Grade 1B (2026)
- Roll Number: 1
- Father's Name: Hardik Patel
- Mother's Name: Sneha Patel
- Father's Phone: 9876543203
- Father's Occupation: Businessman
- Email: ravi.patel@example.com
- Phone: 9876543213
```

**Student 5: Priya Desai**
```
Details:
- First Name: Priya
- Last Name: Desai
- DOB: 12/09/2019
- Class: Grade 1B (2026)
- Roll Number: 2
- Father's Name: Rohit Desai
- Mother's Name: Pooja Desai
- Father's Phone: 9876543204
- Father's Occupation: Accountant
- Email: priya.desai@example.com
- Phone: 9876543214
```

### Step 6.5: Create Students for Grade 2A (3 Students)
**Student 6: Arjun Gupta**
```
Details:
- First Name: Arjun
- Last Name: Gupta
- DOB: 22/03/2018
- Class: Grade 2A (2026)
- Roll Number: 1
- Father's Name: Amit Gupta
- Mother's Name: Shreya Gupta
- Father's Phone: 9876543205
- Father's Occupation: Engineer
- Email: arjun.gupta@example.com
- Phone: 9876543215
```

**Student 7: Kavya Nair**
```
Details:
- First Name: Kavya
- Last Name: Nair
- DOB: 18/04/2018
- Class: Grade 2A (2026)
- Roll Number: 2
- Father's Name: Suresh Nair
- Mother's Name: Divya Nair
- Father's Phone: 9876543206
- Father's Occupation: Teacher
- Email: kavya.nair@example.com
- Phone: 9876543216
```

**Student 8: Nikhil Verma**
```
Details:
- First Name: Nikhil
- Last Name: Verma
- DOB: 30/06/2018
- Class: Grade 2A (2026)
- Roll Number: 3
- Father's Name: Ashish Verma
- Mother's Name: Isha Verma
- Father's Phone: 9876543207
- Father's Occupation: Consultant
- Email: nikhil.verma@example.com
- Phone: 9876543217
```

### Step 6.6: Create Students for Grade 2B (2 Students)
**Student 9: Isha Reddy**
```
Details:
- First Name: Isha
- Last Name: Reddy
- DOB: 25/02/2018
- Class: Grade 2B (2026)
- Roll Number: 1
- Father's Name: Sunil Reddy
- Mother's Name: Geeta Reddy
- Father's Phone: 9876543208
- Father's Occupation: Businessman
- Email: isha.reddy@example.com
- Phone: 9876543218
```

**Student 10: Rohan Joshi**
```
Details:
- First Name: Rohan
- Last Name: Joshi
- DOB: 11/01/2018
- Class: Grade 2B (2026)
- Roll Number: 2
- Father's Name: Rajesh Joshi
- Mother's Name: Meera Joshi
- Father's Phone: 9876543209
- Father's Occupation: Doctor
- Email: rohan.joshi@example.com
- Phone: 9876543219
```

### Step 6.7: Create Students for Grade 3A (2 Students)
**Student 11: Aditi Malhotra**
```
Details:
- First Name: Aditi
- Last Name: Malhotra
- DOB: 08/11/2017
- Class: Grade 3A (2026)
- Roll Number: 1
- Father's Name: Vikram Malhotra
- Mother's Name: Shalini Malhotra
- Father's Phone: 9876543210
- Father's Occupation: Lawyer
- Email: aditi.malhotra@example.com
- Phone: 9876543220
```

**Student 12: Akshay Rao**
```
Details:
- First Name: Akshay
- Last Name: Rao
- DOB: 19/12/2017
- Class: Grade 3A (2026)
- Roll Number: 2
- Father's Name: Mohan Rao
- Mother's Name: Lakshmi Rao
- Father's Phone: 9876543211
- Father's Occupation: Engineer
- Email: akshay.rao@example.com
- Phone: 9876543221
```

### Step 6.8: Verify All 12 Students Created
1. Go to Students page
2. **Verify display shows all students**:
   ```
   Grade 1A:
   - Arun Kumar (Roll 1)
   - Deepak Singh (Roll 2)
   - Maya Sharma (Roll 3)
   
   Grade 1B:
   - Ravi Patel (Roll 1)
   - Priya Desai (Roll 2)
   
   Grade 2A:
   - Arjun Gupta (Roll 1)
   - Kavya Nair (Roll 2)
   - Nikhil Verma (Roll 3)
   
   Grade 2B:
   - Isha Reddy (Roll 1)
   - Rohan Joshi (Roll 2)
   
   Grade 3A:
   - Aditi Malhotra (Roll 1)
   - Akshay Rao (Roll 2)
   ```

3. Count verification:
   - Total should show "12 Students"
   - Grade 1A: 3 students
   - Grade 1B: 2 students
   - Grade 2A: 3 students
   - Grade 2B: 2 students
   - Grade 3A: 2 students

4. Status verification:
   - All should show "Active"
   - All should show "Outstanding: 120.00" (from First Term fee)

---

## SECTION 7: SYSTEM VERIFICATION & DASHBOARD CHECK

### Step 7.1: Navigate to Dashboard
1. Click "Dashboard" in navigation menu
2. **Expected URL**: `/dashboard/`
3. **Expected Screen** with statistics:

### Step 7.2: Verify Statistics
1. **Expected Dashboard Display**:
   ```
   DASHBOARD - SCHOOL MANAGEMENT SYSTEM
   
   Quick Statistics:
   ┌─────────────────────────────────┐
   │ Total Students: 12              │
   │ Active Students: 12             │
   │ Total Classes: 5                │
   │ Total Teachers: 5               │
   │ Assigned Teachers: 5            │
   └─────────────────────────────────┘
   
   Fee Collection:
   ┌─────────────────────────────────┐
   │ Current Term: First Term 2026    │
   │ Term Fee: 120.00                 │
   │ Total Fee: 1440.00               │  (12 students × 120)
   │ Collected: 0.00                  │
   │ Outstanding: 1440.00             │
   └─────────────────────────────────┘
   
   Top Arrears:
   [All students should show 120.00 outstanding]
   ```

2. **Manual Calculation Verify**:
   - Total Students: 12 ✓
   - Total Classes: 5 ✓
   - Total Teachers: 5 ✓
   - Each assigned to one class ✓
   - Each student owes 120.00 ✓
   - Total outstanding: 12 × 120 = 1440.00 ✓

### Step 7.3: Verify Classes Page
1. Click "Classes" menu
2. **Expected to see 5 classes with student counts**:
   ```
   Grade 1A (2026) - John Smith - 3 Students
   Grade 1B (2026) - Jane Wilson - 2 Students
   Grade 2A (2026) - Michael Brown - 3 Students
   Grade 2B (2026) - Sarah Davis - 2 Students
   Grade 3A (2026) - Robert Taylor - 2 Students
   ```

3. Total student count should be 12

### Step 7.4: Verify Teachers Page
1. Click "Teachers" menu
2. **Expected to see 5 teachers with assignments**:
   ```
   John Smith - Mathematics - Grade 1A (2026)
   Jane Wilson - English - Grade 1B (2026)
   Michael Brown - Science - Grade 2A (2026)
   Sarah Davis - History - Grade 2B (2026)
   Robert Taylor - Physical Education - Grade 3A (2026)
   ```

4. Each should show "Active" status
5. Each should show their assigned class

---

## SECTION 8: PAYMENT RECORDING (PARTIAL PAYMENTS)

### Step 8.1: Navigate to Student for Payment
1. Go to Students page
2. Click on first student: "Arun Kumar"
3. **Expected to see**:
   ```
   Student: Arun Kumar
   Class: Grade 1A (2026)
   Outstanding: 120.00
   [Pay Fee] [Edit] [Delete]
   ```

### Step 8.2: Record Partial Payment for Arun Kumar
1. Click "Pay Fee" button
2. **Payment form appears**:
   ```
   Payment Form
   
   Student: Arun Kumar
   Class: Grade 1A (2026)
   Current Outstanding: 120.00
   
   Payment Details:
   - Payment Date: [today's date auto-filled]
   - Amount Paid: [________] (required)
   - Payment Method: [Dropdown: Cash/Check/Online]
   - Reference Number: [________] (optional)
   - Description: [________] (optional)
   ```

3. **Fill in payment**:
   - Amount Paid: `80.00` (Partial payment)
   - Payment Method: Select "Cash"
   - Reference: `PAY001`

4. Click "Record Payment"
5. **Expected Results**:
   - Success message: "Payment recorded successfully"
   - Student page updates:
     ```
     Outstanding: 40.00  (was 120.00 - 80.00 paid)
     ```

### Step 8.3: Record Full Payment for Deepak Singh
1. Go to Students → Deepak Singh
2. Click "Pay Fee"
3. **Fill payment**:
   - Amount Paid: `120.00` (Full payment)
   - Payment Method: "Cash"
   - Reference: `PAY002`
4. Click "Record Payment"
5. **Expected**:
   - Outstanding: 0.00 ✓ (Fully paid)

### Step 8.4: Record Payment for Maya Sharma
1. Go to Students → Maya Sharma
2. Click "Pay Fee"
3. **Fill payment**:
   - Amount Paid: `60.00` (Partial)
   - Payment Method: "Cash"
   - Reference: `PAY003`
4. Click "Record Payment"
5. **Expected**:
   - Outstanding: 60.00 (120 - 60)

### Step 8.5: Record Payment for Ravi Patel
1. Go to Students → Ravi Patel
2. Click "Pay Fee"
3. **Fill payment**:
   - Amount Paid: `120.00` (Full)
   - Payment Method: "Cash"
   - Reference: `PAY004`
4. Click "Record Payment"
5. **Expected**:
   - Outstanding: 0.00

### Step 8.6: Verify Payment Summary
1. Return to Dashboard
2. **Verify updated statistics**:
   ```
   Fee Collection Summary:
   - Total Fee: 1440.00 (12 students × 120)
   - Collected: 320.00 (80+120+60+120, rounded)
   - Outstanding: 1120.00 (remaining)
   - Collection Rate: 22.22%
   ```

3. **Students with Outstanding**:
   - Arun Kumar: 40.00
   - Maya Sharma: 60.00
   - Priya Desai: 120.00
   - Arjun Gupta: 120.00
   - Kavya Nair: 120.00
   - Nikhil Verma: 120.00
   - Isha Reddy: 120.00
   - Rohan Joshi: 120.00
   - Aditi Malhotra: 120.00
   - Akshay Rao: 120.00
   
   **Total: 1120.00 Outstanding** ✓

4. **Fully Paid Students**:
   - Deepak Singh: 0.00 ✓
   - Ravi Patel: 0.00 ✓

---

## SECTION 9: TERM TRANSITION & ARREARS CALCULATION

### Step 9.1: Understand Arrears System
**Important Concept:**
- When a student doesn't pay full fee in Term 1, that unpaid amount becomes "Arrears"
- In Term 2, student owes: New Term Fee + Previous Arrears
- System should calculate this automatically

### Step 9.2: Navigate to Term Management
1. Go to Settings → Academic Terms
2. **Current term should be**: First Term 2026
3. **Verify all 3 terms exist**:
   - First Term 2026 (Current) - Status: CURRENT ✓
   - Second Term 2026 - Status: Inactive
   - Third Term 2026 - Status: Inactive

### Step 9.3: Set Current Term to Second Term
1. Find "Second Term 2026" in terms list
2. Click "Make Current" or "Set as Active" button
3. **Expected Results**:
   - Success message: "Second Term 2026 is now active"
   - First Term 2026 changes to "Previous"
   - Second Term 2026 shows as "Current"

### Step 9.4: Verify Arrears Auto-Calculation
1. Go to Dashboard
2. **Verify fee calculations updated**:
   ```
   Current Term: Second Term 2026
   Term Fee: 120.00
   
   For student Arun Kumar (who paid 80.00 in Term 1):
   - Term 1 Arrears: 40.00 (unpaid)
   - Current Term Fee: 120.00
   - Total Outstanding: 160.00 ✓
   ```

3. Go to Students → Arun Kumar
4. **Verify detail page shows**:
   ```
   Outstanding Fee: 160.00
   
   Breakdown (if visible):
   - Previous Arrears: 40.00
   - Current Term Fee: 120.00
   - Total: 160.00
   ```

### Step 9.5: Verify Arrears for Other Students
**For Deepak Singh (paid full 120 in Term 1)**:
- Previous Arrears: 0.00
- Current Term Fee: 120.00
- Outstanding: 120.00 ✓

**For Maya Sharma (paid 60 in Term 1)**:
- Previous Arrears: 60.00 (unpaid from Term 1)
- Current Term Fee: 120.00
- Outstanding: 180.00 ✓

**Verification Method**:
1. Go to each student detail page
2. Check the Outstanding Fee field
3. Verify it matches calculation

### Step 9.6: Record Payment in Term 2
1. Go to Students → Arun Kumar
2. Click "Pay Fee"
3. **Fill payment**:
   - Amount Paid: `100.00` (Partial - covers part of arrears and current term)
   - Payment Method: "Cash"
   - Reference: `TERM2_PAY001`
4. Click "Record Payment"
5. **Expected**:
   - Outstanding reduces from 160.00 to 60.00
   - Student still owes 60.00 (40 from Term 2 fee + 20 arrears unpaid)

---

## SECTION 10: STUDENT MOVEMENT & TRANSFERS

### Step 10.1: Navigate to Student Transfer
1. Go to Students → Select any student (e.g., "Arun Kumar")
2. Look for "Transfer" button or option
3. **Expected to see**: Transfer Student option

### Step 10.2: Transfer Student to Another Class (Optional)
1. Click "Transfer" on any student
2. **Transfer form appears**:
   ```
   Transfer Student: Arun Kumar
   
   Current Class: Grade 1A (2026)
   New Class: [Dropdown - select another]
   Transfer Date: [Date picker]
   Reason: [Optional text]
   ```

3. **Select new class**: Grade 1B (2026)
4. **Select date**: Today's date
5. Click "Transfer"
6. **Expected Results**:
   - Student moves to new class
   - Old class student count decreases
   - New class student count increases
   - Dashboard updates to show new class distribution

### Step 10.3: Verify Transfer
1. Go to Classes → Grade 1A
2. **Verify Arun Kumar no longer shows**
3. Go to Classes → Grade 1B
4. **Verify Arun Kumar now shows in this class**

---

## SECTION 11: FEE DASHBOARD & REPORTS

### Step 11.1: Navigate to Fee Dashboard
1. Click "Finance" or "Payments" in main menu
2. Look for "Fee Dashboard" or "Payment Report"
3. **Expected URL**: `/fee-dashboard/` or similar

### Step 11.2: Verify Dashboard Display
**Expected to see**:
```
FEE COLLECTION DASHBOARD

Summary Statistics:
- Total Students: 12
- Total Fees: 1440.00 (for current term)
- Collected: [Amount collected so far]
- Outstanding: [Remaining amount]
- Collection %: [Percentage]

Class-wise Breakdown:
┌─────────────────────────────────────┐
│ Class      │ Students │ Fee  │ Paid │
├─────────────────────────────────────┤
│ Grade 1A   │ 3        │ 360  │ ??   │
│ Grade 1B   │ 2        │ 240  │ ??   │
│ Grade 2A   │ 3        │ 360  │ ??   │
│ Grade 2B   │ 2        │ 240  │ ??   │
│ Grade 3A   │ 2        │ 240  │ ??   │
└─────────────────────────────────────┘

Student-wise Details:
[List showing each student with status]
```

### Step 11.3: Filter by Class
1. Look for filter options
2. Select "Grade 1A"
3. **Expected**: Display updates to show only Grade 1A students
4. Verify it shows 3 students for that class

### Step 11.4: Filter by Status
1. Look for "Status" filter
2. Select "Outstanding" or "Unpaid"
3. **Expected**: Shows only students with outstanding fees
4. Count should match your manual tally

---

## SECTION 12: SEARCH & FILTERING

### Step 12.1: Search Students
1. Go to Students page
2. Find search box (usually at top)
3. **Test searches**:
   - Type: "Arun" → Should show "Arun Kumar"
   - Type: "kumar" → Should show all Kumars
   - Type: "1234" → Should search by phone/ID

4. **Verify results update dynamically**

### Step 12.2: Filter Students by Class
1. On Students page, find filter options
2. Select "Class" filter
3. Choose "Grade 1A"
4. **Expected**: Shows only Grade 1A students (3 students)

### Step 12.3: Filter by Status
1. Find "Status" filter
2. Options should include:
   - Active
   - Inactive
   - All
3. Select "Active"
4. **Expected**: Shows only active students

---

## SECTION 13: ERROR HANDLING & EDGE CASES

### Step 13.1: Attempt Invalid Payment
1. Go to Students → Any student
2. Click "Pay Fee"
3. **Try to enter invalid amount**:
   - Amount: `-50` (negative)
   - Expected: Error message "Amount must be positive"

4. **Try to overpay**:
   - Amount: `5000` (more than owed)
   - Expected: Warning or success with note about overpayment

### Step 13.2: Attempt to Assign Teacher to Occupied Class
1. Go to Teachers → Any teacher (e.g., John Smith)
2. Attempt to assign to Grade 1B (already has Jane Wilson)
3. **Expected**: Error message "This class is already assigned to Jane Wilson"

### Step 13.3: Attempt to Delete Teacher with Active Assignment
1. Go to Teachers → John Smith (who is assigned to Grade 1A)
2. Click "Delete"
3. **Expected**: Either error OR automatic unassignment

---

## SECTION 14: DATA EXPORT & REPORTING

### Step 14.1: Export Student List
1. Go to Students page
2. Look for "Export" button or menu
3. **Options should include**:
   - Export as CSV
   - Export as PDF
   - Export as Excel
4. Click "Export as CSV"
5. **Expected**: File downloads to your computer

### Step 14.2: Verify Exported Data
1. Open downloaded file
2. **Should contain columns**:
   - Name
   - Class
   - Roll Number
   - Father Name
   - Outstanding Fee
   - Status

3. **Should have 12 rows** of student data

---

## SECTION 15: CLEANUP & FINAL VERIFICATION

### Step 15.1: Final Dashboard Check
1. Go to Dashboard
2. **Verify all statistics correct**:
   ```
   ✓ Total Students: 12
   ✓ Total Classes: 5
   ✓ Total Teachers: 5
   ✓ Academic Year: 2026
   ✓ Current Term: Second Term 2026
   ✓ Total Outstanding: ~1120.00 (depends on payments)
   ```

### Step 15.2: Verify Data Integrity
1. **Run through each section**:
   - [ ] All 12 students exist
   - [ ] All 5 classes created
   - [ ] All 5 teachers assigned
   - [ ] Payments recorded correctly
   - [ ] Arrears calculated properly
   - [ ] Term transition worked

### Step 15.3: Final System Check
1. **Test all navigation links work**:
   - Dashboard → loads
   - Classes → shows 5 classes
   - Teachers → shows 5 teachers with assignments
   - Students → shows 12 students
   - Settings → loads school details
   - Finance → shows fee dashboard

2. **Test all buttons work**:
   - Create buttons → forms appear
   - Edit buttons → edit pages open
   - Delete buttons → confirmations appear
   - Pay Fee → payment forms open
   - Logout → redirects to login

### Step 15.4: Documentation Complete
✓ **Testing Complete!**

You have successfully:
1. Set up school details
2. Created academic year 2026
3. Created 3 academic terms
4. Created 5 classes across 3 grades
5. Created 5 teachers and assigned each to a class
6. Created 12 students distributed across 4 classes
7. Recorded partial payments for some students
8. Transitioned terms and verified arrears calculation
9. Verified all system dashboards and reports
10. Tested search, filtering, and exports

**System is ready for production testing!**

---

## QUICK NAVIGATION CHECKLIST SO FAR

- [ ] Phase 0: School Details Setup Complete
  - [ ] School name set: "Green Valley International School"
  - [ ] Contact info filled
  - [ ] Colors configured
  - [ ] School name visible in header
  
- [ ] Section 1: Login & Auth Complete
  - [ ] Can login successfully
  - [ ] Dashboard accessible
  - [ ] Can access all menu items
  
- [ ] Section 2: Academic Year Complete
  - [ ] Year 2026 created
  - [ ] Year 2026 activated
  - [ ] Dashboard shows "Active Year: 2026"
  
- [ ] Section 3: Terms Complete
  - [ ] First Term 2026 created & marked CURRENT
  - [ ] Second Term 2026 created
  - [ ] Third Term 2026 created
  - [ ] All show fee: 120.00
  - [ ] Dashboard shows "Current Term: First Term 2026"
  
- [ ] Section 4: Classes Complete
  - [ ] 5 classes created (1A, 1B, 2A, 2B, 3A)
  - [ ] All showing 0 students
  - [ ] All in 2026 year
  
- [ ] Section 5: Teachers Complete
  - [ ] 5 teachers created
  - [ ] All teachers assigned to classes
  - [ ] Each class has one teacher
  - [ ] Teacher page shows all assignments

---

## IMPORTANT SYSTEM FORMULAS

**Fee Calculation:**
- Each student pays: Fee (default from term) = 120.00

**Outstanding Balance:**
```
Outstanding = Fee + Previous Arrears - Paid Payments
```

**Examples:**
1. New student, full payment:
   - Fee: 120.00
   - Paid: 120.00
   - Outstanding: 120 + 0 - 120 = 0.00 ✓

2. New student, partial payment:
   - Fee: 120.00
   - Paid: 80.00
   - Outstanding: 120 + 0 - 80 = 40.00 ✓

3. Unpaid from term 1, enters term 2:
   - Fee: 120.00
   - Arrears: 120.00 (from Term 1)
   - Paid: 0.00
   - Outstanding: 120 + 120 - 0 = 240.00 ✓

4. Paid arrears in term 2:
   - Fee: 120.00
   - Arrears: 120.00 (from Term 1)
   - Paid: 240.00 (covers both)
   - Outstanding: 120 + 120 - 240 = 0.00 ✓

---

## CONTINUE WITH DETAILED_TESTING_FLOW.md

After completing this part (Sections 0-5), continue with **DETAILED_TESTING_FLOW.md** which covers:
- Section 6: Student Creation (detailed with all 12 students)
- Section 7-15: Full testing flow

