# Generated migration to add grade_level field to TermFee for separate ECD fees

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_add_ecda_ecdb_support'),
    ]

    operations = [
        # Add grade_level field to TermFee with default value
        migrations.AddField(
            model_name='termfee',
            name='grade_level',
            field=models.CharField(
                choices=[
                    ('ECD', 'Early Childhood Development (ECD)'),
                    ('PRIMARY', 'Primary (Grades 1-7)'),
                ],
                default='PRIMARY',
                max_length=10,
            ),
        ),
        # Update unique_together constraint
        migrations.AlterUniqueTogether(
            name='termfee',
            unique_together={('term', 'grade_level')},
        ),
        # Update ordering
        migrations.AlterModelOptions(
            name='termfee',
            options={'ordering': ['-term__academic_year', '-term__term', 'grade_level']},
        ),
    ]
