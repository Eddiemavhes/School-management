# Comprehensive Validation Analysis - Django School Management System

## Executive Summary
This document identifies all necessary validations for the school management system, organized by category. Each validation specifies what should be validated, when it should trigger, the appropriate error message, and affected components.

---

## 1. ACADEMIC TERM PROGRESSION VALIDATIONS

### 1.1 Term Sequentiality Validation
**What:** Cannot create a term that skips the sequence (e.g., can't create Term 3 if Term 1 & 2 don't exist)
**When:** When creating a new AcademicTerm
**Trigger Point:** AcademicTerm.clean() method
**Error Message:** "Cannot create {term_number}. Please create preceding terms first. Required: {missing_terms}"
**Model:** `AcademicTerm`
**Affected Views:** Admin term creation, term management

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add validation in AcademicTerm.clean()

---

### 1.2 Term Date Validation
**What:** 
- Start date must be before end date
- Term dates cannot overlap with other terms in same year
- Term dates must fall within academic year start/end dates

**When:** When creating or updating AcademicTerm
**Trigger Point:** AcademicTerm.clean() method
**Error Messages:**
- "End date must be after start date"
- "Term dates overlap with another term in {academic_year}"
- "Term dates must fall within academic year {academic_year} dates ({start} to {end})"
**Model:** `AcademicTerm`
**Affected Views:** Admin term creation/update

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Has basic date validation (start < end)
- **Missing:** Overlap checking with academic year, overlap with other terms

---

### 1.3 Current Term Exclusivity Validation
**What:** Only one term can be marked as current at any time
**When:** When setting is_current=True on any term
**Trigger Point:** AcademicTerm.clean() method
**Error Message:** "Another term is already set as current. Please deactivate it first."
**Model:** `AcademicTerm`

**Current Implementation:** ✅ IMPLEMENTED
- Automatically deactivates other current terms in clean()

---

### 1.4 Cannot Progress Before Previous Term Complete
**What:** Cannot set a term as current if the previous term has outstanding enrollments or unclosed financials
**When:** When attempting to activate a new term
**Trigger Point:** When marking term is_current=True
**Error Message:** "Cannot activate {term}. Previous term {previous_term} still has outstanding issues: {issues_list}"
**Issues to Check:**
- StudentBalance records with unpaid balances
- Students with arrears over a threshold (configurable)
- Unclosed StudentMovement operations

**Model:** `AcademicTerm`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add method check_term_readiness() in AcademicTerm

---

## 2. STUDENT MOVEMENT/PROMOTION/DEMOTION VALIDATIONS

### 2.1 Promotion Grade Validation
**What:**
- Cannot promote to same or lower grade
- Cannot promote to grade > 7
- Promoted class must exist in next academic year

**When:** When executing promotion via promote_student() or bulk_promote_students()
**Trigger Point:** StudentMovement.clean() or view validation
**Error Messages:**
- "Invalid promotion: New grade must be higher than current grade"
- "Cannot promote to grade {grade}. Maximum grade is 7"
- "No class available in grade {grade} for {academic_year}"
**Model:** `StudentMovement`
**Affected Views:** promote_student(), bulk_promote_students(), demote_student()

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Grade validation exists in promote_student()
- **Missing:** Validation for demote_student (should verify grade is lower), class existence check in new year, StudentMovement.clean() method

---

### 2.2 Demotion Grade Validation
**What:**
- Cannot demote to same or higher grade
- Cannot demote to grade < 1
- Demotion requires a reason

**When:** When executing demotion via demote_student()
**Trigger Point:** StudentMovement.clean() or view validation
**Error Messages:**
- "Invalid demotion: New grade must be lower than current grade"
- "Cannot demote to grade less than 1"
- "Reason is required for demotion"
**Model:** `StudentMovement`
**Affected Views:** demote_student()

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add validations in demote_student() and StudentMovement.clean()

---

### 2.3 Transfer Within Same Grade Validation
**What:**
- Can only transfer within same grade
- Can only transfer within same academic year
- Cannot transfer to the same class

**When:** When executing transfer via transfer_student()
**Trigger Point:** StudentMovement.clean() or view validation
**Error Messages:**
- "Invalid transfer: Must be within the same grade"
- "Invalid transfer: Must be within the same academic year"
- "Cannot transfer to the same class student is already in"
**Model:** `StudentMovement`
**Affected Views:** transfer_student()

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Same grade check exists
- **Missing:** Same-year check, same-class check

---

### 2.4 Student Movement Prerequisites
**What:**
- Student must be assigned to a class before any movement
- Student must be active (is_active=True)
- Cannot move a graduated student (status='GRADUATED')

**When:** When attempting any movement operation
**Trigger Point:** All movement views (promote, demote, transfer)
**Error Messages:**
- "Student {name} must be assigned to a class before {movement_type}"
- "Cannot move inactive student {name}"
- "Cannot move graduated student {name}"
**Models:** `Student`, `StudentMovement`

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Current class check exists
- **Missing:** Active status check, graduated status check

---

### 2.5 Arrears Preservation in Movement
**What:**
- Arrears must be properly recorded before movement
- Arrears must be preserved and carried to new term/balance

**When:** When creating StudentMovement record
**Trigger Point:** StudentMovement.save()
**Error Messages:**
- "Failed to capture student arrears before movement"
- "Arrears not properly preserved for student {name}"
**Model:** `StudentMovement`

**Current Implementation:** ✅ IMPLEMENTED
- Captures previous_arrears and preserved_arrears in save()

---

### 2.6 Bulk Movement Atomicity Validation
**What:**
- All students in bulk operation must meet movement criteria
- Partial failures must be logged but not rolled back
- Bulk operation record must track success/failure counts

**When:** When executing bulk_promote_students()
**Trigger Point:** bulk_promote_students() view
**Error Messages:**
- Per-student: "{student_name}: {specific_error}"
- Summary: "Bulk promotion completed: {success} successful, {failed} failed"
**Model:** `BulkMovement`

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Tracks successful/failed counts
- **Missing:** BulkMovement record creation, comprehensive validation per student

---

### 2.7 Graduation Validation
**What:**
- Graduation only occurs when promoting to grade 7
- After graduation, student becomes inactive
- Graduated students cannot be moved

**When:** When promoting to grade 7
**Trigger Point:** promote_student(), bulk_promote_students()
**Error Messages:**
- "Graduation automatically triggered for students promoted to Grade 7"
**Models:** `Student`, `StudentMovement`

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Sets is_active=False when promoting to grade 7
- **Missing:** Prevents movement of already-graduated students

---

## 3. PAYMENT AND FINANCIAL VALIDATIONS

### 3.1 Current Term Payment Validation
**What:**
- Payments can ONLY be recorded for the current academic term
- Cannot record payment for past or future terms

**When:** When creating a Payment record
**Trigger Point:** Payment.clean() method, PaymentCreateView.form_valid()
**Error Message:** "Payments can only be recorded for the current term"
**Model:** `Payment`
**Affected Views:** PaymentCreateView

**Current Implementation:** ✅ IMPLEMENTED

---

### 3.2 Payment Amount Validation (UPDATED)
**What:**
- Payment amount must be >= 0 (allows zero for adjustments)
- Amount CAN exceed total due (excess goes to next term)
- Cannot accept negative payments
- Excess payment automatically applied to next term as prepayment

**When:** When creating a Payment record
**Trigger Point:** Payment.clean() and _handle_excess_payment() methods
**Error Messages:**
- "Payment amount cannot be negative"
- ✅ Allows 0.00 (for adjustments/placeholders)
- ✅ Allows any amount >= total due (excess handled automatically)
**Model:** `Payment`

**Current Implementation:** ✅ IMPLEMENTED
- Validation updated to allow >= 0
- Excess payment logic implemented in _handle_excess_payment()
- Next term prepayment automatic and atomic

---

### 3.3 Student Payment Eligibility Validation
**What:**
- Only active students can have payments recorded
- Student must have a StudentBalance record for the term
- Cannot pay for inactive/graduated students

**When:** When creating a Payment record
**Trigger Point:** Payment._validate_student_eligibility() method
**Error Messages:**
- "Cannot record payment for inactive student {name}"
- "No balance record exists for {student} in {term}. Please initialize the balance first."
**Model:** `Payment`, `Student`, `StudentBalance`

**Current Implementation:** ✅ IMPLEMENTED
- Active status check enforced
- Balance record requirement enforced

---

### 3.4 Term Fee Existence Check
**What:**
- Term must have a TermFee configured before accepting payments
- Cannot accept payment for term without fee

**When:** When creating a Payment record
**Trigger Point:** Payment._validate_term_fee_exists() method
**Error Message:** "Term fee has not been set for {term}"
**Model:** `Payment`, `TermFee`

**Current Implementation:** ✅ IMPLEMENTED
- TermFee existence required for payment

---

### 3.5 Payment Reference Validation
**What:**
- Receipt number must be unique
- Payment reference number must be unique (if required)
- Cannot have duplicate receipts for same student/term

**When:** When creating a Payment record
**Trigger Point:** Payment.save() method
**Error Message:** "Receipt number {receipt_number} already exists"
**Model:** `Payment`

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Receipt number auto-generated with unique constraint
- **Missing:** Explicit validation check in clean()

---

### 3.4 Student Payment Eligibility
**What:**
- Student must be enrolled and active
- Student must have a valid StudentBalance record for current term
- Cannot pay for student with no current class assignment (optional based on business rules)

**When:** When attempting to record payment for student
**Trigger Point:** PaymentCreateView.form_valid()
**Error Messages:**
- "Student {name} is not active. Payment cannot be recorded."
- "Student {name} has no balance record for current term"
- "Student {name} must be assigned to a class"
**Model:** `Student`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add checks in PaymentCreateView.form_valid()

---

### 3.5 Term Fee Existence Validation
**What:**
- A TermFee must exist for the term before accepting payments
- Cannot process payments without known fee amount

**When:** When initializing StudentBalance or recording payment
**Trigger Point:** StudentBalance.initialize_term_balance(), PaymentCreateView
**Error Message:** "Term fee has not been set for this term. Please configure term fees first."
**Models:** `TermFee`, `Payment`

**Current Implementation:** ✅ IMPLEMENTED
- Checked in StudentBalance.initialize_term_balance()

---

## 4. TERM FEE AND ENROLLMENT REQUIREMENTS VALIDATIONS

### 4.1 Term Fee Due Date Validation
**What:**
- Due date must be after term start date
- Due date must be before term end date
- Cannot have multiple due dates per term

**When:** When creating or updating TermFee
**Trigger Point:** TermFee.clean() method
**Error Messages:**
- "Due date cannot be before term start date: {start_date}"
- "Due date must be before term end date: {end_date}"
- "A term fee already exists for {term}"
**Model:** `TermFee`

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Has check for due_date >= start_date
- **Missing:** Check for due_date <= end_date, unique_together enforcement in clean()

---

### 4.2 Term Fee Amount Validation
**What:**
- Fee amount must be > 0
- Fee amount cannot be negative
- Cannot modify term fee after first payment for that term

**When:** When creating or updating TermFee
**Trigger Point:** TermFee.clean() method
**Error Messages:**
- "Fee amount must be greater than zero"
- "Cannot modify term fee after payments have been recorded"
**Model:** `TermFee`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add validation in TermFee.clean()

---

### 4.3 Student Balance Initialization Validation
**What:**
- Previous arrears must be calculated correctly
- Previous arrears should only include immediately previous term balance
- Cannot double-count arrears across multiple terms

**When:** When initializing StudentBalance for a term
**Trigger Point:** StudentBalance.initialize_term_balance() classmethod
**Error Messages:**
- "Failed to calculate previous arrears for student"
- "Arrears calculation error: previous balance is negative"
**Model:** `StudentBalance`

**Current Implementation:** ✅ IMPLEMENTED
- Has calculate_arrears() classmethod that correctly handles immediate previous term only

---

### 4.4 Student Balance Uniqueness Validation
**What:**
- Can only have one balance record per student per term
- Prevent duplicate StudentBalance entries

**When:** When creating StudentBalance
**Trigger Point:** StudentBalance model Meta.unique_together and get_or_create()
**Error Message:** "Student balance record already exists for this term"
**Model:** `StudentBalance`

**Current Implementation:** ✅ IMPLEMENTED
- Enforced via unique_together in Meta

---

### 4.5 Enrollment Status Validation
**What:**
- Student must be enrolled before current term to be included in billing
- Cannot bill unenrolled students

**When:** When creating StudentBalance for a student
**Trigger Point:** StudentBalance.initialize_term_balance()
**Error Message:** "Student {name} is not enrolled. Check enrollment date: {enrollment_date}"
**Model:** `Student`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add enrollment date check in StudentBalance.initialize_term_balance()

---

## 5. CLASS ASSIGNMENTS AND CAPACITY VALIDATIONS

### 5.1 Teacher Assignment Exclusivity
**What:**
- A teacher can only teach one class per academic year
- Cannot assign same teacher to multiple classes in same year

**When:** When assigning teacher to Class
**Trigger Point:** Class.clean() method
**Error Message:** "Teacher {name} is already assigned to {class} in {academic_year}. A teacher can only teach one class per academic year."
**Model:** `Class`

**Current Implementation:** ✅ IMPLEMENTED
- Validation exists in Class.clean()

---

### 5.2 Class Uniqueness Validation
**What:**
- Cannot have duplicate grade+section+academic_year combinations
- Each class must be unique per year

**When:** When creating/updating Class
**Trigger Point:** Model Meta.unique_together and Class.clean()
**Error Message:** "Class Grade {grade}{section} already exists for {academic_year}"
**Model:** `Class`

**Current Implementation:** ✅ IMPLEMENTED
- Enforced via unique_together in Meta

---

### 5.3 Student Class Assignment Validation
**What:**
- Student can only be in one current class at a time
- Cannot have multiple current_class values simultaneously

**When:** When updating student.current_class
**Trigger Point:** Student.clean() method (if implemented)
**Error Message:** "Student is already assigned to a class. Transfer to new class first."
**Model:** `Student`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add validation in Student.clean()

---

### 5.4 Class Grade Level Validation
**What:**
- Grade must be between 1-7 (valid range)
- Cannot assign invalid grades

**When:** When creating/updating Class
**Trigger Point:** Class field validators
**Error Message:** "Grade must be between 1 and 7"
**Model:** `Class`

**Current Implementation:** ✅ IMPLEMENTED
- Field validators MinValueValidator(1), MaxValueValidator(7)

---

### 5.5 Class Section Validation
**What:**
- Section must be from valid choices (A, B, etc.)
- Cannot have arbitrary section names

**When:** When creating/updating Class
**Trigger Point:** Class field choices constraint
**Error Message:** "Section must be one of: {valid_sections}"
**Model:** `Class`

**Current Implementation:** ✅ IMPLEMENTED
- Field choices enforce valid sections

---

### 5.6 Academic Year Validity for Class
**What:**
- Class academic_year must reference an existing AcademicYear
- Class academic_year must be valid (not in future or too far in past)

**When:** When creating/updating Class
**Trigger Point:** Class.clean() method
**Error Message:** "Academic year {year} does not exist or is invalid"
**Model:** `Class`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add validation in Class.clean()

---

## 6. YEAR-END ROLLOVER CONSTRAINTS VALIDATIONS

### 6.1 Rollover Academic Year Validation
**What:**
- New academic year must not already exist
- New academic year year value must be exactly current + 1

**When:** When executing rollover_to_new_year()
**Trigger Point:** AcademicYear.rollover_to_new_year() method
**Error Messages:**
- "Academic year {new_year} already exists"
- "Invalid rollover: New year must be {expected_year}"
**Model:** `AcademicYear`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add checks in rollover_to_new_year()

---

### 6.2 Rollover Student Prerequisites
**What:**
- Can only rollover active students
- Cannot rollover students without class assignment
- Student arrears must be properly calculated before rollover

**When:** When executing student rollover as part of year-end
**Trigger Point:** AcademicYear.rollover_to_new_year()
**Error Messages:**
- "Cannot rollover inactive student {name}"
- "Student {name} has no class assignment and cannot be rolled over"
- "Failed to calculate arrears for student {name}"
**Model:** `Student`

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Checks for student.current_class existence
- **Missing:** Active status check, arrears validation

---

### 6.3 Target Class Existence Validation
**What:**
- Target class in new year must exist before promoting student
- If target class doesn't exist, system must not auto-create it (should fail with error)

**When:** When promoting student during rollover
**Trigger Point:** AcademicYear.rollover_to_new_year()
**Error Messages:**
- "No Grade {grade} class exists in {new_year} for student {name}"
- "Cannot complete rollover: Missing classes in new academic year"
**Model:** `Class`

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Tries to find existing class, logs warning if not found
- **Missing:** Should fail/block if target classes don't exist, not just log warning

---

### 6.4 Term Configuration Validation
**What:**
- New academic year must have all terms created
- New terms must have valid fee structure
- Cannot activate academic year without complete term setup

**When:** When completing year-end rollover
**Trigger Point:** AcademicYear.rollover_to_new_year() and activate()
**Error Messages:**
- "Academic year {year} is missing required terms"
- "Academic year {year} is missing term fees"
- "Cannot activate academic year without complete term structure"
**Model:** `AcademicYear`, `AcademicTerm`, `TermFee`

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Creates terms and fees
- **Missing:** Validation that all 3 terms exist, all have fees

---

### 6.5 Arrears Carryover Validation
**What:**
- Arrears from previous year first term must equal calculated totals
- Arrears must be positive (cannot be negative carryover)
- Cannot rollover with corrupted financial data

**When:** When creating StudentBalance for new year's first term
**Trigger Point:** AcademicYear.rollover_to_new_year()
**Error Messages:**
- "Arrears carryover validation failed for {student_name}: calculated {calc} vs carried {carried}"
- "Cannot rollover negative arrears"
- "Financial data corruption detected for student {name}"
**Model:** `StudentBalance`

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Creates balance with calculated arrears
- **Missing:** Explicit validation that arrears are non-negative and match calculations

---

## 7. STUDENT STATUS TRANSITIONS VALIDATIONS

### 7.1 Student Status Transitions
**What:**
- Valid transitions: ENROLLED → ACTIVE → GRADUATED
- Cannot skip status levels
- Cannot reverse transitions
- Cannot transition to invalid status values

**When:** When changing student status/is_active flag
**Trigger Point:** Student.clean() method
**Error Messages:**
- "Cannot transition from {current_status} to {new_status}"
- "Invalid student status: {status}"
- "Status transitions are forward-only"
**Model:** `Student`

**Current Implementation:** ❌ PARTIALLY IMPLEMENTED
- Uses is_active boolean (not full status enum)
- **Missing:** Formal status enum, transition validation

---

### 7.2 Deactivation Prerequisites
**What:**
- Can only deactivate graduated students or expelled students
- Cannot deactivate active students with outstanding payments (optional business rule)
- Must record reason for deactivation

**When:** When setting student.is_active = False
**Trigger Point:** Student.clean() method
**Error Messages:**
- "Cannot deactivate active enrolled student without graduation"
- "Student {name} has outstanding arrears: {amount}. Resolve before deactivation."
**Model:** `Student`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add deactivation validation in Student.clean()

---

### 7.3 Reactivation Constraints
**What:**
- Cannot reactivate graduated students
- Can only reactivate if all financial obligations are cleared (optional)

**When:** When setting student.is_active = True after deactivation
**Trigger Point:** Student.clean() method
**Error Messages:**
- "Cannot reactivate graduated student"
- "Cannot reactivate student with outstanding arrears"
**Model:** `Student`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add reactivation validation in Student.clean()

---

### 7.4 Date of Birth Age Validation
**What:**
- Student age must be reasonable (e.g., 4-25 years)
- Date of birth cannot be in future
- Cannot create overly young or overly old students

**When:** When creating/updating Student
**Trigger Point:** Student.clean() method
**Error Messages:**
- "Student date of birth cannot be in the future"
- "Student age must be between 4 and 25 years"
**Model:** `Student`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add DOB validation in Student.clean()

---

### 7.5 Enrollment Date Validation
**What:**
- Enrollment date cannot be in future
- Enrollment date cannot be before school founding year
- Enrollment date should not be far in past (e.g., > 10 years)

**When:** When creating/updating Student
**Trigger Point:** Student.clean() method
**Error Messages:**
- "Enrollment date cannot be in the future"
- "Enrollment date is too far in the past"
**Model:** `Student`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add enrollment date validation in Student.clean()

---

## 8. ACADEMIC YEAR VALIDATIONS

### 8.1 Academic Year Date Validation
**What:**
- Start date must be before end date
- Academic year dates cannot overlap with existing years
- Year field must match dates (year field ≈ calendar year of start_date)

**When:** When creating/updating AcademicYear
**Trigger Point:** AcademicYear.clean() method
**Error Messages:**
- "End date must be after start date"
- "Academic year dates overlap with existing academic year"
- "Year value {year} does not match start date year"
**Model:** `AcademicYear`

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- Has date validation (start < end)
- Has overlap checking
- **Missing:** Year field validation against dates

---

### 8.2 Active Academic Year Uniqueness
**What:**
- Only one academic year can be active at a time

**When:** When setting is_active=True on AcademicYear
**Trigger Point:** AcademicYear.clean() method
**Error Message:** "Another academic year is already active"
**Model:** `AcademicYear`

**Current Implementation:** ✅ IMPLEMENTED
- Deactivates other years in clean()

---

### 8.3 Academic Year Cannot Be Deleted with Students
**What:**
- Cannot delete academic year that contains enrolled students
- Cannot delete academic year with financial records

**When:** When attempting to delete AcademicYear
**Trigger Point:** AcademicYear.delete() method override
**Error Message:** "Cannot delete academic year with {count} enrolled students and financial records"
**Model:** `AcademicYear`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Override delete() method with validation

---

## 9. ADMINISTRATOR/TEACHER VALIDATIONS

### 9.1 Teacher Information Completeness
**What:**
- For is_teacher=True users: phone_number, specialization, qualification should be set
- Cannot assign teacher without basic info

**When:** When marking Administrator as teacher
**Trigger Point:** Administrator.clean() method
**Error Message:** "Teacher must have phone number, specialization, and qualification"
**Model:** `Administrator`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add teacher info validation in Administrator.clean()

---

### 9.2 Teacher Assignment Conflict Prevention
**What:**
- Cannot assign teacher to multiple classes simultaneously
- Cannot have overlapping TeacherAssignmentHistory records

**When:** When creating/updating TeacherAssignmentHistory
**Trigger Point:** TeacherAssignmentHistory.clean() method
**Error Message:** "Teacher is already assigned to another class during this period"
**Model:** `TeacherAssignmentHistory`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add assignment conflict validation

---

### 9.3 Email Uniqueness Validation
**What:**
- Email must be unique across all administrators
- Email must be valid format

**When:** When creating/updating Administrator
**Trigger Point:** Model field constraint and clean()
**Error Messages:**
- "Email already exists"
- "Invalid email format"
**Model:** `Administrator`

**Current Implementation:** ✅ IMPLEMENTED
- Email has unique=True constraint

---

## 10. DATA INTEGRITY VALIDATIONS

### 10.1 Cascade Protection
**What:**
- Cannot delete AcademicTerm if payments exist
- Cannot delete Class if students are enrolled
- Cannot delete TermFee if StudentBalance records exist

**When:** When attempting to delete related objects
**Trigger Point:** Model.delete() method, FK on_delete=PROTECT
**Error Message:** "Cannot delete: {related_count} {related_type} records depend on this record"
**Models:** `AcademicTerm`, `Class`, `TermFee`

**Current Implementation:** ✅ PARTIALLY IMPLEMENTED
- TermFee uses on_delete=PROTECT
- **Missing:** AcademicTerm payment protection (uses PROTECT but may need explicit validation)

---

### 10.2 Financial Data Consistency
**What:**
- StudentBalance.amount_paid must equal sum of related payments
- StudentBalance fields must be non-negative
- Arrears must not exceed total_due

**When:** When querying or updating balances
**Trigger Point:** StudentBalance.clean() or periodic audit
**Error Messages:**
- "Balance inconsistency: recorded paid != sum of payments"
- "Invalid balance: negative amount detected"
**Model:** `StudentBalance`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add data integrity checks

---

### 10.3 Historical Record Immutability
**What:**
- Cannot modify StudentMovement records after creation
- Cannot modify Payment records after creation
- Cannot modify StudentBalance after term is closed

**When:** When attempting to update historical records
**Trigger Point:** Model.save() override
**Error Message:** "Cannot modify historical record. Create correction/adjustment instead."
**Models:** `StudentMovement`, `Payment`, `StudentBalance`

**Current Implementation:** ❌ NOT IMPLEMENTED
**Required Implementation:** Add immutability checks in save() methods

---

## 11. BIRTH ENTRY NUMBER VALIDATIONS

### 11.1 Birth Entry Number Format Validation
**What:**
- Must be uppercase alphanumeric with hyphens only
- Cannot be empty or null
- Must follow country-specific format (if applicable)

**When:** When creating/updating Student
**Trigger Point:** Field validator RegexValidator
**Error Message:** "Birth entry number must contain only uppercase letters, numbers, and hyphens"
**Model:** `Student`

**Current Implementation:** ✅ IMPLEMENTED
- Field validator enforces format

---

### 11.2 Birth Entry Number Uniqueness
**What:**
- Cannot have duplicate birth entry numbers
- Each student must have unique identifier

**When:** When creating Student
**Trigger Point:** Model field unique=True
**Error Message:** "Birth entry number already exists"
**Model:** `Student`

**Current Implementation:** ✅ IMPLEMENTED
- Field has unique=True constraint

---

## SUMMARY TABLE

| Category | Total Validations | Implemented | Missing | Priority |
|----------|-------------------|-------------|---------|----------|
| Term Progression | 4 | 1 | 3 | HIGH |
| Student Movement | 7 | 3 | 4 | HIGH |
| Payments | 5 | 3 | 2 | HIGH |
| Term Fees & Enrollment | 5 | 2 | 3 | HIGH |
| Class Assignments | 6 | 4 | 2 | MEDIUM |
| Year-End Rollover | 5 | 2 | 3 | HIGH |
| Student Status | 5 | 0 | 5 | MEDIUM |
| Academic Year | 3 | 2 | 1 | MEDIUM |
| Admin/Teachers | 3 | 1 | 2 | LOW |
| Data Integrity | 3 | 1 | 2 | HIGH |
| Birth Entry Number | 2 | 2 | 0 | LOW |
| **TOTALS** | **48** | **21** | **27** | - |

---

## IMPLEMENTATION ROADMAP

### Phase 1: CRITICAL (Impacts Core Data Integrity)
1. Term sequentiality validation
2. Payment eligibility validation
3. Movement prerequisites validation
4. Arrears carryover validation
5. Financial data consistency checks

### Phase 2: HIGH (Prevents Invalid Business Logic)
1. Term progression blocking
2. Grade-based movement validation
3. Term fee amount/due date validation
4. Rollover academic year validation
5. Cascade protection enforcement

### Phase 3: MEDIUM (Improves Data Quality)
1. Student status transition formalization
2. Enrollment date validation
3. Teacher assignment conflicts
4. Class academic year validation
5. Historical record immutability

### Phase 4: LOW (Nice-to-Have)
1. Collection rate monitoring
2. Teacher info completeness
3. Birth entry number format variations
4. Age validation improvements

---

## CRITICAL BUSINESS RULES TO ENFORCE

1. **One-Way Progression:** Academic progression must always move forward (1→2→3...→7 or graduation)
2. **Arrears Preservation:** Arrears must survive all student movements
3. **Current Term Only:** Payments are only accepted for the current active term
4. **Unique Active Term:** Only one term can be active at any time
5. **Sequential Terms:** Cannot skip terms in a year
6. **Teacher Exclusivity:** Each teacher teaches exactly one class per academic year
7. **Financial Closure:** Year cannot progress until previous year financials are reconciled
8. **Class Capacity:** (May need to add) Enforce max students per class if applicable

