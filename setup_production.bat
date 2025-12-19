@echo off
REM School Management System - Quick Setup Script
REM Run as Administrator

echo.
echo ========================================
echo School Management System Setup
echo ========================================
echo.

REM Step 1: Set Environment Variable
echo [1/5] Setting PostgreSQL environment variable...
setx USE_POSTGRESQL true
echo Done!

REM Step 2: Run Django Migrations
echo.
echo [2/5] Running Django migrations...
cd /d "C:\Users\Admin\Desktop\School management"
python manage.py migrate
echo Done!

REM Step 3: Collect Static Files
echo.
echo [3/5] Collecting static files...
python manage.py collectstatic --noinput
echo Done!

REM Step 4: Create NSSM Service
echo.
echo [4/5] Creating Gunicorn Windows service...
C:\nssm\nssm install SchoolMS C:\Users\Admin\AppData\Local\Programs\Python\Python313\Scripts\gunicorn.exe
REM Set arguments
C:\nssm\nssm set SchoolMS AppParameters "school_management.wsgi:application --bind 127.0.0.1:8000 --workers 3"
C:\nssm\nssm set SchoolMS AppDirectory "C:\Users\Admin\Desktop\School management"
C:\nssm\nssm set SchoolMS Start SERVICE_AUTO_START
echo Done!

REM Step 5: Update Hosts File
echo.
echo [5/5] Adding schoolms.local to hosts file...
echo 127.0.0.1   schoolms.local >> C:\Windows\System32\drivers\etc\hosts
echo Done!

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Install PostgreSQL from: https://www.postgresql.org/download/windows/
echo 2. Create database 'schoolms_db' and user 'schoolms_user'
echo 3. Download Nginx from: http://nginx.org/en/download.html
echo 4. Extract Nginx to: C:\nginx
echo 5. Update C:\nginx\conf\nginx.conf with the configuration from DEPLOYMENT_GUIDE.md
echo 6. Run: nssm start SchoolMS
echo 7. Run: C:\nginx\nginx.exe
echo 8. Open browser and go to: http://schoolms.local
echo.
pause
