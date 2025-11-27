from django import template
from django.forms.widgets import TextInput, Select, Textarea, DateInput, NumberInput, EmailInput

register = template.Library()

@register.filter(name='add_classes')
def add_classes(field, css_classes):
    """Add CSS classes to a form field"""
    if field.field.widget.__class__ in [TextInput, Select, DateInput, NumberInput, EmailInput]:
        field.field.widget.attrs['class'] = f'form-input {css_classes}'
    elif field.field.widget.__class__ == Textarea:
        field.field.widget.attrs['class'] = f'form-textarea {css_classes}'
    return field