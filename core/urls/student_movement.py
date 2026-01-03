from django.urls import path
from .views.student_movement import (
    student_movement_history,
    promote_student,
    demote_student,
    transfer_student,
    bulk_promote_students,
    class_transfers
)

urlpatterns = [
    # Student Movement URLs
    path('students/<int:student_id>/movements/', student_movement_history, name='student_movement_history'),
    path('students/<int:student_id>/promote/', promote_student, name='promote_student'),
    path('students/<int:student_id>/demote/', demote_student, name='demote_student'),
    path('students/<int:student_id>/transfer/', transfer_student, name='transfer_student'),
    path('students/bulk-promote/', bulk_promote_students, name='bulk_promote_students'),
    path('students/transfers/', class_transfers, name='class_transfers'),
]