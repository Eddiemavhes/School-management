# ECD PROGRESSION & FEES MANAGEMENT GUIDE

## System Updated: ECDA/ECDB Support

The system now supports proper Early Childhood Development progression:
```
ECDA (Age 4-5) → ECDB (Age 5-6) → Grade 1 (Age 6+) → Grade 2 → ... → Grade 7
```

## Step-by-Step Setup

### 1. CREATE CLASSES FOR ECDA & ECDB

Go to: **Settings > Classes > Create Class**

```
For 2026 Academic Year:
├── ECDA A (Section A)
├── ECDA B (Section B)
├── ECDB A (Section A)
├── ECDB B (Section B)
├── 1 A (Grade 1, Section A)
├── 1 B (Grade 1, Section B)
└── ... (continue for Grades 2-7)
```

Or use Django Shell:
```python
from core.models import Class

# ECDA Classes
Class.objects.create(grade='ECDA', section='A', academic_year=2026)
Class.objects.create(grade='ECDA', section='B', academic_year=2026)

# ECDB Classes
Class.objects.create(grade='ECDB', section='A', academic_year=2026)
Class.objects.create(grade='ECDB', section='B', academic_year=2026)

# Grade 1-7 Classes
for grade in range(1, 8):
    Class.objects.create(grade=str(grade), section='A', academic_year=2026)
    Class.objects.create(grade=str(grade), section='B', academic_year=2026)
```

### 2. SET UP FEES FOR EACH LEVEL

Go to: **Settings > Fees > Create Fee**

Create Term Fees for each class/term combination:

```
ECDA Classes:
├── Term 1: $X per ECDA class
├── Term 2: $X per ECDA class
└── Term 3: $X per ECDA class

ECDB Classes:
├── Term 1: $Y per ECDB class
├── Term 2: $Y per ECDB class
└── Term 3: $Y per ECDB class

Grade 1:
├── Term 1: $Z per Grade 1 class
├── Term 2: $Z per Grade 1 class
└── Term 3: $Z per Grade 1 class

... (continue for Grades 2-7)
```

**IMPORTANT:** Fees are set per Class, so each class (ECDA-A, ECDA-B, etc.) can have different fees if needed.

### 3. ENROLL STUDENTS IN ECDA

Go to: **Students > Create Student**

1. Select ECDA A or ECDA B as their current class
2. Mark as Active
3. System will automatically track their fees

### 4. PROMOTE ECDA → ECDB (SAME YEAR)

Use the Student Movement page:

**Option A: Individual Transfer**
- Go to: **Dashboard > Class Transfers**
- Select student from ECDA
- Transfer to ECDB (same academic year)

**Option B: Bulk Promotion**
- Go to: **Dashboard > Bulk Promotion**
- Filter for ECDA students (optional)
- Manually select and transfer to ECDB

**Important:** ECDA → ECDB happens in the SAME academic year (2026 → 2026)

### 5. PROMOTE ECDB → GRADE 1 (NEXT YEAR)

**When:** Usually at end of academic year

**Process:**
- Go to: **Dashboard > Class Transfers**
- Select student from ECDB (Year 2026)
- Transfer to Grade 1 (Year 2027)

The system will:
- Create a StudentMovement record (ECDB → Grade 1)
- Automatically create StudentBalance for Grade 1 terms
- Calculate any carried-over arrears

## Fee Structure Example

Say ECDA costs $500/term, ECDB costs $550/term, Grade 1 costs $600/term:

```
Student Timeline:
Jan 2026 - Joins ECDA A: $500 × 3 terms = $1,500
Dec 2026 - Transfers to ECDB B: $550 × 3 terms = $1,650
Jan 2027 - Transfers to Grade 1: $600 × 3 terms = $1,800

Total First Year: $4,950
Any unpaid amounts carry forward as arrears.
```

## Viewing ECD Progress

### Dashboard > Students
Shows all students with their current class and grade

### Individual Student Page
- Current class (ECDA, ECDB, or Grade X)
- Payment history (shows payments at each level)
- Movement history (shows all transfers)
- Total balance (sum of all unpaid terms)

### Reports
- **Fee Dashboard**: Shows outstanding fees by grade
- **Arrears Report**: Shows students with unpaid fees at each level

## Important Notes

⚠️ **ECD STUDENTS CANNOT USE BULK PROMOTION**
- ECDA students are prevented from bulk promotion
- Must use individual Class Transfers instead
- This ensures proper ECDA → ECDB → Grade 1 progression

⚠️ **FEES ARE CLASS-SPECIFIC**
- ECDA-A might have different fees than ECDA-B (if needed)
- Each class/term combination needs a separate TermFee entry
- StudentBalance automatically uses the correct fees

⚠️ **ARREARS CARRY FORWARD**
- Unpaid fees from ECDA carry to ECDB
- Unpaid fees from ECDB carry to Grade 1
- System tracks entire payment history

## Quick Reference: Where to Find Things

| Task | Location |
|------|----------|
| Create Classes | Settings > Classes |
| Set Fees | Settings > Fees |
| Enroll Student | Students > Create Student |
| Transfer Student (ECDA→ECDB) | Dashboard > Class Transfers |
| View Student Progress | Students > [Select Student] |
| Check Fee Status | Fees > Fee Dashboard |
| Payment Records | Payments > Payment List |

## Command Line (Advanced)

```bash
# View all classes
python manage.py shell
>>> from core.models import Class
>>> Class.objects.all().order_by('grade', 'section')

# View students in each grade
>>> from core.models import Student
>>> Student.objects.filter(current_class__grade='ECDA')
>>> Student.objects.filter(current_class__grade='ECDB')
>>> Student.objects.filter(current_class__grade='1')
```
