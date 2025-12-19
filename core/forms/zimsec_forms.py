"""
Forms for ZIMSEC Grade 7 Examination Management
"""

from django import forms
from core.models.zimsec import ZimsecResults
from core.models.student import Student
from core.models.academic import AcademicTerm

class ZimsecResultsForm(forms.ModelForm):
    """Form for entering individual ZIMSEC results"""
    
    class Meta:
        model = ZimsecResults
        fields = [
            'english_units', 'mathematics_units', 'science_units',
            'social_studies_units', 'indigenous_language_units', 'agriculture_units',
            'exam_center', 'candidate_number', 'result_date'
        ]
        widgets = {
            'english_units': forms.NumberInput(attrs={
                'class': 'form-control units-input',
                'min': '1', 'max': '9',
                'placeholder': '1-5 Pass | 6-9 Fail'
            }),
            'mathematics_units': forms.NumberInput(attrs={
                'class': 'form-control units-input',
                'min': '1', 'max': '9',
                'placeholder': '1-5 Pass | 6-9 Fail'
            }),
            'science_units': forms.NumberInput(attrs={
                'class': 'form-control units-input',
                'min': '1', 'max': '9',
                'placeholder': '1-5 Pass | 6-9 Fail'
            }),
            'social_studies_units': forms.NumberInput(attrs={
                'class': 'form-control units-input',
                'min': '1', 'max': '9',
                'placeholder': '1-5 Pass | 6-9 Fail'
            }),
            'indigenous_language_units': forms.NumberInput(attrs={
                'class': 'form-control units-input',
                'min': '1', 'max': '9',
                'placeholder': '1-5 Pass | 6-9 Fail'
            }),
            'agriculture_units': forms.NumberInput(attrs={
                'class': 'form-control units-input',
                'min': '1', 'max': '9',
                'placeholder': '1-5 Pass | 6-9 Fail'
            }),
            'exam_center': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'School name or exam center'
            }),
            'candidate_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIMSEC candidate number'
            }),
            'result_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class BulkZimsecEntryForm(forms.Form):
    """Form for bulk ZIMSEC results entry"""
    
    academic_year = forms.IntegerField(
        min_value=2020,
        max_value=2099,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2027'
        })
    )
    
    grade_7_class = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Grade 7 Class',
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.models import Class
        # Only show Grade 7 classes
        self.fields['grade_7_class'].queryset = Class.objects.filter(grade=7)


class ZimsecComparisonForm(forms.Form):
    """Form for year-over-year comparison"""
    
    academic_year_1 = forms.IntegerField(
        min_value=2020,
        max_value=2099,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'First year (e.g., 2026)'
        }),
        label='Academic Year 1'
    )
    
    academic_year_2 = forms.IntegerField(
        min_value=2020,
        max_value=2099,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Second year (e.g., 2027)'
        }),
        label='Academic Year 2'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        year1 = cleaned_data.get('academic_year_1')
        year2 = cleaned_data.get('academic_year_2')
        
        if year1 and year2 and year1 == year2:
            raise forms.ValidationError("Please select two different academic years.")
        
        return cleaned_data
