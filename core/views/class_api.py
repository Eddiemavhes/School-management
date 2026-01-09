from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from ..models.class_model import Class
from ..models.student import Student
from ..models import AcademicTerm, ECDClassProfile, ECDClassFee

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


@login_required
@require_http_methods(["GET", "POST"])
def ecd_fees_api(request, class_id):
    """API endpoint for getting and saving ECD class fees"""
    try:
        cls = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return JsonResponse({'error': 'Class not found'}, status=404)
    
    # Check if class is ECD (ECDA or ECDB)
    if cls.grade not in ['ECDA', 'ECDB']:
        return JsonResponse({'error': 'This class is not an ECD class'}, status=400)
    
    if request.method == 'GET':
        # Return current ECD fees data
        profile = ECDClassProfile.objects.filter(cls=cls).first()
        term_fees = ECDClassFee.objects.filter(cls=cls)
        all_terms = AcademicTerm.objects.filter(academic_year=cls.academic_year).order_by('term')
        
        profile_data = {
            'capacity': profile.capacity if profile else None,
            'premium': profile.premium if profile else False,
            'meal_plan_fee': float(profile.meal_plan_fee) if profile else 0,
            'nappies_fee': float(profile.nappies_fee) if profile else 0,
            'materials_fee': float(profile.materials_fee) if profile else 0,
            'notes': profile.notes if profile else '',
        } if profile else {
            'capacity': None,
            'premium': False,
            'meal_plan_fee': 0,
            'nappies_fee': 0,
            'materials_fee': 0,
            'notes': '',
        }
        
        term_fees_data = [{
            'term_id': fee.term.id,
            'term_name': fee.term.get_term_display(),
            'amount': float(fee.amount),
            'description': fee.description
        } for fee in term_fees]
        
        return JsonResponse({
            'profile': profile_data,
            'terms': [{'id': t.id, 'name': t.get_term_display()} for t in all_terms],
            'term_fees': term_fees_data
        })
    
    elif request.method == 'POST':
        # Save ECD fees data
        try:
            data = request.POST
            
            # Update or create ECD profile (only capacity and premium now)
            profile, created = ECDClassProfile.objects.get_or_create(cls=cls)
            profile.capacity = int(data.get('capacity', 0)) or None
            profile.premium = data.get('premium', 'false').lower() == 'true'
            profile.save()
            
            # Update term fees
            # First, collect all term fee updates
            term_count = 0
            for key in data.keys():
                if key.startswith('term_') and key.endswith('_id'):
                    term_count += 1
            
            # Process each term
            for i in range(term_count):
                term_id = data.get(f'term_{i}_id')
                amount = data.get(f'term_{i}_amount')
                description = data.get(f'term_{i}_description', '')
                
                if term_id and amount:
                    try:
                        term = AcademicTerm.objects.get(id=term_id)
                        fee, _ = ECDClassFee.objects.get_or_create(cls=cls, term=term)
                        fee.amount = float(amount)
                        fee.description = description
                        fee.save()
                    except AcademicTerm.DoesNotExist:
                        continue
            
            return JsonResponse({'success': True, 'message': 'ECD fees saved successfully'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
