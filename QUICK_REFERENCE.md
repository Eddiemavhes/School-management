# QUICK REFERENCE - Windows Production Setup Commands

## All Commands in One Place

---

## POSTGRESQL SETUP

### Test if running:
```powershell
Get-Service postgresql-x64-15 | Select-Object Status
```

### Start if stopped:
```powershell
Get-Service postgresql-x64-15 | Start-Service
```

### Connect to database:
```powershell
psql -U schoolms_user -d schoolms_db -h localhost -W
# Password: StrongPassword123
# Exit with: \q
```

### Create database (in pgAdmin):
```sql
CREATE DATABASE schoolms_db;
CREATE USER schoolms_user WITH PASSWORD 'StrongPassword123';
GRANT ALL PRIVILEGES ON DATABASE schoolms_db TO schoolms_user;
```

---

## DJANGO SETUP

### Set environment variable (permanent):
```powershell
[Environment]::SetEnvironmentVariable('USE_POSTGRESQL', 'true', 'Machine')
```

### Test Django with PostgreSQL:
```powershell
cd "c:\Users\Admin\Desktop\School management"
python manage.py test tests.test_system -v 1
```

### Run migrations:
```powershell
python manage.py migrate
```

### Create superuser:
```powershell
python manage.py createsuperuser
# Email: admin@school.local
# Password: [choose strong]
```

### Collect static files:
```powershell
python manage.py collectstatic --noinput
```

---

## GUNICORN SETUP

### Test Gunicorn:
```powershell
cd "c:\Users\Admin\Desktop\School management"
gunicorn school_management.wsgi:application --bind 127.0.0.1:8000
# Ctrl+C to stop
```

### Install Windows service:
```powershell
nssm install SchoolMS C:\Users\Admin\AppData\Local\Programs\Python\Python313\Scripts\gunicorn.exe
# Dialog:
# Arguments: school_management.wsgi:application --bind 127.0.0.1:8000 --workers 3
# Startup directory: C:\Users\Admin\Desktop\School management
```

### Start service:
```powershell
nssm start SchoolMS
```

### Stop service:
```powershell
nssm stop SchoolMS
```

### Restart service:
```powershell
nssm restart SchoolMS
```

### Check status:
```powershell
nssm status SchoolMS
```

### View service details:
```powershell
nssm query SchoolMS
```

---

## NGINX SETUP

### Test configuration:
```powershell
C:\nginx\nginx.exe -t
```

### Start Nginx:
```powershell
C:\nginx\nginx.exe
```

### Stop Nginx:
```powershell
C:\nginx\nginx.exe -s stop
```

### Reload configuration (without restart):
```powershell
C:\nginx\nginx.exe -s reload
```

### Check if running:
```powershell
netstat -ano | findstr :80
# If running, will show process ID (PID)
```

---

## LOCAL DOMAIN SETUP

### Edit hosts file:
```powershell
notepad C:\Windows\System32\drivers\etc\hosts
# Add: 127.0.0.1   schoolms.local
# Save file
```

### Test domain resolution:
```powershell
nslookup schoolms.local
# Or ping
ping schoolms.local
```

---

## BACKUP & RESTORE

### Create backup:
```powershell
"C:\Program Files\PostgreSQL\15\bin\pg_dump" -U schoolms_user -d schoolms_db -h localhost > C:\backup_$(Get-Date -Format yyyyMMdd_HHmmss).sql
```

### List backups:
```powershell
dir "C:\Users\Admin\Desktop\School management\backups\"
```

### Restore from backup:
```powershell
psql -U schoolms_user -d schoolms_db -h localhost < C:\backup_file_name.sql
```

---

## VERIFICATION & TESTING

### Verify all services running:
```powershell
# PostgreSQL
Get-Service postgresql-x64-15 | Select-Object Status

# Gunicorn
nssm status SchoolMS

# Nginx
netstat -ano | findstr :80

# All ports
netstat -ano | findstr ":80\|:8000\|:5432"
```

### Test web application:
Open browser and go to: `http://schoolms.local`

### Run system tests:
```powershell
cd "c:\Users\Admin\Desktop\School management"
python manage.py test tests.test_system -v 2
```

### Check Django logs (if errors):
Look for error messages in Command Prompt window where Gunicorn is running

---

## TROUBLESHOOTING QUICK FIXES

### "Cannot connect to database"
```powershell
# 1. Check PostgreSQL is running
Get-Service postgresql-x64-15 | Start-Service

# 2. Test connection
psql -U schoolms_user -d schoolms_db -h localhost -W

# 3. Check firewall
# Windows Defender Firewall → Allow PostgreSQL through
```

### "Service won't start"
```powershell
# 1. Check service config
nssm query SchoolMS

# 2. Stop and restart
nssm stop SchoolMS
nssm start SchoolMS

# 3. Check status
nssm status SchoolMS
```

### "Nginx not working"
```powershell
# 1. Test config
C:\nginx\nginx.exe -t

# 2. Stop and restart
C:\nginx\nginx.exe -s stop
C:\nginx\nginx.exe

# 3. Check port
netstat -ano | findstr :80
```

### "Page shows 502 Bad Gateway"
```powershell
# 1. Check Gunicorn running
nssm status SchoolMS

# 2. Check Django process
netstat -ano | findstr :8000

# 3. Restart if needed
nssm restart SchoolMS
```

### "Cannot access schoolms.local"
```powershell
# 1. Check hosts file
type C:\Windows\System32\drivers\etc\hosts

# 2. Test DNS
ping schoolms.local

# 3. Try IP directly
# Browser: http://127.0.0.1

# 4. Reload hosts file
ipconfig /flushdns
```

---

## AUTO-START SETUP

### Make Gunicorn auto-start:
```powershell
# Already configured with nssm install
# Verify with:
nssm query SchoolMS | findstr Start
# Should show: Start = SERVICE_AUTO_START
```

### Make Nginx auto-start:
```powershell
# Create shortcut to C:\nginx\nginx.exe
# Move to: C:\Users\Admin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
```

### Make PostgreSQL auto-start:
```powershell
# Already configured by PostgreSQL installer
# Verify with:
Get-Service postgresql-x64-15 | Select-Object StartType
# Should show: StartType = Automatic
```

### Test auto-start:
```powershell
# Restart computer
Restart-Computer

# After restart, check:
Get-Service postgresql-x64-15 | Select-Object Status
nssm status SchoolMS
netstat -ano | findstr :80
```

---

## COMMON PATHS

| Item | Path |
|------|------|
| Django Project | C:\Users\Admin\Desktop\School management |
| PostgreSQL Data | C:\Program Files\PostgreSQL\15\data |
| PostgreSQL Bin | C:\Program Files\PostgreSQL\15\bin |
| Nginx | C:\nginx |
| Nginx Config | C:\nginx\conf\nginx.conf |
| NSSM | C:\nssm |
| Python | C:\Users\Admin\AppData\Local\Programs\Python\Python313 |
| Backups | C:\Users\Admin\Desktop\School management\backups |
| Tests | C:\Users\Admin\Desktop\School management\tests\test_system.py |

---

## ENVIRONMENT VARIABLES

### Check current:
```powershell
$env:USE_POSTGRESQL
$env:DB_NAME
$env:DB_USER
$env:DB_PASSWORD
$env:DB_HOST
$env:DB_PORT
```

### Set temporary (current session only):
```powershell
$env:USE_POSTGRESQL='true'
$env:DB_PASSWORD='StrongPassword123'
```

### Set permanent (all sessions):
```powershell
[Environment]::SetEnvironmentVariable('USE_POSTGRESQL', 'true', 'Machine')
[Environment]::SetEnvironmentVariable('DB_PASSWORD', 'StrongPassword123', 'Machine')
```

---

## USEFUL POWERSHELL ALIASES

### Create convenient shortcuts:
```powershell
# Add to PowerShell profile
Set-Alias check-pg "Get-Service postgresql-x64-15 | Select-Object Status"
Set-Alias check-sms "nssm status SchoolMS"
Set-Alias restart-sms "nssm restart SchoolMS"
Set-Alias check-web "netstat -ano | findstr :80"
Set-Alias cd-project "cd C:\Users\Admin\Desktop\School management"
```

---

## EMERGENCY RESTORE (If everything breaks)

```powershell
# 1. Stop all services
nssm stop SchoolMS
C:\nginx\nginx.exe -s stop
Get-Service postgresql-x64-15 | Stop-Service

# 2. Check backups exist
dir "C:\Users\Admin\Desktop\School management\backups\"

# 3. Start PostgreSQL only
Get-Service postgresql-x64-15 | Start-Service

# 4. Restore database
psql -U schoolms_user -d schoolms_db -h localhost < "backup_file_name.sql"

# 5. Restart Gunicorn and Nginx
nssm start SchoolMS
C:\nginx\nginx.exe

# 6. Test
# Browser: http://schoolms.local
```

---

## REFERENCE DOCUMENTATION FILES

| File | Contains |
|------|----------|
| PRODUCTION_DEPLOYMENT_SUMMARY.md | Overview and timeline |
| PRODUCTION_SETUP_CHECKLIST.md | Step-by-step detailed setup |
| DEPLOYMENT_GUIDE.md | Full deployment instructions |
| setup_production.bat | Automated setup script |
| backup_db.bat | Backup script |
| tests/test_system.py | 30 system tests |

---

**Use this file as a quick reference during setup and troubleshooting.**

**For detailed explanations, see the full documentation files.**

**Last updated:** December 17, 2025
