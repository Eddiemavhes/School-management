from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models.student_movement import StudentMovement, BulkMovement
from ..models.student import Student
from ..models.class_model import Class
from ..models import AcademicTerm
import uuid
import json

@login_required
def student_movement_history(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    movements = StudentMovement.objects.filter(student=student)
    return render(request, 'students/movement_history.html', {
        'student': student,
        'movements': movements
    })

@login_required
def promote_student(request, student_id):
    import json
    from django.http import JsonResponse
    
    student = get_object_or_404(Student, pk=student_id)
    
    if request.method == 'GET':
        # Show promotion form with available classes
        if not student.current_class:
            messages.error(request, 'Student must be assigned to a class before promotion')
            return redirect('student_detail', student_id=student_id)
        
        current_grade = student.current_class.grade
        current_year = student.current_class.academic_year
        
        # Only show classes from the SAME academic year, with HIGHER grades
        available_classes = Class.objects.filter(
            academic_year=current_year,
            grade__gt=current_grade
        ).order_by('grade', 'section')
        
        return render(request, 'students/promotion_form.html', {
            'student': student,
            'available_classes': available_classes,
            'current_class': student.current_class
        })
    
    elif request.method == 'POST':
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                new_class_id = data.get('new_class_id')
                reason = data.get('reason', '')
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
            is_json = True
        else:
            new_class_id = request.POST.get('new_class_id')
            reason = request.POST.get('reason', '')
            is_json = False
        
        if not new_class_id:
            error_msg = 'New class is required'
            if is_json:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('promote_student', student_id=student_id)
        
        try:
            if not student.current_class:
                error_msg = 'Student must be assigned to a class before promotion'
                if is_json:
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect('student_detail', student_id=student_id)
            
            # Check if student is in Grade 7 (highest grade) - they GRADUATE
            if int(student.current_class.grade) >= 7:
                # Student is graduating (no Grade 8, so Grade 7 is the end)
                with transaction.atomic():
                    # Create graduation movement
                    movement = StudentMovement(
                        student=student,
                        from_class=student.current_class,
                        to_class=None,  # No next class
                        movement_type='GRADUATION',
                        moved_by=request.user,
                        previous_arrears=Decimal('0'),
                        preserved_arrears=Decimal('0'),
                        reason=reason
                    )
                    
                    try:
                        movement.full_clean()
                    except ValidationError as e:
                        error_msg = f'Cannot graduate student: {", ".join(e.messages)}'
                        if is_json:
                            return JsonResponse({'success': False, 'error': error_msg}, status=400)
                        messages.error(request, error_msg)
                        return redirect('promote_student', student_id=student_id)
                    
                    movement.save()
                    
                    # Mark as graduated and archived
                    student.is_active = False
                    student.status = 'GRADUATED'
                    student.is_archived = True
                    student.save()
                    
                    messages.success(request, f'{student.full_name} has GRADUATED. Status: Alumni. Current balance: ${student.overall_balance}')
                    return redirect('student_movement_history', student_id=student_id)
            
            # Regular promotion to next grade
            new_class = Class.objects.get(pk=new_class_id)
            old_class = student.current_class
            
            # Record current financial state
            current_arrears = student.previous_term_arrears + student.current_term_balance
            
            # Create movement record
            movement = StudentMovement(
                student=student,
                from_class=old_class,
                to_class=new_class,
                movement_type='PROMOTION',
                moved_by=request.user,
                reason=request.POST.get('reason', ''),
                previous_arrears=current_arrears,
                preserved_arrears=current_arrears
            )
            
            # Validate movement using model validations
            try:
                movement.full_clean()
            except ValidationError as e:
                messages.error(request, f'Cannot promote student: {", ".join(e.messages)}')
                return redirect('promote_student', student_id=student_id)
            
            # Save movement
            movement.save()
            
            # Update student's class
            student.current_class = new_class
            student.save()
            
            messages.success(request, f'Successfully promoted {student.full_name} to {new_class}')
            
            return redirect('student_movement_history', student_id=student_id)
        
        except Class.DoesNotExist:
            messages.error(request, 'Selected class does not exist')
            return redirect('promote_student', student_id=student_id)
        except Exception as e:
            messages.error(request, f'Error promoting student: {str(e)}')
            return redirect('promote_student', student_id=student_id)
            return redirect('promote_student', student_id=student_id)
    
    return redirect('student_movement_history', student_id=student_id)

@login_required
@transaction.atomic
def demote_student(request, student_id):
    import json
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    student = get_object_or_404(Student, pk=student_id)
    
    # Handle both JSON and form data
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            new_class_id = data.get('new_class_id')
            reason = data.get('reason')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        new_class_id = request.POST.get('new_class_id')
        reason = request.POST.get('reason')
    
    if not new_class_id:
        return JsonResponse({'error': 'New class is required'}, status=400)
    
    if not reason:
        return JsonResponse({'error': 'Reason is required for demotion'}, status=400)
    
    if not student.current_class:
        return JsonResponse({'error': 'Student must be assigned to a class before demotion'}, status=400)
        
    try:
        new_class = Class.objects.get(pk=new_class_id)
        old_class = student.current_class
        
        # Record current financial state
        current_arrears = student.previous_term_arrears + student.current_term_balance
        
        # Create movement record
        movement = StudentMovement(
            student=student,
            from_class=old_class,
            to_class=new_class,
            movement_type='DEMOTION',
            moved_by=request.user,
            reason=reason,
            previous_arrears=current_arrears,
            preserved_arrears=current_arrears
        )
        
        # Validate movement using model validations
        try:
            movement.full_clean()
        except ValidationError as e:
            transaction.set_rollback(True)
            return JsonResponse({'success': False, 'error': ', '.join(e.messages)}, status=400)
        
        # Save movement
        movement.save()
        
        # Update student's class
        student.current_class = new_class
        student.save()
            
        return JsonResponse({
            'success': True,
            'message': f'Successfully demoted student to {new_class}',
            'new_class': str(new_class),
            'preserved_arrears': float(current_arrears)
        })
        
    except ValidationError as e:
        transaction.set_rollback(True)
        return JsonResponse({'success': False, 'error': ', '.join(e.messages)}, status=400)
    except Exception as e:
        transaction.set_rollback(True)
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def bulk_promote_students(request):
    """Handle bulk promotion: GET shows page, POST processes promotions."""
    
    current_year = timezone.now().year

    if request.method == 'GET':
        # Get active students who can be promoted (exclude graduated/archived)
        students = Student.objects.select_related('current_class').filter(
            is_active=True,  # Only active students
            current_class__isnull=False  # Only students with a current class
        ).exclude(
            current_class__grade=7  # Exclude students already in the highest grade
        ).order_by('current_class__grade', 'current_class__section')

        current_term = AcademicTerm.get_current_term()
        if current_term:
            classes = Class.objects.filter(academic_year=current_term.academic_year).order_by('grade', 'section')
        else:
            classes = Class.objects.none()

        # Calculate next class for each student
        for student in students:
            if student.current_class and student.current_class.grade:
                try:
                    # Grade is now a string, convert to int for comparison
                    current_grade = int(student.current_class.grade) if student.current_class.grade != 'ECD' else 0
                    next_grade = current_grade + 1
                    class_year = student.current_class.academic_year
                    next_year = class_year + 1
                    
                    if next_grade < 8:
                        # Show the next grade they will move to with the actual next year
                        student.next_class = f"Grade {next_grade}{student.current_class.section} ({next_year})"
                    else:
                        student.next_class = "Graduating"
                except (ValueError, TypeError):
                    student.next_class = "No class assigned"
            else:
                student.next_class = "No class assigned"

        return render(request, 'students/bulk_promote.html', {
            'students': students,
            'classes': classes
        })

    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        
        if not student_ids:
            messages.error(request, 'Please select at least one student to promote')
            return redirect('bulk_promote_students')
            
        successful = 0
        failed = 0
        errors = []

        try:
            for student_id in student_ids:
                try:
                    student = Student.objects.get(id=student_id)
                    
                    # Validate student is active
                    if not student.is_active:
                        failed += 1
                        errors.append(f'{student.full_name} - Already graduated/inactive')
                        continue
                    
                    # Validate student has a class
                    if not student or not student.current_class:
                        failed += 1
                        errors.append(f'Student {student_id} - No assigned class')
                        continue
                    
                    old_class = student.current_class
                    
                    # Validate class data
                    if not old_class or old_class.grade is None or old_class.academic_year is None:
                        failed += 1
                        errors.append(f'{student.full_name} - Invalid class data')
                        continue
                    
                    # Skip ECDA/ECDB students - they follow special progression
                    # ECDA → ECDB (same year) → Grade 1 (next year)
                    if old_class.grade in ['ECDA', 'ECDB']:
                        failed += 1
                        errors.append(f'{student.full_name} - ECDA/ECDB students need special handling')
                        continue
                    
                    # Check if student is already in Grade 7 (highest grade) - GRADUATE them
                    if int(old_class.grade) >= 7:
                        # Graduate the student instead of promoting
                        with transaction.atomic():
                            movement = StudentMovement(
                                student=student,
                                from_class=old_class,
                                to_class=None,
                                movement_type='GRADUATION',
                                moved_by=request.user,
                                previous_arrears=Decimal('0'),
                                preserved_arrears=Decimal('0')
                            )
                            
                            try:
                                movement.full_clean()
                            except ValidationError as e:
                                failed += 1
                                errors.append(f'{student.full_name} - Cannot graduate: {", ".join(e.messages)}')
                                continue
                            
                            movement.save()
                            
                            # Mark as graduated and archived (alumni)
                            student.is_active = False
                            student.status = 'GRADUATED'
                            student.is_archived = True
                            student.save()
                            
                            successful += 1
                        continue
                    
                    next_grade = int(old_class.grade) + 1
                    next_year = old_class.academic_year + 1
                    
                    # Auto-create the next year if it doesn't exist
                    from ..models.academic_year import AcademicYear
                    next_year_obj, _ = AcademicYear.objects.get_or_create(
                        year=next_year,
                        defaults={
                            'is_active': False,
                            'start_date': f'{next_year}-01-01',
                            'end_date': f'{next_year}-12-31'
                        }
                    )
                    
                    # Find the next grade class in the next academic year
                    # Convert next_grade int back to string for lookup
                    next_class = Class.objects.filter(
                        grade=str(next_grade),
                        section=old_class.section,
                        academic_year=next_year
                    ).first()
                    
                    # If same section doesn't exist, auto-create it
                    if not next_class:
                        next_class, _ = Class.objects.get_or_create(
                            grade=str(next_grade),
                            section=old_class.section,
                            academic_year=next_year
                        )
                    
                    # Create movement record and update student
                    with transaction.atomic():
                        current_arrears = student.previous_term_arrears + student.current_term_balance
                        
                        movement = StudentMovement(
                            student=student,
                            from_class=old_class,
                            to_class=next_class,
                            movement_type='PROMOTION',
                            moved_by=request.user,
                            previous_arrears=current_arrears,
                            preserved_arrears=current_arrears
                        )
                        
                        # Validate movement using model validations
                        try:
                            movement.full_clean()
                        except ValidationError as e:
                            failed += 1
                            errors.append(f'{student.full_name} - {", ".join(e.messages)}')
                            continue
                        
                        # Save movement
                        movement.save()
                        
                        student.current_class = next_class
                        
                        # IMPORTANT: Grade 7 students are GRADUATING
                        # They should NOT be registered for any 2027 terms
                        # They only track their 2026 debt and can become alumni after payment
                        
                        if next_grade == 8:  # Grade 8 is graduation (after Grade 7)
                            movement.movement_type = 'GRADUATION'
                            movement.save()
                            # Note: Do NOT create any 2027 balance for graduating students
                        
                        student.save()
                        
                        # Initialize balance for the first term of the new year (only for non-graduating students)
                        if next_grade < 8:
                            from ..models.fee import StudentBalance, TermFee
                            
                            first_term = AcademicTerm.objects.filter(
                                academic_year=next_year,
                                term=1
                            ).first()
                            
                            if first_term:
                                # Use initialize_term_balance which properly calculates arrears from previous year
                                try:
                                    StudentBalance.initialize_term_balance(student, first_term)
                                except Exception as e:
                                    print(f"Warning: Could not initialize balance for {student.full_name}: {e}")
                        
                        successful += 1
                        
                except Student.DoesNotExist:
                    failed += 1
                    errors.append(f'Student {student_id} - Not found')
                    continue
                except Exception as e:
                    failed += 1
                    errors.append(f'Student {student_id} - {str(e)}')
                    continue
                    
            if successful > 0:
                messages.success(request, f'Successfully promoted {successful} student(s).')
            if failed > 0:
                messages.warning(request, f'Failed to promote {failed} student(s):')
                for error in errors:
                    messages.error(request, f'  • {error}')
                
        except Exception as e:
            messages.error(request, f'Error during bulk promotion: {str(e)}')
        
        return redirect('bulk_promote_students')

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
@transaction.atomic
def transfer_student(request, student_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    student = get_object_or_404(Student, pk=student_id)
    new_class_id = request.POST.get('new_class_id')
    reason = request.POST.get('reason', '')
    
    if not new_class_id:
        return JsonResponse({'error': 'New class is required'}, status=400)
    
    if not student.current_class:
        return JsonResponse({'error': 'Student must be assigned to a class before transfer'}, status=400)
        
    try:
        new_class = Class.objects.get(pk=new_class_id)
        old_class = student.current_class
        
        # Record current financial state
        current_arrears = student.previous_term_arrears + student.current_term_balance
        
        # Create movement record
        movement = StudentMovement(
            student=student,
            from_class=old_class,
            to_class=new_class,
            movement_type='TRANSFER',
            moved_by=request.user,
            reason=reason,
            previous_arrears=current_arrears,
            preserved_arrears=current_arrears
        )
        
        # Validate movement using model validations
        try:
            movement.full_clean()
        except ValidationError as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': ', '.join(e.messages)}, status=400)
        
        # Save movement
        movement.save()
        
        # Update student's class
        student.current_class = new_class
        student.save()
            
        return JsonResponse({
            'success': True,
            'message': f'Successfully transferred student to {new_class}',
            'new_class': str(new_class),
            'preserved_arrears': float(current_arrears)
        })
        
    except ValidationError as e:
        transaction.set_rollback(True)
        return JsonResponse({'error': ', '.join(e.messages)}, status=400)
    except Exception as e:
        transaction.set_rollback(True)
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def class_transfers(request):
    """Display and manage class transfers for students."""
    from django.contrib import messages
    
    if request.method == 'GET':
        # Get all active students with current classes
        students = Student.objects.select_related('current_class').filter(
            is_active=True,
            current_class__isnull=False
        ).order_by('surname', 'first_name')
        
        # Get all available classes
        classes = Class.objects.all().order_by('academic_year', 'grade', 'section')
        
        context = {
            'students': students,
            'classes': classes,
            'has_students': students.exists(),
            'has_classes': classes.exists(),
        }
        
        # Show info message if no data
        if not students or not classes:
            if not classes:
                messages.info(request, '📚 No classes found. Please create classes in the Classes section first.')
            if not students:
                messages.info(request, '👥 No students found. Please add students to classes first.')
        
        return render(request, 'students/class_transfers.html', context)
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        new_class_id = request.POST.get('new_class_id')
        reason = request.POST.get('reason', '')
        
        if not student_id or not new_class_id:
            messages.error(request, 'Student and class are required')
            return redirect('class_transfers')
        
        try:
            student = Student.objects.get(pk=student_id)
            new_class = Class.objects.get(pk=new_class_id)
            old_class = student.current_class
            
            # Don't allow transfer to same class
            if old_class.id == new_class.id:
                messages.warning(request, f'{student.full_name} is already in {new_class.name}')
                return redirect('class_transfers')
            
            # Record current financial state
            current_arrears = student.previous_term_arrears + student.current_term_balance
            
            # Create movement record
            with transaction.atomic():
                movement = StudentMovement(
                    student=student,
                    from_class=old_class,
                    to_class=new_class,
                    movement_type='TRANSFER',
                    moved_by=request.user,
                    reason=reason,
                    previous_arrears=current_arrears,
                    preserved_arrears=current_arrears
                )
                
                # Validate movement
                try:
                    movement.full_clean()
                except ValidationError as e:
                    transaction.set_rollback(True)
                    messages.error(request, f'Transfer error: {", ".join(e.messages)}')
                    return redirect('class_transfers')
                
                # Save movement
                movement.save()
                
                # Update student's class
                student.current_class = new_class
                student.save()
                
                messages.success(request, f'Successfully transferred {student.full_name} to {new_class.name}')
        
        except Student.DoesNotExist:
            messages.error(request, 'Student not found')
        except Class.DoesNotExist:
            messages.error(request, 'Class not found')
        except Exception as e:
            messages.error(request, f'Error during transfer: {str(e)}')
        
        return redirect('class_transfers')