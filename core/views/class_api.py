from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..models.class_model import Class

@login_required
def get_available_classes(request):
    classes = Class.objects.all().order_by('grade', 'section')
    return JsonResponse([{
        'id': c.id,
        'grade': c.grade,
        'section': c.section,
        'academic_year': c.academic_year
    } for c in classes], safe=False)