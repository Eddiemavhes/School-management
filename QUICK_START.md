# 🚀 Quick Start Guide - School Management System

## Current Status

✓ **Application**: Ready to run
✓ **Database**: SQLite (default, no installation needed)
✓ **Features**: All graduation, payment, and balance logic fully implemented
✓ **Data**: 4 students with complete history (2026-2028)

---

## Run Your Application RIGHT NOW

```powershell
cd "c:\Users\Admin\Desktop\School management"
python manage.py runserver
```

Then open: **http://localhost:8000**

That's it! Your system is ready to use.

---

## What's Included

### Core Features ✓
- Student management (enrollment, graduation)
- Payment tracking and recording
- Balance calculations with arrears carryover
- Automatic graduation after Grade 7 completion
- Alumni status and fee protection
- Complete audit trail (StudentMovement)

### Databases Supported ✓
- SQLite (default, active now)
- MySQL (ready to activate)
- PostgreSQL (ready to activate)

### Data Included ✓
- 4 test students with complete history
- 3 academic years (2026, 2027, 2028)
- 9 academic terms with fees
- Complete payment records
- All graduation records

---

## Quick Commands

### Start Application
```powershell
python manage.py runserver
```
Visit: http://localhost:8000

### Check Database Status
```powershell
python manage.py dbshell
# Shows current database connection
```

### Create Admin Account
```powershell
python manage.py createsuperuser
```

### View Data
```powershell
python manage.py shell
>>> from core.models import Student
>>> Student.objects.all()
```

### Switch to MySQL (When Installed)
```powershell
.\setup_mysql.bat
# Or: python setup_mysql.py
```

### Reset Database (Warning: Deletes Data)
```powershell
python manage.py migrate zero
python manage.py migrate
```

---

## File Structure

```
School management/
├── manage.py                          # Django management
├── db.sqlite3                         # Current database
├── .env                               # Configuration (auto-created)
├── .env.example                       # Configuration template
│
├── school_management/                 # Django project settings
│   ├── settings.py                   # Main configuration (database, apps, etc)
│   ├── urls.py                       # URL routing
│   └── wsgi.py                       # Production server config
│
├── core/                              # Main application
│   ├── models/
│   │   ├── student.py               # Student model
│   │   ├── academic.py              # Terms, years, payments
│   │   ├── fee.py                   # Balances, term fees
│   │   └── student_movement.py      # Graduation tracking
│   │
│   ├── views/
│   │   ├── payment_views.py         # Payment recording
│   │   ├── student_views.py         # Student management
│   │   └── superuser_views.py       # Admin interface
│   │
│   ├── signals.py                   # Auto-graduation logic
│   └── templates/                    # HTML templates
│
├── static/                            # CSS, JavaScript
├── templates/                         # HTML files
│
├── Setup Scripts
├── setup_mysql.bat                    # Windows MySQL setup
├── setup_mysql.py                     # Python MySQL setup
├── setup_postgresql.py                # PostgreSQL setup
│
├── Documentation
├── MYSQL_SETUP_SUMMARY.md            # MySQL quick reference
├── DATABASE_GUIDE.md                 # Database comparison
├── MYSQL_SETUP_GUIDE.md              # Detailed MySQL guide
└── POSTGRESQL_MIGRATION_GUIDE.md     # PostgreSQL guide
```

---

## Key Features Implemented

### ✓ Balance Calculation
- Shows current term balance only (not accumulated)
- Carries forward arrears from previous terms
- Handles credits (overpayments) correctly

### ✓ Payment Recording
- Works for active students
- Supports graduated students (arrears only)
- Updates balance automatically via signal

### ✓ Graduation Logic
- Students graduate after completing Grade 7 (3 terms)
- Auto-graduation triggered when Term 3 marked current
- Alumni status based on payment (fully paid = archived)

### ✓ Fee Management
- Graduated students don't get new term fees
- Outstanding arrears carry forward
- Term fees set at system level

### ✓ Student Data
- Personal info (name, DOB, sex, entry number)
- Class assignment (Grade 1-7)
- Enrollment status tracking
- Movement history (transfers, graduation)

---

## Database Status

### Current (SQLite)
- ✓ 4 students with full history
- ✓ All payment records preserved
- ✓ Graduation data complete
- ✓ Ready for development/testing

### Available Options

**Switch to MySQL:**
1. Install MySQL/MariaDB
2. Run: `.\setup_mysql.bat`
3. Done!

**Switch to PostgreSQL:**
1. Install PostgreSQL
2. Run: `python setup_postgresql.py`
3. Done!

---

## Test Users

All students complete with historical data:

1. **Annah (ID: 8)**
   - Status: Alumni (graduated, fully paid)
   - Grade: 7 (completed 2027)
   - Balance: $0.00 (credit available)

2. **Brandon (ID: 9)**
   - Status: Alumni (graduated, fully paid)
   - Grade: 7 (completed 2027)
   - Balance: $0.00

3. **Cathrine (ID: 10)**
   - Status: Graduated (has arrears)
   - Grade: 7 (completed 2027)
   - Balance: $10.00 (from 2026)

4. **David (ID: 11)**
   - Status: Graduated (has arrears)
   - Grade: 7 (completed 2027)
   - Balance: $600.00 (from 2026-2027)

---

## Common Tasks

### Add New Student
1. Go to: Students → + Add Student
2. Enter details
3. Select Grade and Class
4. Click Save

### Record Payment
1. Go to: Students → Student Card
2. Click "Edit" → "Add Payment"
3. Enter amount and date
4. Click Save

### Change Database
```powershell
# Edit .env file:
USE_MYSQL=True    # for MySQL
USE_POSTGRESQL=True  # for PostgreSQL
# (blank/False for SQLite)

# Then run migrations:
python manage.py migrate
```

### View Student History
1. Go to: Students → Student Card
2. Click "View" to see all details
3. Shows balances for all terms
4. Shows all payments

---

## Troubleshooting

### App Won't Start
```powershell
# Check Python
python --version

# Check Django
python manage.py --version

# Check if port 8000 is available
netstat -ano | findstr :8000
```

### Database Error
```powershell
# Reset to SQLite
Remove-Item .env

# Run migrations
python manage.py migrate
```

### Forgot Admin Password
```powershell
# Create new admin
python manage.py createsuperuser
```

---

## Documentation Files

Read these for detailed info:

- **MYSQL_SETUP_SUMMARY.md** - How to switch to MySQL
- **DATABASE_GUIDE.md** - Compare all databases
- **MYSQL_SETUP_GUIDE.md** - MySQL detailed setup
- **POSTGRESQL_MIGRATION_GUIDE.md** - PostgreSQL setup

---

## Next Steps

1. **Start the application** (see above)
2. **Log in** with admin credentials
3. **Explore student data** - click on any student card
4. **Try recording a payment** - see balance update live
5. **Review graduation logic** - all students are in correct status

---

## Command Reference

```powershell
# Run server
python manage.py runserver

# Access database
python manage.py dbshell

# Create admin
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Load sample data
python manage.py loaddata data_backup.json

# Export data
python manage.py dumpdata > backup.json

# Run tests (if added)
python manage.py test

# Django shell
python manage.py shell
```

---

## Support

If something doesn't work:

1. Check error message carefully
2. Verify database connection: `python manage.py dbshell`
3. Review settings: Check `.env` file
4. Check logs: `school_management.log`
5. Reset if needed: Delete `.env` and rebuild

---

## Summary

🎉 **Your application is ready!**

- ✓ All features implemented
- ✓ All data intact
- ✓ 3 database options available
- ✓ Multiple setup scripts provided
- ✓ Complete documentation

**To start:** 
```powershell
python manage.py runserver
```

**Then visit:** http://localhost:8000

Enjoy! 🚀
