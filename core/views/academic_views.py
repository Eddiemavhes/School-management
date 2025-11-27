from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
import json
from datetime import timedelta

from core.models import AcademicYear, AcademicTerm, TermFee
from core.models.fee import StudentBalance

class AcademicYearListView(LoginRequiredMixin, ListView):
    model = AcademicYear
    template_name = 'academic/year_list.html'
    context_object_name = 'academic_years'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_year'] = AcademicYear.get_current_year()
        return context

class AcademicYearCreateView(LoginRequiredMixin, CreateView):
    model = AcademicYear
    template_name = 'academic/year_form.html'
    fields = ['year', 'start_date', 'end_date']
    success_url = reverse_lazy('academic_year_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Academic Year {form.instance.year} created successfully")
        return response

class AcademicYearDetailView(LoginRequiredMixin, DetailView):
    model = AcademicYear
    template_name = 'academic/year_detail.html'
    context_object_name = 'academic_year'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        academic_year = self.get_object()
        
        # Get terms for this academic year
        context['terms'] = academic_year.get_terms()
        
        # Get financial summary
        context['financial_summary'] = academic_year.get_financial_summary()
        
        return context

@require_http_methods(["POST"])
def create_academic_terms(request, year_id):
    academic_year = get_object_or_404(AcademicYear, id=year_id)
    data = json.loads(request.body)
    
    try:
        # Validate term dates
        terms_data = []
        for term_num in range(1, 4):
            term_key = f'term{term_num}'
            if term_key not in data:
                raise ValueError(f"Data for {term_key} is missing")

            term_data = data[term_key]
            terms_data.append({
                'start_date': term_data['start_date'],
                'end_date': term_data['end_date'],
                'fee_amount': term_data['fee_amount']
            })

        # Create terms
        academic_year.create_terms(terms_data)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Academic terms created successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(["POST"])
def activate_academic_year(request, year_id):
    academic_year = get_object_or_404(AcademicYear, id=year_id)
    try:
        academic_year.activate()
        messages.success(request, f"Academic Year {academic_year.year} is now active")
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_http_methods(["POST"])
def rollover_academic_year(request, year_id):
    current_year = get_object_or_404(AcademicYear, id=year_id)
    
    try:
        new_year = current_year.rollover_to_new_year()
        messages.success(
            request,
            f"Successfully rolled over to Academic Year {new_year.year}. "
            "Student promotions and arrears have been processed."
        )
        return JsonResponse({
            'status': 'success',
            'new_year_id': new_year.id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)