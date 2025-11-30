# PostgreSQL Migration Guide for School Management System

## Step 1: Install PostgreSQL

### Option A: Windows Installer (Recommended)
1. Download from: https://www.postgresql.org/download/windows/
2. Run the installer and follow the setup wizard
3. Remember your superuser password (default user: postgres)
4. Keep the default port 5432

### Option B: Chocolatey (if installed)
```powershell
choco install postgresql
```

## Step 2: Create Database and User

After installation, open PostgreSQL command line or use pgAdmin:

```sql
-- Create database
CREATE DATABASE school_management_db;

-- Create user
CREATE USER school_admin WITH PASSWORD 'your_secure_password';

-- Grant privileges
ALTER ROLE school_admin SET client_encoding TO 'utf8';
ALTER ROLE school_admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE school_admin SET default_transaction_deferrable TO on;
ALTER ROLE school_admin SET default_timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE school_management_db TO school_admin;
```

## Step 3: Install Python PostgreSQL Adapter

```powershell
pip install psycopg2-binary
```

## Step 4: Update Django Settings

Change the DATABASES configuration in `school_management/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'school_management_db',
        'USER': 'school_admin',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Step 5: Backup SQLite Data (Optional)

Before migrating, backup your current SQLite database:
```powershell
Copy-Item -Path "db.sqlite3" -Destination "db.sqlite3.backup"
```

## Step 6: Run Migrations

```powershell
python manage.py migrate
```

## Step 7: Dump Data from SQLite and Load to PostgreSQL

```powershell
# Export data from SQLite
python manage.py dumpdata > data_backup.json

# Load data into PostgreSQL
python manage.py loaddata data_backup.json
```

## Step 8: Verify Connection

```powershell
python manage.py dbshell
```

This should open a PostgreSQL prompt if connection is successful.

## Troubleshooting

1. **Connection refused**: Make sure PostgreSQL service is running
2. **Password authentication failed**: Verify credentials in settings.py
3. **psycopg2 import error**: Run `pip install psycopg2-binary`
4. **Port already in use**: Change PORT in settings to 5433 or another available port

## Going Back to SQLite

If you need to revert:
1. Change DATABASES back in settings.py
2. Run `python manage.py migrate` (Django will handle schema)
3. Load backup data if needed
