# PostgreSQL + Django + Nginx + Gunicorn Setup - Windows

## QUICK SETUP CHECKLIST

Follow these steps in order. Each step must complete before moving to next.

---

## STEP 1: POSTGRESQL INSTALLATION (REQUIRED FIRST)

**Status:** [ ] Not Started [ ] In Progress [ ] Complete

### What to do:
1. Download PostgreSQL 15/16 from: https://www.postgresql.org/download/windows/
2. Run installer: `postgresql-15-installer.exe`
3. During installation:
   - ✓ PostgreSQL Server
   - ✓ pgAdmin 4
   - ✓ Command Line Tools
   - Port: **5432** (default)
   - SuperUser Password: **PostgreSQL@2025** (or your choice)

### Verify:
```powershell
# Check if PostgreSQL is running
Get-Service postgresql-x64-15 | Select-Object Status
# Should show: Status = Running
```

**STOP HERE until PostgreSQL is installed and running.**

---

## STEP 2: CREATE DATABASE & USER (PostgreSQL)

**Status:** [ ] Not Started [ ] In Progress [ ] Complete

### Open pgAdmin:
1. Start → pgAdmin 4
2. Default login: postgres / [your password from Step 1]
3. Right-click "Databases" → Create → Database
   - Name: **schoolms_db**
   - Owner: postgres
   - Click Create

### Create User:
1. Right-click "Login/Group Roles" → Create → Login/Group Role
   - Name: **schoolms_user**
   - Password: **StrongPassword123**
   - Click Definition tab → Check "Can login"
   - Click Create

### Grant Permissions:
1. Tools → Query Tool
2. Paste and run:
```sql
GRANT ALL PRIVILEGES ON DATABASE schoolms_db TO schoolms_user;
ALTER DATABASE schoolms_db OWNER TO schoolms_user;
```

### Test Connection:
```powershell
psql -U schoolms_user -d schoolms_db -h localhost -W
# Enter password: StrongPassword123
# You should see: schoolms_db=>
```

---

## STEP 3: DJANGO CONFIGURATION & MIGRATION

**Status:** [ ] Not Started [ ] In Progress [ ] Complete

### Set Environment Variable (Permanent):
```powershell
# Run as Administrator
[Environment]::SetEnvironmentVariable('USE_POSTGRESQL', 'true', 'Machine')
# Restart PowerShell/CMD after this
```

### Run Migrations:
```powershell
cd "c:\Users\Admin\Desktop\School management"
python manage.py migrate
```

Expected output: Multiple "OK" messages, ending with "System check: 0 issues"

### Create Superuser:
```powershell
python manage.py createsuperuser
# Email: admin@school.local
# Password: [Strong password - write it down!]
```

### Collect Static Files:
```powershell
python manage.py collectstatic --noinput
```

---

## STEP 4: GUNICORN SETUP (APPLICATION SERVER)

**Status:** [ ] Not Started [ ] In Progress [ ] Complete

### Test Gunicorn:
```powershell
cd "c:\Users\Admin\Desktop\School management"
gunicorn school_management.wsgi:application --bind 127.0.0.1:8000
```

You should see:
```
[INFO] Listening at: http://127.0.0.1:8000 (...)
```

Press Ctrl+C to stop.

### Install NSSM (Service Manager):
1. Download from: https://nssm.cc/download
2. Extract to: `C:\nssm`
3. Add to PATH:
```powershell
# Run as Administrator
[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','Machine') + ';C:\nssm', 'Machine')
```

### Create Windows Service:
```powershell
# Run as Administrator
nssm install SchoolMS C:\Users\Admin\AppData\Local\Programs\Python\Python313\Scripts\gunicorn.exe
```

A dialog appears:
- Path: `C:\Users\Admin\AppData\Local\Programs\Python\Python313\Scripts\gunicorn.exe`
- Arguments: `school_management.wsgi:application --bind 127.0.0.1:8000 --workers 3`
- Startup directory: `C:\Users\Admin\Desktop\School management`
- Click "Install service"

### Verify Service:
```powershell
nssm query SchoolMS
# Should show various settings
nssm status SchoolMS
# Should show: SERVICE_STOPPED (for now)
```

---

## STEP 5: NGINX SETUP (WEB SERVER)

**Status:** [ ] Not Started [ ] In Progress [ ] Complete

### Download Nginx:
1. Go to: http://nginx.org/en/download.html
2. Download nginx/1.27.0 (Windows zip)
3. Extract to: `C:\nginx`

### Configure Nginx:
1. Edit: `C:\nginx\conf\nginx.conf`
2. Find the `server {` block (around line 47)
3. Replace entire block with:

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

4. Save file

### Test Nginx Configuration:
```powershell
C:\nginx\nginx.exe -t
# Should show: the configuration file ... is ok
```

### Create Auto-Start Shortcut:
```powershell
# Create shortcut to nginx
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("C:\Users\Admin\Desktop\nginx.lnk")
$Shortcut.TargetPath = "C:\nginx\nginx.exe"
$Shortcut.Save()

# Move to Startup folder
Move-Item "C:\Users\Admin\Desktop\nginx.lnk" "C:\Users\Admin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\"
```

---

## STEP 6: LOCAL DOMAIN SETUP

**Status:** [ ] Not Started [ ] In Progress [ ] Complete

### Edit Hosts File:
1. Open Notepad as Administrator
2. File → Open → `C:\Windows\System32\drivers\etc\hosts`
3. Add at the end of file:
```
127.0.0.1   schoolms.local
```
4. Save file

### Verify in Django:
Settings.py already configured with:
```python
ALLOWED_HOSTS = ['schoolms.local', 'localhost', '127.0.0.1', '*']
```

---

## STEP 7: START ALL SERVICES

**Status:** [ ] Not Started [ ] In Progress [ ] Complete

### Start Gunicorn Service:
```powershell
# Run as Administrator
nssm start SchoolMS
nssm status SchoolMS
# Should show: SERVICE_RUNNING
```

### Start Nginx:
```powershell
C:\nginx\nginx.exe
# No output = success
```

### Verify Services Running:
```powershell
# Check Gunicorn
nssm status SchoolMS

# Check Nginx
netstat -ano | findstr :80
# Should show processes using port 80

# Check PostgreSQL
Get-Service postgresql-x64-15 | Select-Object Status
# Should show: Status = Running
```

---

## STEP 8: TEST THE SYSTEM

**Status:** [ ] Not Started [ ] In Progress [ ] Complete

### Test in Browser:
1. Open any web browser (Chrome, Edge, Firefox)
2. Type in address bar: `http://schoolms.local`
3. You should see the login page
4. Login with superuser credentials:
   - Email: admin@school.local
   - Password: [from Step 3]

### Expected:
- ✓ Page loads without errors
- ✓ Login works
- ✓ Dashboard accessible
- ✓ No technical URLs visible (just schoolms.local)

---

## STEP 9: TEST AUTO-START ON BOOT

**Status:** [ ] Not Started [ ] In Progress [ ] Complete

### Restart Computer:
```powershell
Restart-Computer
```

### After Restart:
1. Wait 30 seconds for services to start
2. Open browser
3. Go to: `http://schoolms.local`
4. Login and verify everything works

### If it works:
✓ System is production-ready!

### If it doesn't:
1. Check PostgreSQL is running: `Get-Service postgresql-x64-15 | Start-Service`
2. Check Gunicorn: `nssm start SchoolMS`
3. Check Nginx: `C:\nginx\nginx.exe`
4. Try again in browser

---

## STEP 10: BACKUP SETUP

**Status:** [ ] Not Started [ ] In Progress [ ] Complete

### Create Backup Script:
Save as `C:\Users\Admin\Desktop\School management\backup_db.bat`:

```batch
@echo off
setlocal enabledelayedexpansion
set BACKUP_DIR=C:\Users\Admin\Desktop\School management\backups
set TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=!TIMESTAMP: =0!

if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

"C:\Program Files\PostgreSQL\15\bin\pg_dump" -U schoolms_user -d schoolms_db -h localhost > %BACKUP_DIR%\schoolms_db_!TIMESTAMP!.sql

echo Backup completed at %date% %time% >> %BACKUP_DIR%\backup_log.txt
echo Backup file: schoolms_db_!TIMESTAMP!.sql >> %BACKUP_DIR%\backup_log.txt
pause
```

### Test Backup:
```powershell
cd "C:\Users\Admin\Desktop\School management"
.\backup_db.bat
```

A backup file should appear in: `backups/schoolms_db_[date][time].sql`

### Schedule Daily Backup (Optional):
1. Windows Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 2:00 AM
4. Action: Run `backup_db.bat`

---

## TROUBLESHOOTING

### Issue: "Cannot connect to PostgreSQL"
```powershell
Get-Service postgresql-x64-15 | Start-Service
# Wait 5 seconds
psql -U schoolms_user -d schoolms_db -h localhost -W
```

### Issue: "Gunicorn service won't start"
```powershell
nssm stop SchoolMS
nssm start SchoolMS
nssm status SchoolMS
```

### Issue: "Nginx not responding"
```powershell
C:\nginx\nginx.exe -t  # Test config
C:\nginx\nginx.exe -s stop  # Stop
C:\nginx\nginx.exe  # Start again
```

### Issue: "Page shows 502 Bad Gateway"
- Gunicorn not running: `nssm start SchoolMS`
- Check firewall allows 127.0.0.1:8000
- Check Django logs in terminal for errors

### Issue: "Cannot access schoolms.local"
1. Check hosts file: `C:\Windows\System32\drivers\etc\hosts`
2. Verify line: `127.0.0.1   schoolms.local`
3. Restart browser/clear cache
4. Try: `http://127.0.0.1`

---

## COMPLETION CHECKLIST

- [ ] PostgreSQL installed and running as service
- [ ] Database `schoolms_db` created
- [ ] User `schoolms_user` created with password
- [ ] USE_POSTGRESQL environment variable set
- [ ] Django migrations applied
- [ ] Superuser created (admin@school.local)
- [ ] Static files collected
- [ ] Gunicorn service installed and running
- [ ] Nginx installed and configured
- [ ] schoolms.local added to hosts file
- [ ] System accessible at http://schoolms.local
- [ ] Services auto-start on boot (tested with restart)
- [ ] Backup script created and tested

**System Status:** [ ] Development [ ] Testing [ ] Production Ready

**Go-Live Date:** ________________

---

## FOR SCHOOL STAFF

### Daily Usage:
1. Computer turns on
2. Open web browser
3. Type: `schoolms.local`
4. Login
5. Use system normally

### That's it! No technical knowledge needed.

### If something breaks:
1. Restart computer
2. If still broken, call the developer

---

**Document prepared by:** [Your Name]
**Date:** [Today]
**Version:** 1.0
