from django.core.management.base import BaseCommand
from core.models import Administrator


class Command(BaseCommand):
    help = 'Create default admin accounts if they do not exist'

    def handle(self, *args, **options):
        # Default admin accounts
        admins = [
            {
                'email': 'admin@dashboard.com',
                'username': 'admin_dashboard',
                'password': 'admin123',
                'description': 'Admin Dashboard Account'
            },
            {
                'email': 'admin@school.com',
                'username': 'admin_school',
                'password': 'admin123',
                'description': 'School Admin Account'
            }
        ]

        for admin_data in admins:
            if not Administrator.objects.filter(email=admin_data['email']).exists():
                try:
                    admin = Administrator.objects.create_user(
                        email=admin_data['email'],
                        username=admin_data['username'],
                        password=admin_data['password'],
                        is_staff=True,
                        is_superuser=True,
                        is_active=True
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created admin account: {admin_data["email"]} - {admin_data["description"]}'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to create {admin_data["email"]}: {str(e)}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Admin account already exists: {admin_data["email"]}')
                )
