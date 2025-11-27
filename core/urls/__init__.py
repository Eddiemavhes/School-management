from django.urls import path
from core.views.auth_views import AdminLoginView, AdminLogoutView, AdminDashboardView, SuperuserLoginView
from core.views.class_views import (
    class_list, class_detail, class_create,
    class_edit, class_delete
)
from core.views.teacher_views import (
    TeacherListView, TeacherDetailView, TeacherCreateView,
    TeacherUpdateView, TeacherDeleteView, assign_class, unassign_class
)
from core.views.student_views import (
    StudentListView, StudentDetailView, StudentCreateView,
    StudentUpdateView, StudentDeleteView, transfer_student,
    ArchivedStudentsListView, ArchivedStudentDeleteView
)
from core.views.payment_views import (
    PaymentCreateView, PaymentListView,
    StudentPaymentHistoryView, FeeDashboardView, student_payment_details_api,
    export_student_payment_history, export_fee_dashboard, arrears_report_pdf
)
from core.views.settings_views import (
    AdminSettingsView, AdminProfileUpdateView,
    update_admin_password, create_academic_term,
    set_current_term, update_term_fee, create_academic_year,
    set_active_year, create_fee, update_password
)
from core.views.class_api import get_available_classes
from core.views.student_movement import (
    student_movement_history, promote_student, 
    demote_student, bulk_promote_students
)
from core.views.step10_academic_management import (
    update_term_fee_api, update_term_dates_api, FeeConfigurationView, create_terms_api, activate_first_term_api
)
from core.views.school_views import SchoolDetailsUpdateView, school_details_view
from core.views.superuser_views import (
    SuperuserDashboardView, ResetAdminPasswordView,
    reset_system_api, clear_payments_api, clear_students_api, clear_terms_api
)

urlpatterns = [
    # Authentication URLs
    path('login/', AdminLoginView.as_view(), name='login'),
    path('login/admin/', SuperuserLoginView.as_view(), name='superuser_login'),
    path('logout/', AdminLogoutView.as_view(), name='logout'),
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Class Management URLs
    path('classes/', class_list, name='class_list'),
    path('classes/create/', class_create, name='class_create'),
    path('classes/<int:pk>/', class_detail, name='class_detail'),
    path('classes/<int:pk>/edit/', class_edit, name='class_edit'),
    path('classes/<int:pk>/delete/', class_delete, name='class_delete'),

    # Teacher Management URLs
    path('teachers/', TeacherListView.as_view(), name='teacher_list'),
    path('teachers/create/', TeacherCreateView.as_view(), name='teacher_create'),
    path('teachers/<int:pk>/', TeacherDetailView.as_view(), name='teacher_detail'),
    path('teachers/<int:pk>/edit/', TeacherUpdateView.as_view(), name='teacher_update'),
    path('teachers/<int:pk>/delete/', TeacherDeleteView.as_view(), name='teacher_delete'),
    path('teachers/<int:teacher_id>/assign-class/', assign_class, name='assign_class'),
    path('teachers/<int:teacher_id>/unassign-class/', unassign_class, name='unassign_class'),

    # Student Management URLs
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/create/', StudentCreateView.as_view(), name='student_create'),
    path('students/archived/', ArchivedStudentsListView.as_view(), name='archived_students'),
    path('students/archived/<int:pk>/delete/', ArchivedStudentDeleteView.as_view(), name='archived_student_delete'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', StudentUpdateView.as_view(), name='student_update'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    path('students/<int:pk>/transfer/', transfer_student, name='transfer_student'),

    # Student Movement URLs
    path('students/<int:student_id>/movements/', student_movement_history, name='student_movement_history'),
    path('students/<int:student_id>/promote/', promote_student, name='promote_student'),
    path('students/<int:student_id>/demote/', demote_student, name='demote_student'),
    path('students/bulk-promote/', bulk_promote_students, name='bulk_promote_students'),
    
    # Payment and Fee Management URLs
    path('fees/', FeeDashboardView.as_view(), name='fee_dashboard'),
    path('fees/export/', export_fee_dashboard, name='export_fee_dashboard'),
    path('fees/arrears-report/', arrears_report_pdf, name='arrears_report_pdf'),
    path('payments/', PaymentListView.as_view(), name='payment_list'),
    path('payments/create/', PaymentCreateView.as_view(), name='payment_create'),
    path('student/<int:pk>/payments/', StudentPaymentHistoryView.as_view(), name='student_payment_history'),
    path('student/<int:student_id>/payments/export/', export_student_payment_history, name='export_student_payment_history'),
    
    # Settings URLs
    path('settings/', AdminSettingsView.as_view(), name='admin_settings'),
    path('settings/profile/', AdminProfileUpdateView.as_view(), name='admin_profile'),
    path('settings/password/', update_admin_password, name='update_password'),
    path('settings/password/update/', update_password, name='update_admin_password'),
    path('settings/school/', SchoolDetailsUpdateView.as_view(), name='school_details'),
    path('settings/school/view/', school_details_view, name='school_details_view'),
    path('settings/years/create/', create_academic_year, name='create_academic_year'),
    path('settings/years/set-active/', set_active_year, name='set_active_year'),
    path('settings/terms/create/', create_academic_term, name='create_term'),
    path('settings/terms/set-current/', set_current_term, name='set_current_term'),
    path('settings/fees/create/', create_fee, name='create_fee'),
    path('settings/fees/update/', update_term_fee, name='update_term_fee'),
    path('settings/fees/configuration/', FeeConfigurationView.as_view(), name='fee_configuration'),
    
    # API URLs
    path('api/classes/', get_available_classes, name='get_available_classes'),
    path('api/student-payment-details/<int:student_id>/', student_payment_details_api, name='student_payment_details_api'),
    
    # Admin API URLs for academic management
    path('admin/api/term/<int:term_id>/update-fee/', update_term_fee_api, name='update_term_fee_api'),
    path('admin/api/term/<int:term_id>/update-dates/', update_term_dates_api, name='update_term_dates_api'),
    path('admin/api/create-terms/', create_terms_api, name='create_terms_api'),
    path('admin/api/activate-first-term/', activate_first_term_api, name='activate_first_term_api'),
    
    # Superuser Management URLs
    path('superuser/', SuperuserDashboardView.as_view(), name='superuser_dashboard'),
    path('superuser/reset-password/', ResetAdminPasswordView.as_view(), name='reset_admin_password'),
    path('superuser/api/reset-system/', reset_system_api, name='reset_system_api'),
    path('superuser/api/clear-payments/', clear_payments_api, name='clear_payments_api'),
    path('superuser/api/clear-students/', clear_students_api, name='clear_students_api'),
    path('superuser/api/clear-terms/', clear_terms_api, name='clear_terms_api'),
]
