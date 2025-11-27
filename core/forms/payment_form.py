from django import forms
from core.models.academic import Payment
from core.models.student import Student


class PaymentForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(is_archived=False),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-primary',
            'required': True,
        })
    )
    
    class Meta:
        model = Payment
        fields = ['student', 'amount', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-primary',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'required': True,
            }),
            'payment_method': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-primary',
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-primary',
                'placeholder': 'Leave blank to auto-generate based on payment method',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-primary resize-none',
                'rows': 3,
                'placeholder': 'Add any notes about this payment...',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make reference_number optional with help text
        self.fields['reference_number'].required = False
        self.fields['reference_number'].help_text = (
            '<small class="text-slate-400">Leave blank for automatic generation '
            'based on payment method (CSH, BNK, MOB, CHQ)</small>'
        )

    def _post_clean(self):
        """
        Override _post_clean to skip model instance validation.
        The model's clean() expects 'term' to be set, which happens in view's form_valid().
        """
        # Don't call the model's full_clean() - just validate fields
        # This is where ModelForm would call instance.full_clean()
        # We skip it here and let the view handle model validation after setting term
        pass

    def clean(self):
        """Form-level validation only (not model-level)"""
        cleaned_data = super().clean()
        
        student = cleaned_data.get('student')
        amount = cleaned_data.get('amount')

        if not student:
            self.add_error('student', 'Please select a student')

        if amount is not None and amount < 0:
            self.add_error('amount', 'Amount cannot be negative')
        
        return cleaned_data
