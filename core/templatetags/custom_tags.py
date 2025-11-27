from django import template
from core.models.school_details import SchoolDetails

register = template.Library()

@register.simple_tag
def school_name_tag():
    """Return the school name from SchoolDetails"""
    try:
        school = SchoolDetails.get_or_create_default()
        return school.school_name or ""
    except:
        return ""
