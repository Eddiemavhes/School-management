from django.contrib import admin
from .models.student_movement import StudentMovement, BulkMovement
from .models.academic import Payment
from .models import ECDClassProfile, ECDClassFee, Class, Student


class ECDClassProfileInline(admin.StackedInline):
	model = ECDClassProfile
	extra = 0
	max_num = 1
	fields = ('capacity', 'premium', 'meal_plan_fee', 'nappies_fee', 'materials_fee', 'notes')


class ECDClassFeeInline(admin.TabularInline):
	model = ECDClassFee
	extra = 0
	fields = ('term', 'amount', 'description')


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'academic_year', 'teacher')
	list_filter = ('academic_year', 'grade')
	search_fields = ('grade', 'section', 'academic_year')
	inlines = [ECDClassProfileInline, ECDClassFeeInline]
	
	def get_queryset(self, request):
		"""Optimize queryset by selecting related fields to avoid N+1 queries"""
		qs = super().get_queryset(request)
		return qs.select_related('academic_year', 'teacher')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'current_class', 'is_active')
	list_filter = ('is_active', 'current_class__grade')
	search_fields = ('surname', 'first_name', 'birth_entry_number')
	
	def get_queryset(self, request):
		"""Optimize queryset by selecting related fields to avoid N+1 queries"""
		qs = super().get_queryset(request)
		return qs.select_related('current_class')


@admin.register(ECDClassProfile)
class ECDClassProfileAdmin(admin.ModelAdmin):
	list_display = ('cls', 'capacity', 'premium', 'meal_plan_fee', 'nappies_fee')
	list_filter = ('premium',)
	search_fields = ('cls__grade', 'cls__section')


@admin.register(ECDClassFee)
class ECDClassFeeAdmin(admin.ModelAdmin):
	list_display = ('cls', 'term', 'amount', 'description')
	list_filter = ('term',)
	search_fields = ('cls__grade', 'cls__section', 'description')

# Register your models here.
admin.site.register(StudentMovement)
admin.site.register(BulkMovement)
admin.site.register(Payment)
