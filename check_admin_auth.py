#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Administrator

# Check if admin@admin.com has a usable password
admin = Administrator.objects.get(email='admin@admin.com')
print(f"Email: {admin.email}")
print(f"Password hash: {admin.password[:50]}...")
print(f"Has usable password: {admin.has_usable_password()}")
print(f"Is staff: {admin.is_staff}")
print(f"Is superuser: {admin.is_superuser}")
print(f"Is active: {admin.is_active}")

# Test password check with a known password
print("\nTesting common passwords:")
test_passwords = ['admin123', 'admin', 'password', '12345678']
for pwd in test_passwords:
    result = admin.check_password(pwd)
    print(f"  check_password('{pwd}'): {result}")

# If password doesn't work, set a known one
print("\n" + "="*60)
print("Setting password to 'admin123' for admin@admin.com...")
admin.set_password('admin123')
admin.save()
print("✓ Password updated to 'admin123'")
print("="*60)
