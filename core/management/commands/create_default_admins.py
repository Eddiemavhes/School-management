from django.core.management.base import BaseCommand
from core.models import Administrator


class Command(BaseCommand):
    help = 'Create default admin accounts if they do not exist'

    def handle(self, *args, **options):
        # Default admin accounts
        admins = [
            {
                'email': 'admin@dashboard.com',
                'password': 'admin123',
                'description': 'Admin Dashboard Account'
            },
            {
                'email': 'admin@school.com',
                'password': 'admin123',
                'description': 'School Admin Account'
            }
        ]

        for admin_data in admins:
            try:
                # Use get_or_create to avoid duplicates
                admin, created = Administrator.objects.get_or_create(
                    email=admin_data['email'],
                    defaults={
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True,
                    }
                )
                
                if created:
                    # Set password for new accounts
                    admin.set_password(admin_data['password'])
                    admin.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created: {admin_data["email"]} ({admin_data["description"]})'
                        )
                    )
                else:
                    # Reset password for existing accounts (in case it was wrong)
                    admin.set_password(admin_data['password'])
                    admin.save()
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Updated: {admin_data["email"]} ({admin_data["description"]})'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error with {admin_data["email"]}: {str(e)}')
                )
