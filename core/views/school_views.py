from django.shortcuts import render, redirect
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from core.models.school_details import SchoolDetails


class SchoolDetailsUpdateView(LoginRequiredMixin, UpdateView):
    """View to update school details"""
    model = SchoolDetails
    template_name = 'settings/school_details.html'
    context_object_name = 'school'
    success_url = reverse_lazy('school_details')
    
    fields = [
        'school_name', 'school_motto', 'school_type',
        'principal_name', 'email', 'phone', 'alternate_phone',
        'street_address', 'city', 'state', 'country',
        'established_year', 'board_affiliation',
        'registration_number',
        'working_days_per_week'
    ]
    
    def get_object(self, queryset=None):
        """Get or create default school details"""
        return SchoolDetails.get_or_create_default()
    
    def form_valid(self, form):
        messages.success(self.request, 'School details updated successfully!')
        return super().form_valid(form)


def school_details_view(request):
    """Display school details"""
    school = SchoolDetails.get_or_create_default()
    context = {
        'school': school,
    }
    return render(request, 'settings/school_details_view.html', context)
