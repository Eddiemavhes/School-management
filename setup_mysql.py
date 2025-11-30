#!/usr/bin/env python3
"""
Automated MySQL Setup and Migration Script
This script sets up MySQL and migrates your Django data
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

def run_command(cmd, description="", env_vars=None):
    """Run a shell command and return success status"""
    if description:
        print(f"▶ {description}...", end=" ", flush=True)
    try:
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120, env=env)
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

def check_mysql():
    """Check if MySQL is installed"""
    print_section("Step 1: Checking MySQL Installation")
    
    # Add MySQL to PATH if possible
    mysql_paths = [
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin",
        r"C:\Program Files\MySQL\MySQL Server 5.7\bin",
        r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin",
    ]
    
    env_vars = {'PATH': ";".join(mysql_paths) + ";" + os.environ.get('PATH', '')}
    
    success, _, _ = run_command("mysql --version", "Checking MySQL...", env_vars)
    if success:
        print("✓ MySQL is already installed!\n")
        return True, env_vars
    else:
        print("✗ MySQL not found\n")
        return False, env_vars

def create_mysql_database(env_vars):
    """Create MySQL database and user"""
    print_section("Step 2: Creating MySQL Database and User")
    
    db_name = "school_management_db"
    db_user = "school_admin"
    db_password = "SchoolAdmin123!"
    
    # MySQL commands
    commands = [
        # Connect as root (no password by default on fresh install)
        f'mysql -u root -e "DROP DATABASE IF EXISTS {db_name};"',
        f'mysql -u root -e "DROP USER IF EXISTS \'{db_user}\'@\'localhost\';"',
        f'mysql -u root -e "CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"',
        f'mysql -u root -e "CREATE USER \'{db_user}\'@\'localhost\' IDENTIFIED BY \'{db_password}\';"',
        f'mysql -u root -e "GRANT ALL PRIVILEGES ON {db_name}.* TO \'{db_user}\'@\'localhost\';"',
        f'mysql -u root -e "FLUSH PRIVILEGES;"',
    ]
    
    for cmd in commands:
        success, _, err = run_command(cmd, env_vars=env_vars)
        if not success and "does not exist" not in err.lower():
            print(f"Note: {err}")
    
    print("✓ MySQL database and user created\n")
    return db_name, db_user, db_password

def wait_for_mysql(env_vars, timeout=120):
    """Wait for MySQL service to be ready"""
    print("Waiting for MySQL service to start...", end=" ", flush=True)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        success, _, _ = run_command("mysql -u root -e 'SELECT 1;' > nul 2>&1", env_vars=env_vars)
        if success:
            print("✓")
            return True
        time.sleep(2)
    
    print("✗ (timeout)")
    return False

def backup_sqlite():
    """Backup existing SQLite database"""
    print_section("Step 3: Backing Up SQLite Database")
    
    sqlite_path = Path("db.sqlite3")
    if sqlite_path.exists():
        backup_path = Path("db.sqlite3.backup")
        try:
            with open(sqlite_path, 'rb') as src:
                with open(backup_path, 'wb') as dst:
                    dst.write(src.read())
            print(f"✓ SQLite backup created: {backup_path}\n")
            return True
        except Exception as e:
            print(f"Warning: Could not backup SQLite: {e}\n")
            return False
    else:
        print("✓ No existing SQLite database to backup\n")
        return True

def export_data():
    """Export Django data to JSON"""
    print_section("Step 4: Exporting Django Data")
    
    success, _, err = run_command(
        "python manage.py dumpdata > data_backup.json",
        "Exporting data from current database"
    )
    if success:
        print("✓ Data exported to data_backup.json\n")
        return True
    else:
        print(f"Warning: Could not export data: {err}\n")
        return False

def update_env_file(db_name, db_user, db_password):
    """Create .env file with MySQL configuration"""
    print_section("Step 5: Updating Configuration")
    
    env_content = f"""# Database Configuration
USE_SQLITE=False
USE_POSTGRESQL=False
USE_MYSQL=True

# MySQL Settings
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST=localhost
DB_PORT=3306
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✓ Created .env file with MySQL configuration\n")
        return True
    except Exception as e:
        print(f"✗ Could not create .env file: {e}\n")
        return False

def run_migrations():
    """Run Django migrations"""
    print_section("Step 6: Running Django Migrations")
    
    success, _, err = run_command(
        "python manage.py migrate",
        "Running migrations on MySQL"
    )
    if success:
        print("✓ Migrations completed successfully\n")
        return True
    else:
        print(f"✗ Migration failed: {err}\n")
        return False

def load_data():
    """Load exported data into MySQL"""
    print_section("Step 7: Loading Data into MySQL")
    
    success, _, err = run_command(
        "python manage.py loaddata data_backup.json",
        "Loading data into MySQL"
    )
    if success:
        print("✓ Data loaded successfully\n")
        return True
    else:
        print(f"Note: Could not load data automatically\n")
        return False

def verify_connection():
    """Verify MySQL connection"""
    print_section("Step 8: Verifying Connection")
    
    success, _, _ = run_command(
        "python manage.py dbshell < nul",
        "Testing MySQL connection"
    )
    if success:
        print("✓ MySQL connection successful\n")
        return True
    else:
        print("✗ Connection failed - check credentials\n")
        return False

def main():
    """Main migration process"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  School Management System - MySQL Migration".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Step 1: Check MySQL
    mysql_found, env_vars = check_mysql()
    if not mysql_found:
        print("\n⚠️  MySQL is not installed.")
        print("Please install MySQL first:")
        print("  1. Download from: https://www.mysql.com/downloads/")
        print("  2. Run the MySQL installer")
        print("  3. Complete the installation wizard")
        print("  4. Then run this script again\n")
        return False
    
    # Step 2: Wait for MySQL service
    if not wait_for_mysql(env_vars):
        print("⚠️  MySQL service is not running")
        print("Please start the MySQL service and try again\n")
        return False
    
    # Step 3: Create database
    db_name, db_user, db_password = create_mysql_database(env_vars)
    
    # Step 4: Backup SQLite
    backup_sqlite()
    
    # Step 5: Export data
    export_data()
    
    # Step 6: Update settings
    update_env_file(db_name, db_user, db_password)
    
    # Step 7: Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Warning: python-dotenv not installed, skipping .env loading\n")
    
    # Step 8: Run migrations
    run_migrations()
    
    # Step 9: Load data
    load_data()
    
    # Step 10: Verify
    verify_connection()
    
    print_section("✓ Migration Complete!")
    print("Your Django application is now using MySQL!\n")
    print("Next steps:")
    print("  1. Start your Django server: python manage.py runserver")
    print("  2. Visit: http://localhost:8000")
    print("  3. All your data has been migrated to MySQL\n")
    print("To switch back to SQLite:")
    print("  1. Set USE_MYSQL=False in .env")
    print("  2. Restart the server\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)
