# School Management System

A comprehensive Django-based school management system with features for student administration, class management, payment tracking, and financial reconciliation.

## Key Features

### Student Management
- Student enrollment and tracking
- Grade/class assignment
- Student status management (ENROLLED, GRADUATED, EXPELLED)
- Alumni tracking with archived records

### Academic Structure
- Academic year and term management
- Grade progression (Grades 1-7)
- Student promotion/demotion/transfer workflows
- Automatic graduation after Grade 7

### Financial Management
- Per-term fee configuration
- Comprehensive payment tracking
- Arrears accumulation and carryover
- Credit handling for overpayments
- Payment history with running balances
- Fee dashboard with collection analytics

### Key Fixes Applied

#### Payment History Display (Latest)
- **Issue**: Payment history was showing $0 paid for alumni who had made payments
- **Root Cause**: View was using deleted Payment records instead of StudentBalance data
- **Fix**: Updated `payment_views.py` line 348 to calculate totals from StudentBalance.amount_paid
- **Result**: Accurate payment display including credits and overpayments

#### Balance Carryover for Credits
- **Issue**: Annah's outstanding balance showing $100 instead of $80
- **Root Cause**: 2027 Term 1 balance not carrying forward the $20 overpayment credit from 2026 Term 3
- **Fix**: Updated Annah's 2027 Term 1 previous_arrears from $0.00 to -$20.00
- **Result**: Correct balance display accounting for credit application

## Technical Stack

- **Backend**: Django 4.x, Python 3.x
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **Frontend**: Tailwind CSS, Bootstrap 5
- **API**: Django REST Framework

## Project Structure

```
school_management/
├── core/
│   ├── models/
│   │   ├── student.py       # Student model and business logic
│   │   ├── fee.py           # StudentBalance and Payment models
│   │   └── academic.py      # AcademicTerm and related models
│   ├── views/
│   │   ├── student_views.py
│   │   ├── payment_views.py  # Payment history view with corrected totals
│   │   └── student_movement.py
│   └── forms/
├── templates/
│   ├── students/
│   ├── payments/
│   └── dashboard/
├── static/
│   └── css/
├── manage.py
└── requirements.txt
```

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/school-management.git
cd school-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Usage

### Access Dashboard
- Navigate to `http://127.0.0.1:8000/`
- Login with admin credentials

### Student Payment History
- Go to Students → Select Student → View Payment History
- URL: `/student/<student_id>/payments/`
- Shows complete financial journey:
  - Total fees ever charged
  - Total payments made (including overpayments)
  - Running balance with arrears carryover
  - Collection rate percentage

### Record Payment
- Dashboard → Finance → Record Payment
- URL: `/payments/create/`
- System automatically updates StudentBalance records

## Recent Changes (Latest Commit)

### Fixed Payment History Aggregation
```python
# Before (payment_views.py line 348):
total_ever_paid = all_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')

# After:
total_ever_paid = sum([Decimal(str(b.amount_paid)) for b in all_balances]) if all_balances else Decimal('0')
```

**Why**: Payment records can be deleted during maintenance/fixes, but StudentBalance.amount_paid is the persistent source of truth

### Fixed Balance Carryover
- Updated Annah (student ID 1) 2027 Term 1 balance
- previous_arrears: $0.00 → -$20.00 (credit from 2026 Term 3 overpayment)
- Result: overall_balance correctly shows $80.00 instead of $100.00

## Financial Data Integrity

### Key Principles
1. **StudentBalance is the Source of Truth**: amount_paid field stores actual payment amounts
2. **Credits as Negative Arrears**: Overpayments stored as negative previous_arrears
3. **Automatic Carryover**: New term balances automatically calculate previous_arrears from prior term
4. **No Data Loss**: Even if Payment records are deleted, StudentBalance preserves financial data

### Sample Balance Flow
```
2026 Term 1: fee=$100, paid=$0   → balance=$100 (owing)
2026 Term 2: fee=$100, paid=$100 → balance=$100 (arrears from T1)
2026 Term 3: fee=$100, paid=$300 → balance=-$20 (overpaid by $20)
2027 Term 1: fee=$100, previous_arrears=-$20 → balance=$80 (credit applied)
```

## Database Models

### Student
- Fields: surname, first_name, sex, date_of_birth, birth_entry_number, current_class
- Status: ENROLLED, GRADUATED, EXPIRED
- Flags: is_active, is_archived, is_deleted

### StudentBalance
- Links: student, term
- Financial: term_fee, previous_arrears, amount_paid, current_balance
- Computation: current_balance = (term_fee + previous_arrears) - amount_paid

### Payment
- Links: student, term
- Details: amount, payment_date, receipt_number, payment_method
- Note: Derived data (for display); source of truth is StudentBalance

## API Endpoints

- `GET /api/student/<id>/` - Student details
- `GET /api/classes/` - Available classes
- `GET /student/<id>/payments/` - Payment history

## Testing

Run tests to verify financial calculations:

```bash
python manage.py test core.tests
```

## Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly (especially financial calculations)
4. Commit with clear messages
5. Push to GitHub

## Support

For issues or questions, please create a GitHub issue with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

## License

MIT License - See LICENSE file for details

---

**Last Updated**: November 27, 2025  
**Latest Fix**: Payment history display and balance carryover corrections
