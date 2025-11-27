# COMPLETE SYSTEM FLOW - A to Z TESTING GUIDE

## Phase 1: Initial Setup
### 1.1 Login
- Navigate to: `http://127.0.0.1:8000/login/`
- Login with your admin credentials
- **Expected**: Redirects to `/dashboard/`

### 1.2 Access Admin Dashboard
- Should show: Admin Dashboard with menu options
- Visible menu items:
  - Academic Management
  - Classes
  - Teachers
  - Students
  - Payments & Fees
  - Settings

---

## Phase 2: Academic Structure Setup
### 2.1 Create Academic Year
**Path**: Settings → Academic Management → Academic Years
- Click "Create Academic Year"
- **Form Fields**:
  - Year: `2026`
  - Description: "Academic Year 2026"
  - Start Date: `2026-01-01`
  - End Date: `2026-12-31`
- **Expected Result**: 
  - Success message
  - Year appears in list
  - Can set as active year

### 2.2 Activate Academic Year
- Click "Set as Active" on 2026
- **Expected Result**: 
  - Status changes to "Active"
  - This year is now the system's current working year

### 2.3 Create Academic Terms
**Path**: Settings → Academic Management → Active Terms
- Create three terms for 2026:
  1. **First Term 2026**
     - Start: 2026-01-15
     - End: 2026-04-15
     - Default Fee: 120.00
  
  2. **Second Term 2026**
     - Start: 2026-05-01
     - End: 2026-08-15
     - Default Fee: 120.00
  
  3. **Third Term 2026**
     - Start: 2026-09-01
     - End: 2026-12-15
     - Default Fee: 120.00

- **Expected Result**: All three terms visible in Active Terms list

### 2.4 Set Current Term
- Click "Set as Current" on First Term 2026
- **Expected Result**: 
  - First Term 2026 marked as current
  - System uses this for all operations

---

## Phase 3: Classes Setup
### 3.1 Create Classes
**Path**: `/classes/`
- Click "Create Class" button
- **Form Fields**:
  - Grade: `1` (First time)
  - Section: `A`
  - Academic Year: `2026` (auto-filled)
  - Teacher: Leave blank (will assign later)
  - Click "Create Class"

- **Repeat for**:
  - Grade 1, Section B
  - Grade 2, Section A
  - Grade 2, Section B
  - Grade 3, Section A

- **Expected Result**: 
  - All 5 classes visible in Classes list
  - Each shows Grade, Section, Year

---

## Phase 4: Teachers Setup
### 4.1 Create Teachers
**Path**: `/teachers/`
- Click "Create Teacher"
- **Form Fields** (Create 5 teachers):
  1. **John Smith**
     - Email: john.smith@school.com
     - Phone: 1234567890
     - Specialization: Mathematics
     - Qualification: B.Ed
  
  2. **Jane Wilson**
     - Email: jane.wilson@school.com
     - Phone: 1234567891
     - Specialization: English
     - Qualification: M.A
  
  3. **Michael Brown**
     - Email: michael.brown@school.com
     - Phone: 1234567892
     - Specialization: Science
     - Qualification: B.Sc
  
  4. **Sarah Davis**
     - Email: sarah.davis@school.com
     - Phone: 1234567893
     - Specialization: History
     - Qualification: B.A
  
  5. **Robert Taylor**
     - Email: robert.taylor@school.com
     - Phone: 1234567894
     - Specialization: Physical Education
     - Qualification: B.Ed

- **Expected Result**: All teachers visible in Teachers list

### 4.2 Assign Teachers to Classes
**Path**: `/teachers/` → Click teacher → "Assign Class"
- Assign each teacher to one class:
  - John Smith → Grade 1, Section A
  - Jane Wilson → Grade 1, Section B
  - Michael Brown → Grade 2, Section A
  - Sarah Davis → Grade 2, Section B
  - Robert Taylor → Grade 3, Section A

- **Expected Result**: 
  - Teacher shows "Assigned to [Class Name]"
  - Cannot assign same teacher to multiple classes in same year

---

## Phase 5: Students Setup
### 5.1 Create Students
**Path**: `/students/`
- Click "Create Student"
- **Form Fields** (Create 12 students - 3 per class):
  
  **Grade 1, Section A** (John Smith's class):
  1. Aisha Ahmed
     - Roll: 001
     - DOB: 2015-03-15
     - Parent: Ahmed Ali
     - Phone: 9876543210
  
  2. Bilal Hassan
     - Roll: 002
     - DOB: 2015-04-20
     - Parent: Hassan Mohammed
     - Phone: 9876543211
  
  3. Clara Singh
     - Roll: 003
     - DOB: 2015-05-10
     - Parent: Singh Rajesh
     - Phone: 9876543212

  **Grade 1, Section B** (Jane Wilson's class):
  4. David Lee
     - Roll: 001
     - DOB: 2015-06-15
     - Parent: Lee Chen
     - Phone: 9876543213
  
  5. Emma Johnson
     - Roll: 002
     - DOB: 2015-07-20
     - Parent: Johnson Mark
     - Phone: 9876543214
  
  6. Fatima Khan
     - Roll: 003
     - DOB: 2015-08-10
     - Parent: Khan Malik
     - Phone: 9876543215

  **Grade 2, Section A** (Michael Brown's class):
  7. Grace Martinez
     - Roll: 001
     - DOB: 2014-09-15
     - Parent: Martinez Juan
     - Phone: 9876543216
  
  8. Henry Patel
     - Roll: 002
     - DOB: 2014-10-20
     - Parent: Patel Vijay
     - Phone: 9876543217
  
  9. Iris Thompson
     - Roll: 003
     - DOB: 2014-11-10
     - Parent: Thompson Robert
     - Phone: 9876543218

  **Grade 2, Section B** (Sarah Davis's class):
  10. Jack Wilson
      - Roll: 001
      - DOB: 2014-12-15
      - Parent: Wilson George
      - Phone: 9876543219
  
  11. Karen White
      - Roll: 002
      - DOB: 2015-01-20
      - Parent: White Paul
      - Phone: 9876543220
  
  12. Leo Garcia
      - Roll: 003
      - DOB: 2015-02-10
      - Parent: Garcia Carlos
      - Phone: 9876543221

- **Expected Result**: 
  - All students appear in respective class lists
  - Each student assigned to correct class
  - Status shows "Active"

---

## Phase 6: Fee Management & Payments
### 6.1 Verify Term Fees
**Path**: `/fees/`
- **Expected**: Show all classes with students and fee information
- Each student should have:
  - Fee: 120.00 (current term)
  - Outstanding: 120.00 (new students)
  - Arrears: 0.00 (new students)

### 6.2 Record Payments
**Path**: `/payments/create/`
- **Create Payment 1 (Aisha Ahmed - Full Payment)**:
  - Student: Aisha Ahmed
  - Amount: 120.00
  - Term: First Term 2026
  - Payment Date: 2026-02-01
  - Reference: REF001
  - Status: Completed
  - **Expected**: Outstanding = 0.00, Arrears = 0.00

- **Create Payment 2 (Bilal Hassan - Partial Payment)**:
  - Student: Bilal Hassan
  - Amount: 80.00
  - Term: First Term 2026
  - Payment Date: 2026-02-05
  - Reference: REF002
  - Status: Completed
  - **Expected**: Outstanding = 40.00, Arrears = 0.00

- **Create Payment 3 (Clara Singh - No Payment)**:
  - Don't record any payment
  - **Expected**: Outstanding = 120.00, Arrears = 0.00

- **Create Payment 4 (David Lee - Full Payment)**:
  - Student: David Lee
  - Amount: 120.00
  - Term: First Term 2026
  - Payment Date: 2026-02-10
  - **Expected**: Outstanding = 0.00, Arrears = 0.00

- Repeat similar pattern for remaining students (some paid, some partial, some unpaid)

### 6.3 View Payment History
**Path**: Click on student → "Payment History"
- **Expected**: 
  - Shows all payments for student
  - Payment date, amount, reference visible
  - Status (Completed/Pending) shown
  - Can download payment history

### 6.4 View Fee Dashboard
**Path**: `/fees/`
- **Expected**: 
  - Overview of all students, fees, payments
  - Can filter by class
  - Can export as CSV
  - Shows totals: Total Students, Total Fee, Total Paid, Total Outstanding

---

## Phase 7: Student Movement
### 7.1 Promote Student
**Path**: Click student → "Move Student" or Use bulk promote
- **Scenario**: Promote all Grade 1 students to Grade 2
- **Expected Result**:
  - Student moved to new class
  - Status shows in Grade 2
  - Previous class is vacated
  - Record of movement in history

### 7.2 Demote Student
**Path**: Click student → "Move Student"
- **Scenario**: Demote one Grade 2 student back to Grade 1
- **Expected Result**:
  - Student moved back to Grade 1
  - Movement recorded
  - Can view history

### 7.3 Transfer Student
**Path**: Click student → "Transfer"
- **Scenario**: Move student to different section in same grade
- **Expected Result**:
  - Student moved to new section
  - Transfer recorded
  - Can view in new class

---

## Phase 8: Term Rollover
### 8.1 Create Next Term
**Path**: Settings → Create new term
- **Form**:
  - Term: "Second Term 2026"
  - Start: 2026-05-01
  - End: 2026-08-15
  - Default Fee: 120.00
- **Expected**: New term created and visible

### 8.2 Set as Current Term
- Click "Set as Current" on Second Term 2026
- **Expected**: System now uses Second Term

### 8.3 View Arrears Calculation
**Path**: `/fees/`
- **Expected for Bilal Hassan**:
  - Previous Arrears: 40.00 (from Term 1 - didn't pay full)
  - Current Fee: 120.00
  - Outstanding: 160.00 (120 + 40 carried forward)

### 8.4 Apply Arrears Payment
**Path**: `/payments/create/`
- **Payment for Bilal Hassan - Term 2**:
  - Amount: 160.00 (covers both current + arrears)
  - **Expected**: Outstanding = 0.00, Arrears = 0.00

---

## Phase 9: Reporting & Export
### 9.1 Export Fee Dashboard
**Path**: `/fees/` → "Export as CSV"
- **Expected**: CSV file downloads with columns:
  - Student Name
  - Class
  - Term
  - Fee
  - Paid
  - Outstanding
  - Arrears

### 9.2 Export Student Payment History
**Path**: Student Detail → Payments → "Export History"
- **Expected**: CSV with:
  - Payment Date
  - Amount
  - Reference
  - Status

### 9.3 Search & Filter
**Path**: Dashboard → Global Search
- **Scenarios**:
  - Search by student name: "Aisha"
  - Filter by class: "Grade 1, Section A"
  - Filter by status: "Unpaid"
- **Expected**: Correct results returned

---

## Phase 10: Administrative Functions
### 10.1 Create New Admin
**Path**: Settings → Admin Management (if available)
- Create new admin user with email and password
- **Expected**: New admin can login

### 10.2 Update Teacher
**Path**: Click teacher → Edit
- Change specialization or qualification
- **Expected**: Changes saved and visible

### 10.3 Delete Teacher (with validation)
**Path**: Click teacher → Delete
- **Scenario 1** (Teacher with class assigned):
  - **Expected**: Error message - cannot delete assigned teacher
  
- **Scenario 2** (Teacher with no class):
  - **Expected**: Teacher deleted successfully

### 10.4 Update Student
**Path**: Click student → Edit
- Update phone or parent name
- **Expected**: Changes saved

### 10.5 Delete Student
**Path**: Click student → Delete
- **Expected**: Student deleted (check for payments first)

---

## Phase 11: Error Handling & Edge Cases
### 11.1 Duplicate Prevention
- Try to create student with same roll in same class
- **Expected**: Error preventing duplicate

### 11.2 Validation Tests
- Create payment with negative amount
- **Expected**: Error - amount must be positive
  
- Try to create payment exceeding fee
- **Expected**: Either allow or warn about overpayment

### 11.3 Class Constraints
- Try to assign same teacher to 2 classes in same year
- **Expected**: Error preventing duplicate assignment

---

## Phase 12: System Verification
### 12.1 Check Dashboard Calculations
- Total Students: Should match count
- Total Fees: Sum of all fees
- Total Paid: Sum of all payments
- Total Outstanding: Should be correct

### 12.2 Verify Balance Calculations
- For each student: Outstanding = (Fee + Arrears) - Paid
- Arrears should carry forward to next term
- Balance should be non-negative

### 12.3 Check URL Patterns
- `/` → Login if not authenticated
- `/dashboard/` → Shows admin dashboard
- `/classes/` → Class list
- `/teachers/` → Teacher list
- `/students/` → Student list
- `/fees/` → Fee dashboard
- `/payments/` → Payment list
- `/settings/` → Settings

---

## Testing Checklist

- [ ] Phase 1: Login & Dashboard Access
- [ ] Phase 2: Academic Structure (Years, Terms)
- [ ] Phase 3: Classes Creation
- [ ] Phase 4: Teachers Setup & Assignment
- [ ] Phase 5: Students Creation & Assignment
- [ ] Phase 6: Fees & Payments
- [ ] Phase 7: Student Movement
- [ ] Phase 8: Term Rollover & Arrears
- [ ] Phase 9: Reporting & Export
- [ ] Phase 10: Admin Functions
- [ ] Phase 11: Error Handling
- [ ] Phase 12: System Verification

---

## Common Issues & Solutions

**Issue**: 405 Error on Create endpoints
- **Solution**: Use POST request with form data, not GET

**Issue**: NoReverseMatch errors
- **Solution**: Check URL patterns in urls.py and __init__.py are aligned

**Issue**: Missing balance calculations
- **Solution**: Ensure StudentBalance records are created automatically when payment is recorded

**Issue**: Students showing wrong class
- **Solution**: Verify current_class property filters by active year

---

## Quick Test Data Summary
- **Academic Year**: 2026 (Active)
- **Terms**: 3 (First, Second, Third - all 120.00 fee)
- **Current Term**: First Term 2026
- **Classes**: 5 (Grade 1 A, 1 B, 2 A, 2 B, 3 A)
- **Teachers**: 5 (one per class)
- **Students**: 12 (3 per class first 4 classes)
- **Total Initial Fees**: 12 × 120 = 1,440.00
