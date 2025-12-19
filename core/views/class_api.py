from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..models.class_model import Class
from ..models.student import Student
from ..models import AcademicTerm

@login_required
def get_available_classes(request):
    student_id = request.GET.get('student_id')
    
    # If student_id provided, get classes from student's academic year
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
            if student.current_class:
                # Get classes from the same academic year as student's current class
                classes = Class.objects.filter(
                    academic_year=student.current_class.academic_year
                ).order_by('grade', 'section')
            else:
                classes = Class.objects.none()
        except Student.DoesNotExist:
            classes = Class.objects.none()
    else:
        # Fallback: return classes from current academic year
        current_term = AcademicTerm.get_current_term()
        if current_term:
            classes = Class.objects.filter(academic_year=current_term.academic_year).order_by('grade', 'section')
        else:
            classes = Class.objects.none()
    
    return JsonResponse([{
        'id': c.id,
        'grade': c.grade,
        'section': c.section,
        'academic_year': str(c.academic_year)
    } for c in classes], safe=False)