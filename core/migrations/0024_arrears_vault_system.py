"""
Django migration to create Arrears Vault system
Database schema for strict, immutable graduated with arrears management
"""

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_alter_studentbalance_term_fee_record'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArrearsVault',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.IntegerField(help_text='Original student database ID (reference only, no FK)')),
                ('student_full_name', models.CharField(help_text='Snapshot of student name at graduation', max_length=200)),
                ('student_birth_entry', models.CharField(help_text='Snapshot of birth entry number at graduation', max_length=20)),
                ('graduation_date', models.DateField(auto_now_add=True)),
                ('graduation_year', models.IntegerField()),
                ('graduation_grade', models.CharField(default='7', max_length=3)),
                ('final_aggregate', models.CharField(blank=True, help_text='Academic performance at graduation (reference only)', max_length=50)),
                ('fixed_balance', models.DecimalField(decimal_places=2, help_text='Fixed outstanding amount - NEVER CHANGES until paid', max_digits=10)),
                ('required_payment', models.DecimalField(decimal_places=2, help_text='Amount required for alumni transition - EQUALS fixed_balance', max_digits=10)),
                ('parent_name', models.CharField(max_length=200)),
                ('parent_phone', models.CharField(max_length=20)),
                ('parent_email', models.EmailField(max_length=254)),
                ('status', models.CharField(default='GRADUATED_WITH_ARREARS', editable=False, help_text='Status is always GRADUATED_WITH_ARREARS until 100% paid', max_length=50)),
                ('total_payment_attempts', models.IntegerField(default=0)),
                ('last_payment_attempt_date', models.DateTimeField(blank=True, null=True)),
                ('last_payment_attempt_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Record of rejected or held payment', max_digits=10, null=True)),
                ('total_escrowed', models.DecimalField(decimal_places=2, default=0, help_text='Partial payments held in escrow (awaiting full payment)', max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('transition_date', models.DateTimeField(blank=True, editable=False, help_text='When student transitioned to ALUMNI (null if unpaid)', null=True)),
                ('transition_payment_method', models.CharField(blank=True, help_text='How the final payment was made', max_length=50)),
                ('is_locked', models.BooleanField(default=True, editable=False, help_text='Record is always locked (immutable)')),
            ],
            options={
                'verbose_name': 'Graduated with Arrears (Vault)',
                'verbose_name_plural': 'Graduated with Arrears (Vault)',
                'db_table': 'arrears_vault_permanent',
            },
        ),
        migrations.CreateModel(
            name='ArrearsPaymentLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('payment_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(max_length=50)),
                ('result', models.CharField(choices=[('ACCEPTED_FULL_PAYMENT', 'Full Payment Accepted - Transition to ALUMNI'), ('REJECTED_PARTIAL_PAYMENT', 'Partial Payment Rejected - Held in Escrow'), ('REJECTED_EXCESS_PAYMENT', 'Excess Payment Rejected'), ('INVALID_AMOUNT', 'Invalid Amount')], max_length=50)),
                ('details', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, editable=False)),
                ('vault', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payment_logs', to='core.arrearsvault')),
            ],
            options={
                'verbose_name': 'Arrears Payment Log',
                'verbose_name_plural': 'Arrears Payment Logs',
                'db_table': 'arrears_payment_log',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ArrearsReport',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('generated_date', models.DateTimeField(auto_now_add=True)),
                ('report_type', models.CharField(choices=[('DAILY_SUMMARY', 'Daily Summary'), ('MONTHLY_REPORT', 'Monthly Report'), ('ANNUAL_REPORT', 'Annual Report'), ('PERMANENT_REGISTER', 'Permanent Register')], max_length=50)),
                ('total_in_vault', models.IntegerField()),
                ('total_arrears_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('oldest_graduation_year', models.IntegerField()),
                ('collections_this_period', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('number_transitioned_to_alumni', models.IntegerField(default=0)),
                ('average_arrears', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('largest_single_arrears', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('smallest_single_arrears', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('rejected_partial_payments', models.IntegerField(default=0)),
                ('administrative_exceptions_granted', models.IntegerField(default=0)),
                ('report_data', models.JSONField(blank=True, default=dict)),
            ],
            options={
                'verbose_name': 'Arrears Report',
                'verbose_name_plural': 'Arrears Reports',
                'db_table': 'arrears_reports',
                'ordering': ['-generated_date'],
            },
        ),
        migrations.AddConstraint(
            model_name='arrearsvault',
            constraint=models.CheckConstraint(check=models.Q(('fixed_balance__gt', 0)), name='arrears_balance_must_be_positive'),
        ),
        migrations.AddConstraint(
            model_name='arrearsvault',
            constraint=models.CheckConstraint(check=models.Q(('required_payment', models.F('fixed_balance'))), name='required_payment_must_equal_balance'),
        ),
        migrations.AddConstraint(
            model_name='arrearsvault',
            constraint=models.CheckConstraint(check=models.Q(('status', 'GRADUATED_WITH_ARREARS')), name='status_must_be_graduated_with_arrears'),
        ),
        migrations.AddIndex(
            model_name='arrearsvault',
            index=models.Index(fields=['student_id'], name='arrears_vau_student_idx'),
        ),
        migrations.AddIndex(
            model_name='arrearsvault',
            index=models.Index(fields=['graduation_year'], name='arrears_vau_grad_year_idx'),
        ),
        migrations.AddIndex(
            model_name='arrearsvault',
            index=models.Index(fields=['status'], name='arrears_vau_status_idx'),
        ),
        migrations.AddIndex(
            model_name='arrearsvault',
            index=models.Index(fields=['fixed_balance'], name='arrears_vau_balance_idx'),
        ),
    ]
