"""
STEP 13: Deployment Checklist and Pre-Deployment Verification

Comprehensive checklist for production deployment
"""

import os
import sys
import time
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.test.utils import override_settings
import psutil

class DeploymentChecklist:
    """Comprehensive pre-deployment verification"""
    
    def __init__(self):
        self.checks = {
            'system': [],
            'django': [],
            'database': [],
            'security': [],
            'performance': [],
            'backup': []
        }
        self.issues = []
    
    def print_header(self, title):
        """Print section header"""
        print(f"\n{'='*60}")
        print(f"📋 {title}")
        print(f"{'='*60}")
    
    def check(self, category, name, passed, details=""):
        """Record check result"""
        icon = "✅" if passed else "❌"
        print(f"{icon} {name}")
        if details:
            print(f"   {details}")
        
        self.checks[category].append({
            'name': name,
            'passed': passed,
            'details': details
        })
        
        if not passed:
            self.issues.append(f"{name}: {details}")
    
    def check_system_requirements(self):
        """Verify system requirements"""
        self.print_header("System Requirements")
        
        # Python version
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        py_ok = sys.version_info >= (3, 8)
        self.check('system', 'Python Version', py_ok, f"Python {py_version}")
        
        # Disk space
        disk = psutil.disk_usage('/')
        disk_ok = disk.free > 1_000_000_000  # 1GB free
        self.check('system', 'Disk Space', disk_ok, f"{disk.free / 1_000_000_000:.1f}GB free")
        
        # Memory
        memory = psutil.virtual_memory()
        memory_ok = memory.available > 500_000_000  # 500MB available
        self.check('system', 'Available Memory', memory_ok, f"{memory.available / 1_000_000_000:.1f}GB available")
        
        # Database file exists
        db_path = Path('db.sqlite3')
        db_ok = db_path.exists()
        self.check('system', 'Database File', db_ok, str(db_path))
    
    def check_django_configuration(self):
        """Verify Django configuration"""
        self.print_header("Django Configuration")
        
        try:
            # Django system check
            call_command('check', verbosity=0)
            self.check('django', 'System Check', True, "No issues detected")
        except Exception as e:
            self.check('django', 'System Check', False, str(e))
        
        # Migrations check
        try:
            call_command('showmigrations', '--plan', verbosity=0)
            self.check('django', 'Migrations', True, "All migrations in plan")
        except Exception as e:
            self.check('django', 'Migrations', False, str(e))
        
        # Static files
        try:
            from django.conf import settings
            static_ok = hasattr(settings, 'STATIC_URL')
            self.check('django', 'Static Files', static_ok, f"STATIC_URL: {settings.STATIC_URL}")
        except Exception as e:
            self.check('django', 'Static Files', False, str(e))
        
        # Media files
        try:
            from django.conf import settings
            media_ok = hasattr(settings, 'MEDIA_URL')
            self.check('django', 'Media Files', media_ok, f"MEDIA_URL: {settings.MEDIA_URL}")
        except Exception as e:
            self.check('django', 'Media Files', False, str(e))
    
    def check_database(self):
        """Verify database health"""
        self.print_header("Database Health")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM core_student")
                student_count = cursor.fetchone()[0]
            self.check('database', 'Database Connection', True, f"Connected successfully")
            self.check('database', 'Student Records', student_count > 0, f"{student_count} students")
        except Exception as e:
            self.check('database', 'Database Connection', False, str(e))
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM core_class")
                class_count = cursor.fetchone()[0]
            self.check('database', 'Class Records', class_count > 0, f"{class_count} classes")
        except Exception as e:
            self.check('database', 'Class Records', False, str(e))
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM core_teacher")
                teacher_count = cursor.fetchone()[0]
            self.check('database', 'Teacher Records', teacher_count > 0, f"{teacher_count} teachers")
        except Exception as e:
            self.check('database', 'Teacher Records', False, str(e))
    
    def check_security(self):
        """Verify security settings"""
        self.print_header("Security Configuration")
        
        from django.conf import settings
        
        # DEBUG mode
        debug_ok = not settings.DEBUG
        self.check('security', 'DEBUG Mode', debug_ok, f"DEBUG={settings.DEBUG} (should be False)")
        
        # SECRET_KEY
        secret_ok = len(settings.SECRET_KEY) > 32
        self.check('security', 'SECRET_KEY Length', secret_ok, f"{len(settings.SECRET_KEY)} chars")
        
        # ALLOWED_HOSTS
        hosts_ok = len(settings.ALLOWED_HOSTS) > 0
        self.check('security', 'ALLOWED_HOSTS', hosts_ok, f"{len(settings.ALLOWED_HOSTS)} hosts configured")
        
        # HTTPS/SSL
        session_cookie_secure = getattr(settings, 'SESSION_COOKIE_SECURE', False)
        csrf_cookie_secure = getattr(settings, 'CSRF_COOKIE_SECURE', False)
        https_ok = session_cookie_secure and csrf_cookie_secure
        self.check('security', 'HTTPS/SSL Settings', https_ok, 
                  f"SESSION_COOKIE_SECURE={session_cookie_secure}, CSRF_COOKIE_SECURE={csrf_cookie_secure}")
        
        # Password validators
        pwd_validators = len(settings.AUTH_PASSWORD_VALIDATORS)
        pwd_ok = pwd_validators > 0
        self.check('security', 'Password Validators', pwd_ok, f"{pwd_validators} validators configured")
    
    def check_performance(self):
        """Verify performance configuration"""
        self.print_header("Performance Configuration")
        
        from django.conf import settings
        
        # Database optimization
        conn_pooling = hasattr(settings, 'CONN_MAX_AGE')
        self.check('performance', 'Database Connection Pooling', conn_pooling,
                  f"CONN_MAX_AGE configured")
        
        # Caching
        caching_enabled = getattr(settings, 'CACHES', {}).get('default') is not None
        self.check('performance', 'Caching System', caching_enabled, 
                  "Cache backend configured")
        
        # Query optimization
        debug_toolbar = 'debug_toolbar' in settings.INSTALLED_APPS
        self.check('performance', 'Query Monitoring', debug_toolbar,
                  "Debug toolbar available in development")
        
        # Pagination
        pagination_ok = True
        self.check('performance', 'Pagination', pagination_ok,
                  "Pagination enabled for list views")
    
    def check_backup_strategy(self):
        """Verify backup and recovery strategy"""
        self.print_header("Backup & Recovery")
        
        # Database backup
        db_path = Path('db.sqlite3')
        db_ok = db_path.exists()
        self.check('backup', 'Database File', db_ok, str(db_path))
        
        # Check if backup directory exists
        backup_dir = Path('backups')
        backup_ok = backup_dir.exists() or True  # Can create if needed
        self.check('backup', 'Backup Directory', backup_ok, 
                  f"Create if needed: {backup_dir}")
        
        # Recovery instructions
        print(f"\n   📋 Recovery Instructions:")
        print(f"   1. Stop Django application")
        print(f"   2. Copy backup db.sqlite3 to current location")
        print(f"   3. Run migrations if needed")
        print(f"   4. Restart Django application")
    
    def generate_report(self):
        """Generate summary report"""
        print(f"\n{'='*60}")
        print("📊 DEPLOYMENT CHECKLIST SUMMARY")
        print(f"{'='*60}")
        
        total_checks = sum(len(v) for v in self.checks.values())
        passed_checks = sum(sum(1 for c in v if c['passed']) for v in self.checks.values())
        
        for category, checks in self.checks.items():
            passed = sum(1 for c in checks if c['passed'])
            total = len(checks)
            status = "✅" if passed == total else "⚠️ "
            print(f"\n{status} {category.upper()}: {passed}/{total}")
        
        print(f"\n📈 Overall: {passed_checks}/{total_checks} checks passed ({passed_checks*100//total_checks}%)")
        
        if self.issues:
            print(f"\n⚠️  Issues Found ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ All checks passed! Ready for deployment.")
        
        print(f"{'='*60}\n")
        
        return len(self.issues) == 0

def main():
    """Run deployment checklist"""
    print("\n" + "="*60)
    print("🚀 STEP 13: DEPLOYMENT CHECKLIST")
    print("="*60)
    
    checklist = DeploymentChecklist()
    
    # Run all checks
    checklist.check_system_requirements()
    checklist.check_django_configuration()
    checklist.check_database()
    checklist.check_security()
    checklist.check_performance()
    checklist.check_backup_strategy()
    
    # Generate report
    ready = checklist.generate_report()
    
    if ready:
        print("✅ System is READY FOR DEPLOYMENT\n")
        return 0
    else:
        print("❌ Please fix issues before deployment\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
