#!/usr/bin/env python3
"""
Automated PostgreSQL Setup and Migration Script
This script sets up PostgreSQL and migrates your Django data
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def run_command(cmd, description=""):
    """Run a shell command and return success status"""
    if description:
        print(f"▶ {description}...", end=" ", flush=True)
    try:
        # Add PostgreSQL to PATH
        env = os.environ.copy()
        env['PATH'] = r"C:\Program Files\PostgreSQL\18\bin;" + env.get('PATH', '')
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60, env=env)
        if description:
            if result.returncode == 0:
                print("✓")
            else:
                print(f"✗\n{result.stderr}")
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        if description:
            print("✗ (timeout)")
        return False, "", "Command timed out"
    except Exception as e:
        if description:
            print(f"✗\n{str(e)}")
        return False, "", str(e)

def check_postgresql():
    """Check if PostgreSQL is installed"""
    print_section("Step 1: Checking PostgreSQL Installation")
    
    success, _, _ = run_command("psql --version", "Checking PostgreSQL...")
    if success:
        print("✓ PostgreSQL is already installed!\n")
        return True
    else:
        print("✗ PostgreSQL not found\n")
        return False

def wait_for_postgresql(timeout=120):
    """Wait for PostgreSQL service to be ready"""
    print("Waiting for PostgreSQL service to start...", end=" ", flush=True)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        success, _, _ = run_command("psql -U postgres -c 'SELECT 1' > nul 2>&1")
        if success:
            print("✓")
            return True
        time.sleep(2)
    
    print("✗ (timeout)")
    return False

def create_postgresql_user_and_db():
    """Create PostgreSQL user and database"""
    print_section("Step 2: Creating PostgreSQL User and Database")
    
    # Password for PostgreSQL
    pg_password = "postgres123"
    db_user = "school_admin"
    db_name = "school_management_db"
    
    # Connect to default postgres database and create user/db
    commands = [
        f'psql -U postgres -c "DROP DATABASE IF EXISTS {db_name};"',
        f'psql -U postgres -c "DROP USER IF EXISTS {db_user};"',
        f'psql -U postgres -c "CREATE USER {db_user} WITH PASSWORD \'{pg_password}\';"',
        f'psql -U postgres -c "CREATE DATABASE {db_name} OWNER {db_user};"',
        f'psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"',
    ]
    
    for cmd in commands:
        success, _, err = run_command(cmd)
        if not success and "does not exist" not in err.lower():
            print(f"Warning: {err}")
    
    print("✓ PostgreSQL user and database created\n")
    return db_user, db_password, db_name

def backup_sqlite():
    """Backup existing SQLite database"""
    print_section("Step 3: Backing Up SQLite Database")
    
    sqlite_path = Path("db.sqlite3")
    if sqlite_path.exists():
        backup_path = Path("db.sqlite3.backup")
        run_command(f'copy "{sqlite_path}" "{backup_path}"', "Backing up SQLite database")
        print(f"✓ SQLite backup created: {backup_path}\n")
        return True
    else:
        print("✓ No existing SQLite database to backup\n")
        return True

def export_data():
    """Export Django data to JSON"""
    print_section("Step 4: Exporting Django Data")
    
    success, _, err = run_command(
        "python manage.py dumpdata > data_backup.json",
        "Exporting data from SQLite"
    )
    if success:
        print("✓ Data exported to data_backup.json\n")
        return True
    else:
        print(f"Warning: Could not export data: {err}\n")
        return False

def update_settings():
    """Update Django settings to use PostgreSQL"""
    print_section("Step 5: Updating Django Settings")
    
    # Create .env file
    env_content = """USE_POSTGRESQL=True
DB_NAME=school_management_db
DB_USER=school_admin
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✓ Created .env file with PostgreSQL configuration\n")
    return True

def run_migrations():
    """Run Django migrations"""
    print_section("Step 6: Running Django Migrations")
    
    success, _, err = run_command(
        "python manage.py migrate",
        "Running migrations on PostgreSQL"
    )
    if success:
        print("✓ Migrations completed successfully\n")
        return True
    else:
        print(f"✗ Migration failed: {err}\n")
        return False

def load_data():
    """Load exported data into PostgreSQL"""
    print_section("Step 7: Loading Data into PostgreSQL")
    
    success, _, err = run_command(
        "python manage.py loaddata data_backup.json",
        "Loading data into PostgreSQL"
    )
    if success:
        print("✓ Data loaded successfully\n")
        return True
    else:
        print(f"Warning: Could not load data: {err}\n")
        return False

def verify_connection():
    """Verify PostgreSQL connection"""
    print_section("Step 8: Verifying Connection")
    
    success, _, _ = run_command(
        "python manage.py dbshell < nul",
        "Testing PostgreSQL connection"
    )
    if success:
        print("✓ PostgreSQL connection successful\n")
        return True
    else:
        print("✗ Connection failed - check credentials\n")
        return False

def main():
    """Main migration process"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  School Management System - PostgreSQL Migration".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Step 1: Check PostgreSQL
    if not check_postgresql():
        print("\n⚠️  PostgreSQL is not installed.")
        print("Please install PostgreSQL first:")
        print("  1. Download from: https://www.postgresql.org/download/windows/")
        print("  2. Run the installer and set password to: postgres123")
        print("  3. Accept default port: 5432")
        print("  4. Then run this script again\n")
        return False
    
    # Step 2: Wait for service
    if not wait_for_postgresql():
        print("⚠️  PostgreSQL service is not running")
        print("Please start the PostgreSQL service and try again\n")
        return False
    
    # Step 3: Create database
    db_user, db_password, db_name = create_postgresql_user_and_db()
    
    # Step 4: Backup SQLite
    backup_sqlite()
    
    # Step 5: Export data
    export_data()
    
    # Step 6: Update settings
    update_settings()
    
    # Step 7: Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Step 8: Run migrations
    run_migrations()
    
    # Step 9: Load data
    load_data()
    
    # Step 10: Verify
    verify_connection()
    
    print_section("✓ Migration Complete!")
    print("Your Django application is now using PostgreSQL!\n")
    print("Next steps:")
    print("  1. Start your Django server: python manage.py runserver")
    print("  2. Visit: http://localhost:8000")
    print("  3. All your data has been migrated to PostgreSQL\n")
    print("To switch back to SQLite:")
    print("  1. Set USE_POSTGRESQL=False in .env")
    print("  2. Restart the server\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)
