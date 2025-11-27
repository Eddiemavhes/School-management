"""
Superuser Forms
"""
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from core.models.administrator import Administrator


class ResetAdminPasswordForm(forms.Form):
    """Form to reset administrator password"""
    admin = forms.ModelChoiceField(
        queryset=Administrator.objects.all(),
        label='Select Administrator',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-slate-700 border border-slate-600 text-white'
        })
    )
    
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-slate-700 border border-slate-600 text-white',
            'placeholder': 'Enter new password'
        }),
        min_length=8
    )
    
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-slate-700 border border-slate-600 text-white',
            'placeholder': 'Confirm password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')
        
        if password and confirm:
            if password != confirm:
                raise ValidationError('Passwords do not match!')
        
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('new_password', e)
        
        return cleaned_data
