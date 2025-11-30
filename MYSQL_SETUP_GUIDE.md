# MySQL Setup Guide for School Management System

## Quick Start

Your Django application is now configured to support MySQL. To enable MySQL:

### Step 1: Install MySQL

**Option A: MySQL (Official)**
- Download: https://dev.mysql.com/downloads/mysql/
- Run installer and complete setup
- Default port: 3306
- Default root user: root (no password by default)

**Option B: MariaDB (Compatible Drop-in Replacement - Recommended)**
- Download: https://mariadb.org/download/
- Easier to install and fully MySQL compatible
- Run installer and complete setup
- Default port: 3306

### Step 2: Create Database (After MySQL Installation)

Open MySQL command line or MySQL Workbench and run:

```sql
-- Create database
CREATE DATABASE school_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'school_admin'@'localhost' IDENTIFIED BY 'SchoolAdmin123!';

-- Grant privileges
GRANT ALL PRIVILEGES ON school_management_db.* TO 'school_admin'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;
```

### Step 3: Update Environment

Create or edit `.env` file in project root:

```
USE_MYSQL=True
USE_POSTGRESQL=False

DB_NAME=school_management_db
DB_USER=school_admin
DB_PASSWORD=SchoolAdmin123!
DB_HOST=localhost
DB_PORT=3306
```

### Step 4: Run Setup Script

```powershell
cd "c:\Users\Admin\Desktop\School management"
python setup_mysql.py
```

This will:
1. Check MySQL installation
2. Create database if not exists
3. Backup SQLite data
4. Export all data
5. Run Django migrations
6. Load data into MySQL
7. Verify connection

### Step 5: Verify Setup

```powershell
python manage.py dbshell
# Should connect to MySQL
```

### Step 6: Start Server

```powershell
python manage.py runserver
```

## Database Configuration Details

### MySQL Connection String
```
mysql://school_admin:SchoolAdmin123!@localhost:3306/school_management_db
```

### Django Setting

The application automatically detects which database to use based on environment variables:
- `USE_MYSQL=True` → MySQL
- `USE_POSTGRESQL=True` → PostgreSQL  
- Default → SQLite

## Troubleshooting

### MySQL Not Found
- Ensure MySQL/MariaDB is installed and in system PATH
- Add to PATH: `C:\Program Files\MySQL\MySQL Server 8.0\bin`

### Port Already in Use
- Change port in `.env`: `DB_PORT=3307`
- Restart MySQL service

### Connection Refused
- Ensure MySQL service is running
- On Windows: Services app → look for MySQL
- Verify credentials in `.env`

### Charset Errors
- MySQL 8.0 uses `utf8mb4` by default (recommended)
- Django settings include charset configuration

## Switching Databases

### SQLite → MySQL
1. Set `USE_MYSQL=True` in `.env`
2. Ensure MySQL is running
3. Run `python setup_mysql.py`

### MySQL → PostgreSQL
1. Set `USE_POSTGRESQL=True` in `.env`
2. Set PostgreSQL connection details in `.env`
3. Run `python manage.py migrate`

### MySQL → SQLite
1. Delete `.env` or set `USE_MYSQL=False`
2. Run `python manage.py migrate`

## Performance Tips

For production MySQL:
1. Enable query caching
2. Optimize table indexes
3. Set appropriate buffer pool size
4. Use connection pooling

## Next Steps

Once MySQL is installed:
1. Run `python setup_mysql.py`
2. Test with `python manage.py dbshell`
3. All your data will be automatically migrated!

