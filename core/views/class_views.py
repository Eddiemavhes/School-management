from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models.class_model import Class
from ..models.administrator import Administrator
from ..forms.class_form import ClassForm

@login_required
def class_list(request):
    from ..models.academic_year import AcademicYear
    
    # Get current active year
    current_year = AcademicYear.objects.filter(is_active=True).first()
    active_year = current_year.year if current_year else timezone.now().year
    
    # Get all available academic years for filtering
    all_years = AcademicYear.objects.order_by('-year')
    
    # Allow filtering by academic year via query parameter
    selected_year = request.GET.get('year', str(active_year))
    try:
        selected_year = int(selected_year)
    except (ValueError, TypeError):
        selected_year = active_year
    
    # Get classes for selected year
    classes = Class.objects.filter(academic_year=selected_year).select_related('teacher').all()
    available_teachers = Class.get_available_teachers(selected_year)
    
    context = {
        'classes': classes,
        'available_teachers': available_teachers,
        'active_year': active_year,
        'selected_year': selected_year,
        'all_years': all_years,
    }
    return render(request, 'classes/list.html', context)

@login_required
def class_detail(request, pk):
    class_obj = get_object_or_404(Class.objects.select_related('teacher'), pk=pk)
    students = class_obj.students.all()
    
    context = {
        'class': class_obj,
        'students': students,
    }
    return render(request, 'classes/detail.html', context)

@login_required
def class_create(request):
    from ..models.academic_year import AcademicYear
    from ..forms.class_form import ClassForm
    
    if request.method == 'GET':
        # Get current active year
        current_year = AcademicYear.objects.filter(is_active=True).first()
        active_year = current_year.year if current_year else timezone.now().year
        
        # Get all available academic years (not just active)
        all_years = AcademicYear.objects.order_by('-year')
        
        # Check if it's an API request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            selected_year = int(request.GET.get('year', active_year))
            available_teachers = Class.get_available_teachers(selected_year)
            available_teacher_list = [
                {'id': t.id, 'name': t.full_name} 
                for t in available_teachers
            ]
            return JsonResponse({
                'academic_year': selected_year,
                'available_teachers': available_teacher_list
            })
        
        # Render HTML template for browser access
        form = ClassForm()
        context = {
            'form': form,
            'active_year': active_year,
            'all_years': all_years,
        }
        return render(request, 'classes/create.html', context)
    
    elif request.method == 'POST':
        try:
            data = request.POST
            teacher_id = data.get('teacher')
            teacher = None if not teacher_id else get_object_or_404(Administrator, pk=teacher_id)
            
            academic_year = int(data.get('academic_year', timezone.now().year))
            
            # Check if academic year exists before attempting to create class
            try:
                AcademicYear.objects.get(year=academic_year)
            except AcademicYear.DoesNotExist:
                return JsonResponse({
                    'error': f'Academic year {academic_year} does not exist. Please create it first in Settings before creating classes.'
                }, status=400)
            
            class_obj = Class(
                grade=data['grade'],
                section=data['section'],
                academic_year=academic_year,
                teacher=teacher
            )
            
            # This will validate via clean()
            class_obj.full_clean()  # Validate before saving
            class_obj.save()
            messages.success(request, f'Class {class_obj.grade}{class_obj.section} created successfully!')
            return JsonResponse({'success': True, 'id': class_obj.id})
        except ValidationError as ve:
            # Handle validation errors gracefully
            error_msg = str(ve)
            if 'already assigned' in error_msg:
                return JsonResponse({'error': error_msg}, status=409)
            return JsonResponse({'error': error_msg}, status=400)
        except Exception as e:
            error_msg = str(e)
            # Extract validation error message
            if 'already assigned' in error_msg:
                return JsonResponse({'error': error_msg}, status=409)
            return JsonResponse({'error': error_msg}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def class_edit(request, pk):
    from ..models.academic_year import AcademicYear
    from ..forms.class_form import ClassForm
    
    class_obj = get_object_or_404(Class, pk=pk)
    
    if request.method == 'GET':
        # Get available teachers for this year (including current teacher)
        current_year = AcademicYear.objects.filter(is_active=True).first()
        active_year = current_year.year if current_year else class_obj.academic_year
        
        available_teachers = Class.get_available_teachers(active_year, exclude_class_id=pk)
        
        # Check if it's an API request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            available_teacher_list = [
                {'id': t.id, 'name': t.full_name} 
                for t in available_teachers
            ]
            return JsonResponse({
                'grade': class_obj.grade,
                'section': class_obj.section,
                'academic_year': class_obj.academic_year,
                'teacher': class_obj.teacher.id if class_obj.teacher else None,
                'available_teachers': available_teacher_list
            })
        
        # Render HTML template for browser access
        form = ClassForm(instance=class_obj)
        context = {
            'form': form,
            'class': class_obj,
            'available_teachers': available_teachers,
        }
        return render(request, 'classes/edit.html', context)
    
    if request.method == 'POST':
        try:
            data = request.POST
            teacher_id = data.get('teacher')
            teacher = None if not teacher_id else get_object_or_404(Administrator, pk=teacher_id)
            
            class_obj.grade = data['grade']
            class_obj.section = data['section']
            class_obj.academic_year = data['academic_year']
            class_obj.teacher = teacher
            
            # This will validate via clean()
            class_obj.save()
            
            messages.success(request, f'Class {class_obj.grade}{class_obj.section} updated successfully!')
            return redirect('class_list')
        except Exception as e:
            error_msg = str(e)
            messages.error(request, error_msg)
            return redirect('class_edit', pk=pk)

@login_required
@require_POST
def class_delete(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    
    if not class_obj.can_be_deleted():
        return JsonResponse({'error': 'Cannot delete class with enrolled students'}, status=400)
    
    try:
        class_obj.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)