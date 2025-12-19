# School Management System - Production Deployment Guide (Windows)

## OVERVIEW
This guide sets up a complete production environment:
- PostgreSQL (Database)
- Django (Application)
- Gunicorn (Application Server)
- Nginx (Web Server)
- Local Domain: `schoolms.local`

All components auto-start on Windows boot. No technical action required from school staff.

---

## STEP 1: INSTALL POSTGRESQL

### 1.1 Download PostgreSQL
- Go to: https://www.postgresql.org/download/windows/
- Download PostgreSQL 15 or later (Windows x86-64)

### 1.2 Run Installer
- Run: `postgresql-15-installer.exe`
- During installation, choose:
  - ✔ PostgreSQL Server
  - ✔ pgAdmin 4
  - ✔ Command Line Tools
  - ✔ Stack Builder (optional)

### 1.3 Installation Settings
- **Port**: 5432 (default - DO NOT CHANGE)
- **Superuser Password**: Set a strong password, e.g., `PostgreSQL@2025`
- **Locale**: Default (or your locale)
- **Service Name**: postgresql-x64-15 (auto-starts on boot)

### 1.4 Verify Installation
```powershell
where psql
```
Should return path to PostgreSQL. If not, add to PATH:
- C:\Program Files\PostgreSQL\15\bin

---

## STEP 2: CREATE DATABASE & USER

### 2.1 Open pgAdmin
- Start → pgAdmin 4
- Default login: postgres / [your password from step 1.3]

### 2.2 Create Database
Right-click "Databases" → Create → Database
- **Name**: schoolms_db
- **Owner**: postgres
- Click Create

### 2.3 Create User
Right-click "Login/Group Roles" → Create → Login/Group Role
- **Name**: schoolms_user
- **Password**: StrongPassword123
- Click "Definition" tab:
  - ✔ Can login
- Click Create

### 2.4 Grant Permissions
Run this SQL query in pgAdmin (Tools → Query Tool):

```sql
GRANT ALL PRIVILEGES ON DATABASE schoolms_db TO schoolms_user;
ALTER DATABASE schoolms_db OWNER TO schoolms_user;
```

### 2.5 Test Connection
Open Command Prompt:
```powershell
psql -U schoolms_user -d schoolms_db -h localhost -W
```
Enter password: `StrongPassword123`

If you see `schoolms_db=>` prompt, PostgreSQL is ready!

---

## STEP 3: CONFIGURE DJANGO

### 3.1 Set Environment Variable
Set the system to use PostgreSQL:

**Option A: Permanent (Recommended)**
```powershell
# Run as Administrator
[Environment]::SetEnvironmentVariable('USE_POSTGRESQL', 'true', 'Machine')
```

**Option B: Temporary (for testing)**
```powershell
$env:USE_POSTGRESQL='true'
```

### 3.2 Update Django Settings
File: `school_management/settings.py`

Verify this section exists (it should already be there):
```python
elif USE_POSTGRESQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'schoolms_db'),
            'USER': os.getenv('DB_USER', 'schoolms_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'StrongPassword123'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
```

### 3.3 Run Migrations
```powershell
cd C:\Users\Admin\Desktop\School management
python manage.py migrate
```

Output should show: `Running migrations... [OK]`

### 3.4 Create Superuser
```powershell
python manage.py createsuperuser
```
- Email: admin@school.local
- Password: [choose strong password]

### 3.5 Collect Static Files
```powershell
python manage.py collectstatic --noinput
```

---

## STEP 4: INSTALL & CONFIGURE GUNICORN

### 4.1 Install Gunicorn
```powershell
pip install gunicorn
```

### 4.2 Test Gunicorn
```powershell
cd C:\Users\Admin\Desktop\School management
gunicorn school_management.wsgi:application --bind 127.0.0.1:8000
```

You should see:
```
[INFO] Listening at: http://127.0.0.1:8000
```

Press Ctrl+C to stop.

### 4.3 Install NSSM (Windows Service Manager)
- Download from: https://nssm.cc/download
- Extract to: `C:\nssm`
- Add to PATH:
  ```powershell
  [Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','Machine') + ';C:\nssm', 'Machine')
  ```

### 4.4 Create Gunicorn Windows Service
Open Command Prompt as Administrator:

```powershell
C:\nssm\nssm install SchoolMS C:\Users\Admin\AppData\Local\Programs\Python\Python313\Scripts\gunicorn.exe
```

A dialog appears:
- **Path**: `C:\Users\Admin\AppData\Local\Programs\Python\Python313\Scripts\gunicorn.exe`
- **Arguments**: `school_management.wsgi:application --bind 127.0.0.1:8000 --workers 3`
- **Startup directory**: `C:\Users\Admin\Desktop\School management`
- Click "Install service"

### 4.5 Test Service
```powershell
nssm start SchoolMS
nssm status SchoolMS
```

Should show: `SERVICE_RUNNING`

Stop for now (we'll start it after Nginx):
```powershell
nssm stop SchoolMS
```

---

## STEP 5: INSTALL & CONFIGURE NGINX

### 5.1 Download Nginx
- Go to: http://nginx.org/en/download.html
- Download: nginx/1.27.0 (or latest stable)
- Extract to: `C:\nginx`

### 5.2 Create Nginx Configuration
Edit: `C:\nginx\conf\nginx.conf`

Replace the entire `server` block (around line 47) with:

```nginx
server {
    listen 80;
    server_name schoolms.local localhost;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias C:/Users/Admin/Desktop/School management/static/;
    }

    location /media/ {
        alias C:/Users/Admin/Desktop/School management/media/;
    }
}
```

Save file.

### 5.3 Test Nginx Configuration
```powershell
C:\nginx\nginx.exe -t
```

Should show: `the configuration file ... is ok`

### 5.4 Create Nginx Shortcut for Auto-Start
1. Right-click Desktop → New → Shortcut
2. Location: `C:\nginx\nginx.exe`
3. Name: `Nginx School MS`
4. Click Finish

Move shortcut to Startup folder:
```powershell
Move-Item "C:\Users\Admin\Desktop\Nginx School MS.lnk" "C:\Users\Admin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\"
```

### 5.5 Start Nginx
```powershell
C:\nginx\nginx.exe
```

Check if running:
```powershell
netstat -ano | findstr :80
```

Should show a PID (process running).

---

## STEP 6: CREATE CLEAN LOCAL DOMAIN

### 6.1 Edit Windows Hosts File
Open Notepad as Administrator:
- File → Open
- Path: `C:\Windows\System32\drivers\etc\hosts`
- Add at the end:
  ```
  127.0.0.1   schoolms.local
  ```
- Save

### 6.2 Update Django ALLOWED_HOSTS
File: `school_management/settings.py`

Change:
```python
ALLOWED_HOSTS = ['*', 'testserver']
```

To:
```python
ALLOWED_HOSTS = ['schoolms.local', 'localhost', '127.0.0.1']
```

Restart services (see next step).

---

## STEP 7: START ALL SERVICES

### 7.1 Start Gunicorn Service
```powershell
nssm start SchoolMS
nssm status SchoolMS
```

Should show: `SERVICE_RUNNING`

### 7.2 Start Nginx
If not already running:
```powershell
C:\nginx\nginx.exe
```

### 7.3 Test System
Open any browser and go to:
```
http://schoolms.local
```

You should see the login page!

---

## STEP 8: VERIFY AUTO-START ON BOOT

### 8.1 Verify Services
```powershell
# Check Gunicorn service
nssm query SchoolMS
Get-Service postgresql-x64-15 | Select-Object Status
```

Both should show as running or set to auto-start.

### 8.2 Restart Computer
Restart Windows.

After restart:
1. Open browser
2. Type: `http://schoolms.local`
3. Login with superuser credentials

If this works, everything is properly configured!

---

## STEP 9: BACKUP STRATEGY

### 9.1 Daily PostgreSQL Backup
Create `backup_database.bat`:
```batch
@echo off
set BACKUP_DIR=C:\Users\Admin\Desktop\School management\backups
set TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

"C:\Program Files\PostgreSQL\15\bin\pg_dump" -U schoolms_user -d schoolms_db -h localhost > %BACKUP_DIR%\schoolms_db_%TIMESTAMP%.sql

echo Backup completed at %date% %time% >> %BACKUP_DIR%\backup_log.txt
pause
```

### 9.2 Schedule Daily Backup
- Task Scheduler (Windows)
- Create Basic Task
- Run: `backup_database.bat` daily at 2:00 AM

---

## STEP 10: PRODUCTION CHECKLIST

- ✔ PostgreSQL installed and auto-starts
- ✔ Database created with proper user
- ✔ Django migrations applied
- ✔ Gunicorn running as Windows service
- ✔ Nginx configured and running
- ✔ Domain `schoolms.local` works
- ✔ ALLOWED_HOSTS updated
- ✔ Static files collected
- ✔ Services auto-start on boot
- ✔ Backup strategy in place
- ✔ Superuser account created

---

## TROUBLESHOOTING

### Issue: "Cannot connect to PostgreSQL"
```powershell
# Check PostgreSQL service
Get-Service postgresql-x64-15 | Start-Service

# Test connection
psql -U schoolms_user -d schoolms_db -h localhost
```

### Issue: "Gunicorn service won't start"
```powershell
# Check logs
nssm query SchoolMS AppDirectory
nssm query SchoolMS AppExit

# Restart service
nssm stop SchoolMS
nssm start SchoolMS
```

### Issue: "Nginx not responding"
```powershell
# Check if running
netstat -ano | findstr :80

# Restart
C:\nginx\nginx.exe -s stop
C:\nginx\nginx.exe
```

### Issue: "Page shows 502 Bad Gateway"
- Check Gunicorn is running: `nssm status SchoolMS`
- Check Django logs for errors
- Verify firewall allows 127.0.0.1:8000

---

## IMPORTANT NOTES FOR SCHOOL STAFF

**What to tell them:**
"The system starts automatically when the computer is turned on. Simply open a web browser and type `schoolms.local` in the address bar. No technical knowledge required."

**What they should NOT do:**
- Don't open Command Prompt or PowerShell
- Don't try to "start" the system
- Don't modify database files
- Don't close any background windows

**What to do if it doesn't work:**
- Restart the computer
- Check internet connection
- Call the developer (you!)

---

**Deployment Date**: [Today's Date]
**System**: School Management System v1.0
**Status**: Production Ready
