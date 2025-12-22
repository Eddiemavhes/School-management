from django.core.management.base import BaseCommand
from decimal import Decimal


class Command(BaseCommand):
    help = 'Repair arrears applied by import batches. Dry-run by default; use --apply to make changes.'

    def add_arguments(self, parser):
        parser.add_argument('--batch-id', type=str, help='ArrearsImportBatch.batch_id to repair (optional)')
        parser.add_argument('--limit', type=int, default=50, help='Number of recent batches to inspect when --batch-id is omitted')
        parser.add_argument('--apply', action='store_true', help='Apply fixes (dangerous). Without this flag the command only shows a dry-run')

    def handle(self, *args, **options):
        from core.models import ArrearsImportBatch, StudentBalance

        batch_id = options.get('batch_id')
        limit = options.get('limit', 50)
        do_apply = options.get('apply', False)

        if batch_id:
            batches = ArrearsImportBatch.objects.filter(batch_id=batch_id)
        else:
            batches = ArrearsImportBatch.objects.order_by('-created_at')[:limit]

        if not batches.exists():
            self.stdout.write('No matching arrears import batches found.')
            return

        total_proposed = 0
        total_applied = 0

        for b in batches:
            self.stdout.write('\n=== Batch %s  status=%s  starting_term=%s ===' % (b.batch_id, b.status, getattr(b, 'starting_term', None)))
            starting_term = b.starting_term or (b.academic_year.terms.filter(term=1).first() if getattr(b, 'academic_year', None) else None)
            if not starting_term:
                self.stdout.write('  Cannot resolve starting term for batch; skipping')
                continue

            for e in b.entries.all():
                student = e.student
                # final amount: verified if verified, else original
                final_amount = getattr(e, 'verified_amount', None) if getattr(e, 'is_verified', False) else e.arrears_amount
                if final_amount is None:
                    final_amount = Decimal('0')

                try:
                    bal = StudentBalance.objects.get(student=student, term=starting_term)
                except StudentBalance.DoesNotExist:
                    self.stdout.write(' ENTRY: %s (id=%s): no StudentBalance for term %s' % (student.full_name, student.id, starting_term))
                    continue

                # base_arrears = calculated from previous terms (excludes this imported batch)
                base_arrears = StudentBalance.calculate_arrears(student, starting_term) or Decimal('0')

                desired_previous_arrears = (base_arrears or Decimal('0')) + (final_amount or Decimal('0'))

                current_prev = bal.previous_arrears or Decimal('0')

                if current_prev != desired_previous_arrears:
                    total_proposed += 1
                    self.stdout.write(' ENTRY: %s (id=%s): final_amount=%s  base_arrears=%s  current_prev=%s  desired_prev=%s' % (
                        student.full_name, student.id, final_amount, base_arrears, current_prev, desired_previous_arrears))

                    if do_apply:
                        bal.previous_arrears = desired_previous_arrears
                        bal.save(update_fields=['previous_arrears'])
                        total_applied += 1
                        self.stdout.write('   -> Applied change')
                    else:
                        self.stdout.write('   -> DRY-RUN only (use --apply to write)')

        self.stdout.write('\nSummary: proposed_changes=%d applied_changes=%d' % (total_proposed, total_applied))
