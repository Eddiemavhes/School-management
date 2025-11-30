# Database Configuration Reference

Your School Management system now supports **3 different databases**. Choose based on your needs:

## Quick Comparison

| Feature | SQLite | MySQL/MariaDB | PostgreSQL |
|---------|--------|---------------|------------|
| **Installation** | Built-in (✓) | Separate install | Separate install |
| **Best For** | Development/Testing | Production Web Apps | Enterprise Apps |
| **Performance** | Single user | Multiple users | Very high throughput |
| **Scalability** | ⭐ Limited | ⭐⭐⭐ Good | ⭐⭐⭐⭐ Excellent |
| **Setup Time** | None | 10 mins | 10 mins |
| **Data Size** | Up to 100GB | Unlimited | Unlimited |
| **Concurrent Users** | 1-2 | 100+ | 1000+ |
| **Learning Curve** | None | Easy | Medium |

---

## Current Status

Your application is currently using: **SQLite** (default)

---

## How to Switch Databases

### Method 1: Using Environment Variables (.env)

Create/Edit `.env` file in project root:

```bash
# For SQLite (DEFAULT - no .env needed)
# Just delete .env file or comment everything out

# For MySQL
USE_MYSQL=True
DB_NAME=school_management_db
DB_USER=school_admin
DB_PASSWORD=SchoolAdmin123!
DB_HOST=localhost
DB_PORT=3306

# For PostgreSQL
USE_POSTGRESQL=True
DB_NAME=school_management_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432
```

### Method 2: Run Setup Scripts

```powershell
# For MySQL
python setup_mysql.py

# For PostgreSQL
python setup_postgresql.py
```

These scripts will:
- Check if database is installed
- Create database and user
- Backup existing data
- Run migrations
- Load data automatically

---

## Installation Instructions

### SQLite
✓ **Already installed** - no action needed

### MySQL/MariaDB (Recommended for Production)

**Download:**
- MySQL: https://dev.mysql.com/downloads/mysql/
- MariaDB: https://mariadb.org/download/ (easier)

**Install:**
1. Run installer
2. Complete setup wizard
3. Remember port (default 3306)

**Then run:**
```powershell
python setup_mysql.py
```

### PostgreSQL (Enterprise-Grade)

**Download:** https://www.postgresql.org/download/windows/

**Install:**
1. Run installer
2. Remember superuser password
3. Note port (default 5432)

**Then run:**
```powershell
python setup_postgresql.py
```

---

## Step-by-Step: Switch to MySQL

1. **Install MySQL/MariaDB**
   - Download and run installer
   - Accept defaults (port 3306)

2. **Update `.env` file**
   ```
   USE_MYSQL=True
   DB_NAME=school_management_db
   DB_USER=school_admin
   DB_PASSWORD=SchoolAdmin123!
   DB_HOST=localhost
   DB_PORT=3306
   ```

3. **Run setup**
   ```powershell
   python setup_mysql.py
   ```

4. **Verify**
   ```powershell
   python manage.py dbshell
   ```

5. **Start server**
   ```powershell
   python manage.py runserver
   ```

---

## Troubleshooting

### MySQL Won't Connect
```powershell
# Check if MySQL is running
Get-Service MySQL80  # (or check Windows Services)

# Check connection
mysql -u root
```

### PostgreSQL Won't Connect
```powershell
# Verify service
Get-Service postgresql-x64-18

# Check port
netstat -ano | findstr :5432
```

### Charset Issues
- SQLite: Handles automatically
- MySQL: Uses utf8mb4 (recommended)
- PostgreSQL: Uses UTF8 by default

### Data Not Migrating
All scripts include automatic backup:
- `db.sqlite3.backup` - SQLite backup
- `data_backup.json` - Full data export

---

## Migration Path

```
SQLite → MySQL
  ↓
MySQL → PostgreSQL
  ↓
PostgreSQL → SQLite (if needed)
```

All scripts handle data migration automatically.

---

## For Development vs Production

### Development (SQLite)
- No installation
- Fast setup
- Single-user
- Perfect for testing

### Staging/Production (MySQL or PostgreSQL)
- Easy setup with scripts
- Multiple concurrent users
- Data persistence
- Professional grade

---

## Support

All setup scripts include:
- Automatic error handling
- Data backup before migration
- Detailed progress output
- Troubleshooting hints

If issues occur, check:
1. Is database service running?
2. Are credentials correct in `.env`?
3. Is port available?
4. Check `data_backup.json` exists (data safety)

---

## Current Configuration

**File: `school_management/settings.py`**

The application reads `.env` file and automatically:
- Detects which database to use
- Sets connection parameters
- Configures charset/encoding
- Sets optimal defaults

**No code changes needed** - just update `.env`!

---

## Next Steps

Choose your database:

1. **Stay with SQLite** (quickest)
   - Just run the app: `python manage.py runserver`

2. **Switch to MySQL** (recommended for production)
   - Run: `python setup_mysql.py`

3. **Switch to PostgreSQL** (enterprise)
   - Run: `python setup_postgresql.py`

All your data will be preserved in migration!
