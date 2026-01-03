from django.db import migrations


def create_ecd_profiles(apps, schema_editor):
    Class = apps.get_model('core', 'Class')
    ECDClassProfile = apps.get_model('core', 'ECDClassProfile')

    ecd_classes = Class.objects.filter(grade='ECD')
    created = 0
    for cls in ecd_classes:
        profile, was_created = ECDClassProfile.objects.get_or_create(
            cls_id=cls.id,
            defaults={
                'capacity': 30,
                'premium': False,
                'meal_plan_fee': '0.00',
                'nappies_fee': '0.00',
                'materials_fee': '0.00',
            }
        )
        if was_created:
            created += 1


def remove_ecd_profiles(apps, schema_editor):
    Class = apps.get_model('core', 'Class')
    ECDClassProfile = apps.get_model('core', 'ECDClassProfile')

    ecd_classes = Class.objects.filter(grade='ECD')
    for cls in ecd_classes:
        try:
            profile = ECDClassProfile.objects.get(cls_id=cls.id)
            profile.delete()
        except ECDClassProfile.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0052_alter_class_grade_ecdclassprofile_ecdclassfee'),
    ]

    operations = [
        migrations.RunPython(create_ecd_profiles, remove_ecd_profiles),
    ]
