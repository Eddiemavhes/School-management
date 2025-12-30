import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.academic import AcademicTerm
from core.models.arrears_import import ArrearsImportBatch

def main():
    ct = AcademicTerm.get_current_term()
    print('CURRENT_TERM_REPR:', repr(ct))
    if ct is not None:
        print('academic_year:', getattr(ct, 'academic_year', None))
        print('term_field:', getattr(ct, 'term', None))
        try:
            print('get_term_display:', ct.get_term_display())
        except Exception:
            pass
    else:
        print('No current term (None)')

    year = getattr(ct, 'academic_year', None)
    blocking_statuses = ['VALIDATING', 'READY', 'IMPORTED']
    qs = ArrearsImportBatch.objects.all()
    print('TOTAL_BATCHES:', qs.count())
    if year is not None:
        qs_year = ArrearsImportBatch.objects.filter(academic_year=year)
        print('BATCHES_FOR_CURRENT_YEAR:', qs_year.count())
        for b in qs_year:
            print('BATCH:', b.id, 'status=', b.status, 'starting_term=', getattr(b, 'starting_term', None))

    blocking_qs = ArrearsImportBatch.objects.filter(status__in=blocking_statuses)
    print('BLOCKING_TOTAL:', blocking_qs.count())
    for b in blocking_qs:
        print('BLOCKING BATCH:', b.id, 'status=', b.status, 'academic_year=', getattr(b, 'academic_year', None))

if __name__ == '__main__':
    main()
