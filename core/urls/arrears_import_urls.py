from django.urls import path
from core.views.arrears_import_views import (
    arrears_import_wizard_start,
    arrears_import_manual_entry,
    arrears_import_bulk_upload,
    arrears_import_download_template,
    arrears_import_summary,
    arrears_import_complete,
)

urlpatterns = [
    # Arrears Import Wizard
    path('arrears-import/', arrears_import_wizard_start, name='arrears_import_start'),
    path('arrears-import/<uuid:batch_id>/manual/', arrears_import_manual_entry, name='arrears_import_manual_entry'),
    path('arrears-import/<uuid:batch_id>/bulk/', arrears_import_bulk_upload, name='arrears_import_bulk_upload'),
    path('arrears-import/<uuid:batch_id>/download-template/', arrears_import_download_template, name='arrears_import_download_template'),
    path('arrears-import/<uuid:batch_id>/summary/', arrears_import_summary, name='arrears_import_summary'),
    path('arrears-import/<uuid:batch_id>/complete/', arrears_import_complete, name='arrears_import_complete'),
]
