# Generated migration to add ECD (Early Childhood Development) support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_rename_arrears_vau_student_idx_arrears_vau_student_7d1f5d_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='grade',
            field=models.CharField(
                choices=[
                    ('ECD', 'ECD (Early Childhood Development)'),
                    ('1', 'Grade 1'),
                    ('2', 'Grade 2'),
                    ('3', 'Grade 3'),
                    ('4', 'Grade 4'),
                    ('5', 'Grade 5'),
                    ('6', 'Grade 6'),
                    ('7', 'Grade 7'),
                ],
                max_length=4,
            ),
        ),
    ]
