from django.core.management.base import BaseCommand
from core.models import Administrator

class Command(BaseCommand):
    help = 'Creates a default admin user'

    def handle(self, *args, **kwargs):
        if not Administrator.objects.filter(email='admin@admin.com').exists():
            admin = Administrator.objects.create_user(
                email='admin@admin.com',
                password='admin',
                first_name='Admin',
                last_name='User',
                phone_number='1234567890'
            )
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write(self.style.SUCCESS('Successfully created admin user'))