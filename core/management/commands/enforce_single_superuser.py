"""
Management command to ensure only one superuser exists (Edwin)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

Administrator = get_user_model()

class Command(BaseCommand):
    help = 'Ensure only Edwin is a superuser. Demote all other superusers.'

    def handle(self, *args, **options):
        # Find Edwin
        edwin = Administrator.objects.filter(email='eddy.mavhe@gmail.com').first()
        
        if not edwin:
            self.stdout.write(
                self.style.ERROR('Edwin (eddy.mavhe@gmail.com) not found!')
            )
            return

        # Make sure Edwin is superuser
        if not edwin.is_superuser:
            edwin.is_superuser = True
            edwin.is_staff = True
            edwin.save()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Edwin promoted to superuser')
            )

        # Demote all other superusers
        other_superusers = Administrator.objects.exclude(
            email='eddy.mavhe@gmail.com'
        ).filter(is_superuser=True)

        count = 0
        for admin in other_superusers:
            admin.is_superuser = False
            admin.save()
            count += 1
            self.stdout.write(
                self.style.WARNING(f'✗ Demoted {admin.email} from superuser')
            )

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('✓ Only Edwin is superuser')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Demoted {count} superusers')
            )
