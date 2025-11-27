from django.urls import path
from core.views.payment_views import (
    PaymentCreateView, PaymentListView,
    StudentPaymentHistoryView, FeeDashboardView, student_payment_details_api
)

app_name = 'payments'

urlpatterns = [
    path('', PaymentListView.as_view(), name='payment_list'),
    path('create/', PaymentCreateView.as_view(), name='payment_create'),
    path('api/student/<int:student_id>/', student_payment_details_api, name='student_payment_details_api'),
    path('student/<int:pk>/', StudentPaymentHistoryView.as_view(), name='student_payment_history'),
]