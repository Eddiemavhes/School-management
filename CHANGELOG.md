# Changelog

All notable changes to the School Management System are documented in this file.

## [1.0.0] - 2025-11-27

### Fixed
- **Payment History Display Bug**: Fixed aggregation of total payments from deleted Payment records
  - Changed view to use StudentBalance.amount_paid (persistent) instead of Payment table sum
  - File: `core/views/payment_views.py` line 348
  - Impact: Alumni payment history now shows correct totals (e.g., Daniel: $400 paid, not $0)

- **Balance Carryover for Credits**: Fixed missing credit application in new term balances
  - Corrected Annah's 2027 Term 1 balance to properly carry forward -$20.00 credit
  - File: Database update (StudentBalance id=77)
  - Impact: Outstanding balance now correctly shows $80 instead of $100

### Changed
- Updated payment calculation logic to prioritize StudentBalance over Payment records
- Improved financial data persistence (StudentBalance is now the single source of truth)

### Technical Details

#### Payment History Fix
```
Before: Total Paid = SUM(Payment.amount) = $0 (empty after deletion)
After:  Total Paid = SUM(StudentBalance.amount_paid) = $400 (persistent)
```

#### Balance Carryover Fix
```
Before: 2027 T1 previous_arrears = $0.00 → balance = $100.00
After:  2027 T1 previous_arrears = -$20.00 → balance = $80.00
```

### Files Modified
1. `core/views/payment_views.py`
   - Line 348: Changed total_ever_paid calculation

2. Database
   - StudentBalance record for Annah (2027 Term 1)
   - Updated previous_arrears and current_balance

### Testing
- Verified Daniel (alumni) payment history displays correct totals
- Verified Annah's outstanding balance calculation
- Verified Carol's 2027 balance shows $110 ($100 fee + $10 arrears)
- Verified Brandon's 2027 balance shows $100 ($100 fee, no arrears)

### Known Issues
None at this time

---

## [0.9.0] - Previous Releases

### Features
- Student enrollment and management
- Grade progression (Grades 1-7)
- Automatic graduation after Grade 7
- Per-term fee configuration
- Payment tracking and reporting
- Arrears accumulation
- Payment history display

### Previous Fixes
- Grade 7 promotion logic (now correctly graduates instead of marking inactive)
- Balance carryover from 2026 to 2027 for active students
- Exclusion of 2027 balances for graduating students
- Alumni archiving after debt payment

---

## Version History

| Version | Date | Status |
|---------|------|--------|
| 1.0.0   | 2025-11-27 | Current |
| 0.9.0   | 2025-11-27 | Previous |

---

## How to Use This Changelog

- **Fixed**: Bug fixes and corrections
- **Changed**: Changes in existing functionality
- **Added**: New features
- **Removed**: Removed features
- **Technical Details**: Implementation specifics
- **Testing**: Validation performed

Each entry should include:
1. What was changed
2. Why it was changed (root cause)
3. File(s) affected
4. Impact on users
5. How to test the fix
