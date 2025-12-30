# Generated migration to add ECDA and ECDB support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_alter_class_options'),  # Adjust to your latest migration
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='grade',
            field=models.CharField(
                choices=[
                    ('ECDA', 'ECDA (Early Childhood A)'),
                    ('ECDB', 'ECDB (Early Childhood B)'),
                    (1, 'Grade 1'),
                    (2, 'Grade 2'),
                    (3, 'Grade 3'),
                    (4, 'Grade 4'),
                    (5, 'Grade 5'),
                    (6, 'Grade 6'),
                    (7, 'Grade 7'),
                ],
                max_length=4,
            ),
        ),
    ]
