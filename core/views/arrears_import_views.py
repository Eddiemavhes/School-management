from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from decimal import Decimal
import csv
import logging

from core.models import (
    ArrearsImportBatch,
    ArrearsImportEntry,
    StudentArrearsRecord,
    AcademicYear,
    AcademicTerm,
    Student,
    StudentBalance,
)
from core.forms.arrears_import_forms import (
    ArrearsImportInitializationForm,
    StudentArrearsEntryForm,
    ConfirmArrearsAmountForm,
    BulkArrearsUploadForm,
    PreImportConfirmationForm,
)
from core.services.arrears_import_service import ArrearsImportService

logger = logging.getLogger(__name__)


def is_staff_or_admin(user):
    """Check if user is staff or superuser"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
def arrears_import_wizard_start(request):
    """Phase 1: Initialize arrears import - select year and method"""
    
    # Only allow arrears import in Term 1 and before any import batch has been attempted
    current_term = AcademicTerm.get_current_term()
    if not current_term or current_term.term != 1:
        # Not in Term 1, redirect to dashboard
        return redirect('dashboard')
    
    # Check if any arrears import batch exists (completed or in progress)
    if ArrearsImportBatch.objects.exists():
        # Arrears import has already been attempted, redirect to dashboard
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ArrearsImportInitializationForm(request.POST)
        if form.is_valid():
            academic_year = form.cleaned_data['academic_year']
            import_method = form.cleaned_data['import_method']
            starting_term = form.cleaned_data.get('starting_term')
            
            # Create batch
            batch = ArrearsImportService.create_import_batch(
                academic_year=academic_year,
                import_method=import_method,
                user=request.user,
                starting_term=starting_term
            )
            
            # Redirect based on import method
            if import_method == 'MANUAL':
                return redirect('arrears_import_manual_entry', batch_id=batch.batch_id)
            elif import_method == 'BULK_UPLOAD':
                return redirect('arrears_import_bulk_upload', batch_id=batch.batch_id)
            else:
                return redirect('arrears_import_copy_previous', batch_id=batch.batch_id)
    else:
        form = ArrearsImportInitializationForm()
    
    context = {
        'form': form,
        'page_title': 'Arrears Import Setup',
        'step': 1,
        'total_steps': 4
    }
    
    return render(request, 'arrears/import_wizard_start.html', context)


@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
def arrears_import_manual_entry(request, batch_id):
    """Phase 2a: Manual entry of arrears one student at a time"""
    
    batch = get_object_or_404(ArrearsImportBatch, batch_id=batch_id)
    
    if not batch.is_editable:
        # messages.error(request, 'This import batch is no longer editable')
        return redirect('arrears_import_summary', batch_id=batch.batch_id)
    
    if request.method == 'POST':
        if 'add_student' in request.POST:
            form = StudentArrearsEntryForm(request.POST, request.FILES)
            if form.is_valid():
                student = form.cleaned_data['student']
                amount = form.cleaned_data['arrears_amount']
                
                entry = ArrearsImportService.add_arrears_entry(
                    batch=batch,
                    student=student,
                    amount=amount,
                    description=form.cleaned_data.get('arrears_description', ''),
                    date_incurred=form.cleaned_data.get('date_incurred'),
                    user=request.user
                )
                
                # messages.success(request, f'Added {student.full_name} with ${amount} arrears')
                
                # Save file if provided
                if 'supporting_document' in request.FILES:
                    entry.supporting_document = request.FILES['supporting_document']
                    entry.save()
                
                return redirect('arrears_import_manual_entry', batch_id=batch.batch_id)
        else:
            form = StudentArrearsEntryForm()
    else:
        form = StudentArrearsEntryForm()
    
    # Get existing entries
    entries = batch.entries.all().order_by('-arrears_amount')
    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'batch': batch,
        'entries': page_obj,
        'total_entries': entries.count(),
        'total_arrears': batch.total_arrears_amount,
        'page_title': 'Manual Arrears Entry',
        'step': 2,
        'total_steps': 4
    }
    
    return render(request, 'arrears/import_manual_entry.html', context)


@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
def arrears_import_bulk_upload(request, batch_id):
    """Phase 2b: Bulk upload via Excel/CSV"""
    
    batch = get_object_or_404(ArrearsImportBatch, batch_id=batch_id)
    
    if not batch.is_editable:
        # messages.error(request, 'This import batch is no longer editable')
        return redirect('arrears_import_summary', batch_id=batch.batch_id)
    
    if request.method == 'POST':
        form = BulkArrearsUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = request.FILES['upload_file']
            batch.upload_file = upload_file
            batch.save()
            
            # Process file
            result = _process_bulk_upload(batch, upload_file, request.user)
            
            if result['success']:
                # messages.success(request, f"Imported {result['imported']} students with arrears. {result['errors']} errors found.")
                return redirect('arrears_import_summary', batch_id=batch.batch_id)
            else:
                # messages.error(request, f"Upload failed: {result['error']}")
                pass
    else:
        form = BulkArrearsUploadForm()
    
    context = {
        'form': form,
        'batch': batch,
        'download_template': _generate_csv_template(batch),
        'page_title': 'Bulk Upload Arrears',
        'step': 2,
        'total_steps': 4
    }
    
    return render(request, 'arrears/import_bulk_upload.html', context)


@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
@require_http_methods(['GET'])
def arrears_import_download_template(request, batch_id):
    """Download CSV template for bulk import"""
    
    batch = get_object_or_404(ArrearsImportBatch, batch_id=batch_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="arrears_template_{batch.batch_id}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Arrears Amount', 'Description', 'Date Incurred'])
    writer.writerow(['Example:', '1', 'Student A', '80.00', '2026 unpaid fees', '2026-12-31'])
    writer.writerow(['', '2', 'Student B', '150.00', '2026 unpaid fees', '2026-12-31'])
    
    # Add actual students
    active_students = Student.objects.filter(is_deleted=False).order_by('surname', 'first_name')
    for student in active_students[:50]:  # Limit to first 50
        writer.writerow([student.id, student.full_name, '', '', ''])
    
    return response


@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
def arrears_import_summary(request, batch_id):
    """Phase 3: Review and confirm import before proceeding"""
    
    batch = get_object_or_404(ArrearsImportBatch, batch_id=batch_id)
    
    if batch.status == 'DRAFT':
        # Validate batch
        errors, warnings = ArrearsImportService.validate_batch(batch)
        
        if errors:
            batch.status = 'VALIDATING'
            batch.processing_notes = f"Validation errors: {'; '.join(errors)}"
            batch.save()
            
            context = {
                'batch': batch,
                'errors': errors,
                'warnings': warnings,
                'page_title': 'Validation Issues Found',
                'step': 3,
                'total_steps': 4
            }
            
            return render(request, 'arrears/import_validation_errors.html', context)
        
        batch.status = 'READY'
        batch.save()
    
    # Generate summary
    summary = ArrearsImportService.generate_import_summary_report(batch)
    
    if request.method == 'POST':
        form = PreImportConfirmationForm(request.POST)
        if form.is_valid():
            try:
                # Ensure batch is READY before importing
                if batch.status != 'READY':
                    batch.status = 'READY'
                    batch.save()
                
                result = ArrearsImportService.apply_arrears_to_balance(batch)
                
                # messages.success(request, f"✅ Successfully imported {result['imported_count']} students' arrears")
                
                if result['failed_count'] > 0:
                    messages.warning(
                        request,
                        f"⚠️ {result['failed_count']} entries failed to import"
                    )
                
                return redirect('arrears_import_complete', batch_id=batch.batch_id)
            except Exception as e:
                logger.error(f"Arrears import failed: {str(e)}")
                # messages.error(request, f"Import failed: {str(e)}")
                pass
    else:
        form = PreImportConfirmationForm()
    
    entries = batch.entries.all()
    
    context = {
        'form': form,
        'batch': batch,
        'summary': summary,
        'entries': entries,
        'page_title': 'Import Summary & Confirmation',
        'step': 3,
        'total_steps': 4
    }
    
    return render(request, 'arrears/import_summary.html', context)


@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
def arrears_import_complete(request, batch_id):
    """Phase 4: Import complete - show results and next steps"""
    
    batch = get_object_or_404(ArrearsImportBatch, batch_id=batch_id)
    
    if batch.status != 'IMPORTED':
        return redirect('arrears_import_summary', batch_id=batch.batch_id)
    
    # Get import results
    entries = batch.entries.filter(is_imported=True)
    failed_entries = batch.entries.filter(error_message__isnull=False).exclude(error_message='')
    
    # Sample student statements
    sample_students = entries[:5]
    statements = [
        ArrearsImportService.get_student_statement_after_import(entry.student, batch)
        for entry in sample_students
    ]
    
    context = {
        'batch': batch,
        'imported_count': entries.count(),
        'failed_count': failed_entries.count(),
        'failed_entries': failed_entries,
        'sample_statements': statements,
        'page_title': 'Import Completed Successfully',
        'step': 4,
        'total_steps': 4
    }
    
    return render(request, 'arrears/import_complete.html', context)


# Helper functions

def _process_bulk_upload(batch, upload_file, user):
    """Process uploaded CSV/Excel file and import entries"""
    try:
        # Simple CSV processing
        imported = 0
        errors = 0
        
        # Decode file
        content = upload_file.read().decode('utf-8')
        reader = csv.DictReader(content.splitlines())
        
        for row in reader:
            try:
                # Find student by ID or name
                student_id = row.get('Student ID', '').strip()
                student_name = row.get('Student Name', '').strip()
                amount_str = row.get('Arrears Amount', '').strip()
                
                if not amount_str:
                    errors += 1
                    continue
                
                amount = Decimal(amount_str)
                
                # Find student
                if student_id:
                    student = Student.objects.get(id=student_id, is_deleted=False)
                elif student_name:
                    parts = student_name.split()
                    student = Student.objects.get(
                        surname=parts[-1],
                        first_name=' '.join(parts[:-1]),
                        is_deleted=False
                    )
                else:
                    errors += 1
                    continue
                
                # Add entry
                ArrearsImportService.add_arrears_entry(
                    batch=batch,
                    student=student,
                    amount=amount,
                    description=row.get('Description', ''),
                    user=user
                )
                imported += 1
                
            except Exception as e:
                logger.warning(f"Error importing row {row}: {str(e)}")
                errors += 1
                continue
        
        return {
            'success': True,
            'imported': imported,
            'errors': errors
        }
        
    except Exception as e:
        logger.error(f"Bulk upload processing failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def _generate_csv_template(batch):
    """Generate CSV template content"""
    return """Student ID,Student Name,Arrears Amount,Description,Date Incurred
1,Student A,80.00,2026 unpaid fees,2026-12-31
2,Student B,150.00,2026 unpaid fees,2026-12-31"""
