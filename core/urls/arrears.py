"""
URL configuration for Arrears Vault management system
"""

from django.urls import path
from core.views.arrears_management import (
    ArrearsVaultListView,
    ArrearsVaultDetailView,
    process_payment,
    send_payment_reminder,
    arrears_reports,
    api_check_payment_status,
)

app_name = 'arrears'

urlpatterns = [
    # Arrears vault management
    path('', ArrearsVaultListView.as_view(), name='vault_list'),
    path('<uuid:pk>/', ArrearsVaultDetailView.as_view(), name='vault_detail'),
    path('<uuid:pk>/process-payment/', process_payment, name='process_payment'),
    path('<uuid:pk>/send-reminder/', send_payment_reminder, name='send_reminder'),
    
    # Reports
    path('reports/permanent-register/', arrears_reports, name='reports'),
    
    # API endpoints
    path('api/<uuid:pk>/status/', api_check_payment_status, name='api_status'),
]
