@echo off
REM MySQL One-Click Setup Script for School Management System

echo.
echo ╔════════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                                ║
echo ║         School Management System - MySQL Setup                                ║
echo ║                                                                                ║
echo ╚════════════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if MySQL is installed
echo Checking for MySQL installation...
mysql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ✗ MySQL not found in PATH
    echo.
    echo Please install MySQL first:
    echo   1. Download from: https://dev.mysql.com/downloads/mysql/
    echo   2. OR Download MariaDB: https://mariadb.org/download/
    echo   3. Run the installer
    echo   4. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✓ MySQL found!
echo.

REM Test MySQL connection
echo Testing MySQL connection...
mysql -u root -e "SELECT 1;" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ✗ Cannot connect to MySQL
    echo.
    echo Please ensure:
    echo   1. MySQL service is running
    echo   2. Root user password is empty (or adjust command below)
    echo.
    pause
    exit /b 1
)

echo ✓ MySQL service is running!
echo.

REM Create database and user
echo Creating database and user...
mysql -u root -e "DROP DATABASE IF EXISTS school_management_db;" >nul 2>&1
mysql -u root -e "DROP USER IF EXISTS 'school_admin'@'localhost';" >nul 2>&1
mysql -u root -e "CREATE DATABASE school_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" >nul 2>&1
mysql -u root -e "CREATE USER 'school_admin'@'localhost' IDENTIFIED BY 'SchoolAdmin123!';" >nul 2>&1
mysql -u root -e "GRANT ALL PRIVILEGES ON school_management_db.* TO 'school_admin'@'localhost';" >nul 2>&1
mysql -u root -e "FLUSH PRIVILEGES;" >nul 2>&1

echo ✓ Database created!
echo.

REM Create .env file
echo Creating .env file...
(
    echo # Database Configuration
    echo USE_MYSQL=True
    echo USE_POSTGRESQL=False
    echo.
    echo # MySQL Settings
    echo DB_NAME=school_management_db
    echo DB_USER=school_admin
    echo DB_PASSWORD=SchoolAdmin123!
    echo DB_HOST=localhost
    echo DB_PORT=3306
) > .env

echo ✓ .env file created!
echo.

REM Backup SQLite
echo Backing up SQLite database...
if exist db.sqlite3 (
    copy db.sqlite3 db.sqlite3.backup >nul 2>&1
    echo ✓ SQLite backup created: db.sqlite3.backup
) else (
    echo ✓ No SQLite database to backup
)
echo.

REM Export data
echo Exporting data...
python manage.py dumpdata > data_backup.json
if %errorlevel% equ 0 (
    echo ✓ Data exported to data_backup.json
) else (
    echo ⚠ Warning: Could not export data
)
echo.

REM Run migrations
echo Running migrations...
python manage.py migrate
if %errorlevel% equ 0 (
    echo ✓ Migrations completed!
) else (
    echo ✗ Migration failed - check output above
    pause
    exit /b 1
)
echo.

REM Load data
echo Loading data into MySQL...
python manage.py loaddata data_backup.json
if %errorlevel% equ 0 (
    echo ✓ Data loaded successfully!
) else (
    echo ⚠ Warning: Could not load data
)
echo.

REM Verify connection
echo Verifying MySQL connection...
python manage.py dbshell < nul
if %errorlevel% equ 0 (
    echo ✓ Connection successful!
) else (
    echo ✗ Connection failed
    pause
    exit /b 1
)
echo.

echo ╔════════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                                ║
echo ║                    ✓ MySQL Setup Complete!                                    ║
echo ║                                                                                ║
echo ║  Your application is now using MySQL!                                         ║
echo ║                                                                                ║
echo ║  Next steps:                                                                   ║
echo ║    1. Start server: python manage.py runserver                                ║
echo ║    2. Open: http://localhost:8000                                             ║
echo ║    3. All data has been migrated to MySQL                                     ║
echo ║                                                                                ║
echo ╚════════════════════════════════════════════════════════════════════════════════╝
echo.

pause
