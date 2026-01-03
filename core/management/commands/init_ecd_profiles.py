from django.core.management.base import BaseCommand
from core.models import Class, ECDClassProfile


class Command(BaseCommand):
    help = 'Initialize ECDClassProfile records for existing ECD classes with sensible defaults'

    def handle(self, *args, **options):
        ecd_classes = Class.objects.filter(grade='ECD')
        created = 0
        for cls in ecd_classes:
            profile, was_created = ECDClassProfile.objects.get_or_create(
                cls=cls,
                defaults={
                    'capacity': 30,
                    'premium': False,
                    'meal_plan_fee': 0.00,
                    'nappies_fee': 0.00,
                    'materials_fee': 0.00,
                }
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Initialized {created} ECDClassProfile records'))
