from django.contrib import admin
from .models.student_movement import StudentMovement, BulkMovement
from .models.academic import Payment

# Register your models here.
admin.site.register(StudentMovement)
admin.site.register(BulkMovement)
admin.site.register(Payment)
