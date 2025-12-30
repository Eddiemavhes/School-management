import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Class
from core.forms.class_form import ClassForm

print("=" * 60)
print("CHECKING ECDA/ECDB CONFIGURATION")
print("=" * 60)

print("\n1. MODEL GRADE_CHOICES:")
print("-" * 60)
for choice in Class.GRADE_CHOICES:
    print(f"   {choice}")
print(f"\n   Total: {len(Class.GRADE_CHOICES)} choices")

print("\n2. FORM GRADE FIELD CHOICES:")
print("-" * 60)
form = ClassForm()
grade_field = form.fields.get('grade')
if grade_field:
    print(f"   Field type: {type(grade_field).__name__}")
    print(f"   Widget type: {type(grade_field.widget).__name__}")
    if hasattr(grade_field, 'choices'):
        print(f"   Number of choices: {len(list(grade_field.choices))}")
        print("   Choices:")
        for choice in grade_field.choices:
            print(f"      {choice}")
else:
    print("   ERROR: 'grade' field not found in form!")

print("\n3. DATABASE CLASSES:")
print("-" * 60)
classes = Class.objects.all()
print(f"   Total classes in DB: {classes.count()}")
if classes.exists():
    print("   Grades in database:")
    for cls in classes.order_by('grade'):
        print(f"      {cls.grade}-{cls.section} ({cls.academic_year})")
else:
    print("   No classes in database yet")

print("\n" + "=" * 60)
