from django import forms
from ..models.class_model import Class
from ..models.administrator import Administrator

class ClassForm(forms.ModelForm):
    # Explicitly declare grade field to ensure ECD choice is included
    grade = forms.ChoiceField(
        choices=Class.GRADE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-4 py-3 rounded-xl border-0 bg-white bg-opacity-50 backdrop-blur-sm shadow-lg focus:ring-2 focus:ring-teal-500 focus:bg-opacity-70 transition-all duration-200 text-gray-700',
        }),
        help_text='Choose the grade level (ECD → Grade 1-7)'
    )
    
    class Meta:
        model = Class
        fields = ['grade', 'section', 'academic_year', 'teacher']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Refresh grade choices from model (ensures ECD is included)
        self.fields['grade'].choices = Class.GRADE_CHOICES
        
        # Only show teachers for the teacher field
        self.fields['teacher'].queryset = Administrator.objects.filter(is_teacher=True)
        
        # Add required classes for styling
        for field_name, field in self.fields.items():
            if field_name != 'grade':  # Skip grade, already styled above
                field.widget.attrs['class'] = 'mt-1 block w-full px-4 py-3 rounded-xl border-0 bg-white bg-opacity-50 backdrop-blur-sm shadow-lg focus:ring-2 focus:ring-teal-500 focus:bg-opacity-70 transition-all duration-200 text-gray-700'