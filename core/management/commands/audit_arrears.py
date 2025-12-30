from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Audit recent arrears import batches and print student balances for inspection'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=5, help='Number of recent batches to inspect')

    def handle(self, *args, **options):
        from core.models import ArrearsImportBatch, StudentBalance

        limit = options.get('limit', 5)
        batches = ArrearsImportBatch.objects.order_by('-created_at')[:limit]

        if not batches:
            self.stdout.write('No arrears import batches found.')
            return

        for b in batches:
            self.stdout.write('\nBATCH: %s  STATUS: %s  STARTING_TERM: %s' % (b.batch_id, b.status, getattr(b, 'starting_term', None)))
            st = b.starting_term or (b.academic_year.terms.filter(term=1).first() if getattr(b, 'academic_year', None) else None)
            self.stdout.write('Resolved starting_term -> %s' % st)

            for e in b.entries.all():
                s = e.student
                self.stdout.write(' ENTRY: %s  id=%s  amount=%s  is_imported=%s  error=%s' % (
                    s.full_name, s.id, getattr(e, 'arrears_amount', None), e.is_imported, e.error_message))

                try:
                    bal = StudentBalance.objects.get(student=s, term=st)
                    self.stdout.write('  BALANCE: term_fee=%s  previous_arrears=%s  amount_paid=%s  total_due=%s  current_balance=%s' % (
                        bal.term_fee, bal.previous_arrears, bal.amount_paid, bal.total_due, bal.current_balance))
                except StudentBalance.DoesNotExist:
                    self.stdout.write('  BALANCE: None')
