"""
Setup wizard views for fresh system initialization
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from core.models.school_details import SchoolDetails


class FreshSystemSetupView(LoginRequiredMixin, TemplateView):
    """Setup wizard for fresh systems that need configuration"""
    template_name = 'setup/fresh_system_setup.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if system is still fresh
        context['is_fresh_system'] = getattr(self.request, 'is_fresh_system', False)
        
        # Get school details for status display
        try:
            school = SchoolDetails.get_or_create_default()
            context['school'] = school
            
            # Create a setup checklist
            context['setup_steps'] = [
                {
                    'title': 'School Details',
                    'description': 'Configure school name, motto, contact information, and location',
                    'completed': school.school_name != 'Your School Name',
                    'url': 'school_details',
                },
                {
                    'title': 'Academic Structure',
                    'description': 'Set up academic years and terms for your school',
                    'completed': False,
                    'url': 'academic_year_list',
                },
                {
                    'title': 'Classes Setup',
                    'description': 'Create grades and sections for your school',
                    'completed': False,
                    'url': 'class_list',
                },
                {
                    'title': 'Teachers & Staff',
                    'description': 'Add administrators and teachers to the system',
                    'completed': False,
                    'url': 'administrator_list',
                },
                {
                    'title': 'Fee Structure',
                    'description': 'Configure term fees for classes',
                    'completed': False,
                    'url': 'term_fee_list',
                },
            ]
            
            # Calculate completion percentage
            completed_steps = sum(1 for step in context['setup_steps'] if step['completed'])
            context['completion_percentage'] = int((completed_steps / len(context['setup_steps'])) * 100)
            context['completed_steps'] = completed_steps
            context['total_steps'] = len(context['setup_steps'])
            
        except Exception as e:
            context['error'] = str(e)
        
        return context
