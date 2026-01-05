from django import forms
from ..models import Student
from ..models.academic_year import AcademicYear

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['surname', 'first_name', 'sex', 'date_of_birth', 
                 'birth_entry_number', 'current_class']
        widgets = {
            'surname': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'sex': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input datepicker', 'type': 'date'}),
            'birth_entry_number': forms.TextInput(attrs={'class': 'form-input'}),
            'current_class': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow selecting classes from any academic year, not just the active one
        # This lets users work with non-active years (pending/created years)
        # Make the class field required
        self.fields['current_class'].required = True