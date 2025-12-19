from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from core.models import (
    ArrearsImportBatch, 
    ArrearsImportEntry, 
    Student, 
    AcademicYear,
    AcademicTerm
)
import csv
from io import TextIOWrapper


class ArrearsImportInitializationForm(forms.Form):
    """Phase 1: Setup academic year and import method"""
    
    IMPORT_METHOD_CHOICES = [
        ('MANUAL', '📝 Manual Entry - Add students one-by-one'),
        ('BULK_UPLOAD', '📄 Bulk Upload - Import Excel/CSV file'),
        ('COPY_PREVIOUS', '🔄 Copy from Previous System - Select existing data'),
    ]
    
    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all().order_by('-year'),
        label='Academic Year',
        help_text='Select the year to import arrears for',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-slate-300 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 transition'
        })
    )
    
    starting_term = forms.ModelChoiceField(
        queryset=AcademicTerm.objects.all(),
        label='Starting Term',
        required=False,
        help_text='Optional: Select starting term (defaults to Term 1)',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-slate-300 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 transition'
        })
    )
    
    import_method = forms.ChoiceField(
        choices=IMPORT_METHOD_CHOICES,
        label='Choose Import Method',
        help_text='Select how you want to enter arrears data',
        widget=forms.RadioSelect(attrs={
            'class': 'space-y-3'
        })
    )


class StudentArrearsEntryForm(forms.Form):
    """Phase 2a: Manual single student arrears entry"""
    
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(is_deleted=False).order_by('surname', 'first_name'),
        label='Select Student',
        empty_label='--- Search by name ---',
        help_text='Type to search for student',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-slate-300 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 transition'
        })
    )
    
    arrears_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label='Arrears Amount ($)',
        help_text='Outstanding balance from previous system',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-slate-300 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 transition',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )
    
    arrears_description = forms.CharField(
        max_length=255,
        required=False,
        label='Description (Optional)',
        help_text='e.g., "2026 unpaid fees" or "2025-2026 cumulative"',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-slate-300 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 transition',
            'placeholder': 'Enter description...'
        })
    )
    
    date_incurred = forms.DateField(
        required=False,
        label='Date Incurred (Optional)',
        help_text='When did this arrears originate?',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-slate-300 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 transition'
        })
    )
    
    supporting_document = forms.FileField(
        required=False,
        label='Supporting Document (Optional)',
        help_text='Upload PDF or image of proof',
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-slate-300 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 transition',
            'accept': '.pdf,.png,.jpg,.jpeg,.gif'
        })
    )


class ConfirmArrearsAmountForm(forms.Form):
    """Verification: Double-entry confirmation of amount"""
    
    confirmed_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Re-enter Amount to Confirm ($)',
        help_text='Please enter the amount again to verify accuracy',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-slate-300 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 transition',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )
    
    def __init__(self, *args, original_amount=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_amount = original_amount


class BulkArrearsUploadForm(forms.Form):
    """Phase 2b: Bulk upload via Excel/CSV"""
    
    upload_file = forms.FileField(
        label='Upload Excel or CSV File',
        help_text='File must contain columns: Student ID/Name, Arrears Amount, Description',
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-slate-300 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 transition',
            'accept': '.xlsx,.xls,.csv'
        })
    )
    
    def clean_upload_file(self):
        """Validate and preview file"""
        file = self.cleaned_data.get('upload_file')
        if file:
            if not file.name.lower().endswith(('.xlsx', '.xls', '.csv')):
                raise ValidationError('File must be Excel (.xlsx, .xls) or CSV format')
            
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError('File size must be less than 5MB')
        
        return file


class PreImportConfirmationForm(forms.Form):
    """Phase 3: Final confirmation before import"""
    
    confirm_accuracy = forms.BooleanField(
        label='I confirm that all entered amounts are accurate and complete',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 rounded border-gray-300 text-cyan-600 focus:ring-2 focus:ring-cyan-500'
        })
    )
    
    confirm_apply_to_balance = forms.BooleanField(
        label='Apply these arrears to student balances immediately',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 rounded border-gray-300 text-cyan-600 focus:ring-2 focus:ring-cyan-500'
        })
    )
    
    import_notes = forms.CharField(
        max_length=500,
        required=False,
        label='Import Notes (Optional)',
        help_text='Any additional notes about this import',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-slate-300 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 transition',
            'rows': 3,
            'placeholder': 'Add any notes...'
        })
    )
