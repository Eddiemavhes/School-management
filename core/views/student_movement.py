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
    student = get_object_or_404(Student, pk=student_id)
    
    if request.method == 'GET':
        # Show promotion form with available classes
        if not student.current_class:
            messages.error(request, 'Student must be assigned to a class before promotion')
            return redirect('student_detail', student_id=student_id)
        
        current_grade = student.current_class.grade
        available_classes = Class.objects.filter(
            grade__gt=current_grade
        ).order_by('grade', 'section')
        
        return render(request, 'students/promotion_form.html', {
            'student': student,
            'available_classes': available_classes,
            'current_class': student.current_class
        })
    
    elif request.method == 'POST':
        # Handle promotion
        new_class_id = request.POST.get('new_class_id')
        
        if not new_class_id:
            messages.error(request, 'New class is required')
            return redirect('promote_student', student_id=student_id)
        
        try:
            if not student.current_class:
                messages.error(request, 'Student must be assigned to a class before promotion')
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
                        preserved_arrears=Decimal('0')
                    )
                    
                    try:
                        movement.full_clean()
                    except ValidationError as e:
                        messages.error(request, f'Cannot graduate student: {", ".join(e.messages)}')
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
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    student = get_object_or_404(Student, pk=student_id)
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
            return JsonResponse({'error': ', '.join(e.messages)}, status=400)
        
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
        return JsonResponse({'error': ', '.join(e.messages)}, status=400)
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

        classes = Class.objects.all().order_by('grade', 'section')

        # Calculate next class for each student
        for student in students:
            if student.current_class and student.current_class.grade:
                next_grade = student.current_class.grade + 1
                current_year = student.current_class.academic_year
                next_year = current_year + 1
                
                if next_grade < 8:
                    # Show the next grade they will move to with the actual next year
                    student.next_class = f"Grade {next_grade}{student.current_class.section} ({next_year})"
                else:
                    student.next_class = "Graduating"
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
                    next_year = int(old_class.academic_year) + 1
                    
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
                    next_class = Class.objects.filter(
                        grade=next_grade,
                        section=old_class.section,
                        academic_year=next_year
                    ).first()
                    
                    # If same section doesn't exist, auto-create it
                    if not next_class:
                        next_class, _ = Class.objects.get_or_create(
                            grade=next_grade,
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
                            from ..models.academic import AcademicTerm
                            
                            first_term = AcademicTerm.objects.filter(
                                academic_year=next_year,
                                term=1
                            ).first()
                            
                            if first_term:
                                # Check if balance already exists
                                existing = StudentBalance.objects.filter(
                                    student=student,
                                    term=first_term
                                ).exists()
                                
                                if not existing:
                                    # Get term fee
                                    term_fee = TermFee.objects.filter(term=first_term).first()
                                    
                                    if term_fee:
                                        StudentBalance.objects.create(
                                            student=student,
                                            term=first_term,
                                            term_fee=term_fee.amount,
                                            previous_arrears=max(Decimal('0'), current_arrears),
                                            amount_paid=Decimal('0')
                                        )
                        
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