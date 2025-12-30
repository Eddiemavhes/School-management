# ECDA/ECDB Implementation Guide

## Overview
The system now supports Early Childhood Development classes (ECDA and ECDB) as pre-primary levels before Grade 1.

## Class Progression Path
```
ECDA (Age 4-5) → ECDB (Age 5-6) → Grade 1 (Age 6+) → Grade 2 → ... → Grade 7
```

## Key Features Implemented

### 1. **Class Model Updates**
- Grade field changed from IntegerField to CharField
- Supports both numeric grades (1-7) and string grades (ECDA, ECDB)
- ECDA and ECDB have full separate fee structures
- Same section system (A, B) applies to all grades

### 2. **Student Progression Methods**
```python
# Get the next class for a student
next_class = student.get_next_class()

# Promote student to next class
success, message, new_class = student.promote_to_next_class()
```

### 3. **Batch Promotion Command**
```bash
# Promote all Grade 7 students
python manage.py promote_students --from-grade 7 --to-year 2026

# Preview promotions without saving
python manage.py promote_students --dry-run

# Auto-confirm without asking
python manage.py promote_students --confirm
```

## Setting Up ECDA/ECDB

### Step 1: Create Academic Years
Ensure both current and next academic years exist:
```bash
python manage.py shell
>>> from core.models import AcademicYear
>>> AcademicYear.objects.create(year=2025, is_active=True)
>>> AcademicYear.objects.create(year=2026, is_active=False)
```

### Step 2: Create Classes
Create ECDA, ECDB, and Grade 1-7 classes for each academic year:
```bash
# Via Django admin or:
>>> from core.models import Class
>>> Class.objects.create(grade='ECDA', section='A', academic_year=2025)
>>> Class.objects.create(grade='ECDA', section='B', academic_year=2025)
>>> Class.objects.create(grade='ECDB', section='A', academic_year=2025)
>>> # ... continue for other grades
```

### Step 3: Set Up Fee Structures
ECDA, ECDB, and each grade have separate fee structures:
```bash
# Via Django admin:
# 1. Create TermFee records for ECDA
# 2. Create TermFee records for ECDB
# 3. Create TermFee records for Grades 1-7
```

Each TermFee should specify:
- Academic Term (Term 1, Term 2, Term 3)
- Class (ECDA-A, ECDB-A, etc.)
- Amount

### Step 4: Enroll Students in ECDA
Students start their journey in ECDA with automatic progression as they complete each year.

## Fee Management

### Different Fee Structures
Each grade level can have different fees:
- ECDA: May have lower fees (pre-primary)
- ECDB: May have lower fees (pre-primary)
- Grade 1-7: Progressive fees based on grade level

### Automatic Fee Tracking
When a student is promoted to a new class, the system automatically:
1. Tracks their movement
2. Associates new TermFee for that class/term
3. Maintains previous arrears history

## Important Notes

### ⚠️ Data Integrity
1. Always create academic years BEFORE creating classes
2. Create classes BEFORE enrolling students
3. Create fee structures BEFORE the term starts
4. Use the promotion command for bulk promotions to maintain consistency

### 🔐 Safety Features
1. Promotion command includes dry-run option (preview without changes)
2. Grade 7 students cannot be promoted (final grade)
3. Each promotion is validated before execution
4. Transaction rollback on errors

### 📊 Fee Tracking Across Classes
The StudentBalance model automatically handles:
- Current class fees
- Previous arrears from previous classes
- Complete payment history across all classes

## Migration Details

### Migration File: 0050_add_ecda_ecdb_support.py
Changes the `Class.grade` field from IntegerField to CharField with choices:
- ECDA, ECDB, 1, 2, 3, 4, 5, 6, 7

**No data loss** - existing numeric grades (1-7) remain valid as CharField values.

## Rollback Instructions (If Needed)

If you need to revert ECDA/ECDB support:
```bash
# Only if not yet used in production
python manage.py migrate core 0049_alter_class_options
```

⚠️ WARNING: Do this ONLY if no ECDA/ECDB classes are in use!

## Support & Troubleshooting

### Issue: "Class DoesNotExist" during promotion
- Ensure next year's classes are created
- Run: `python manage.py promote_students --to-year 2026` (specify the year)

### Issue: Students in Grade 7 cannot promote
- This is by design. Grade 7 is the final grade.
- Change student status to GRADUATED/ALUMNI

### Issue: Fee structure mismatch
- Ensure TermFees exist for ECDA, ECDB, and all grades
- Check that fees are linked to correct classes

## Examples

### Creating Complete Class Structure for New Year
```python
from core.models import Class, AcademicYear

year = 2026
AcademicYear.objects.create(year=year, is_active=False)

grades = ['ECDA', 'ECDB', '1', '2', '3', '4', '5', '6', '7']
sections = ['A', 'B']

for grade in grades:
    for section in sections:
        Class.objects.create(
            grade=grade,
            section=section,
            academic_year=year
        )
```

### Promoting All Grade 7 Students (Year End)
```bash
python manage.py promote_students --from-grade 7 --to-year 2026 --confirm
```

### Checking Student's Class Progression
```python
from core.models import Student

student = Student.objects.get(id=1)
print(f"Current: {student.current_class}")
print(f"Next: {student.get_next_class()}")
```

## Feature Expansion (Future)

Possible enhancements:
- Custom progression paths per student
- Conditional promotion (based on exam scores)
- Automatic fee calculation based on grade level
- Age-based class recommendation system
- Multi-class per student (split classes)
