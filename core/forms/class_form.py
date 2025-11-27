from django import forms
from ..models.class_model import Class
from ..models.administrator import Administrator

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['grade', 'section', 'academic_year', 'teacher']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show teachers for the teacher field
        self.fields['teacher'].queryset = Administrator.objects.filter(is_teacher=True)
        # Add required classes for styling
        for field in self.fields.values():
            field.widget.attrs['class'] = 'mt-1 block w-full px-4 py-3 rounded-xl border-0 bg-white bg-opacity-50 backdrop-blur-sm shadow-lg focus:ring-2 focus:ring-teal-500 focus:bg-opacity-70 transition-all duration-200 text-gray-700'