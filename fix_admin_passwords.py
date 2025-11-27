import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Administrator

# Set passwords for all admin accounts
for admin in Administrator.objects.all():
    admin.set_password('AdminPassword123')
    admin.save()
    print(f'✓ Set password for {admin.email}')

print('\n' + '='*60)
print('All admin accounts now use: AdminPassword123')
print('='*60)
