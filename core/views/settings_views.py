from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from ..models.academic import AcademicTerm
from ..models.academic_year import AcademicYear
from ..models.fee import TermFee
from ..models import Administrator
from django.shortcuts import get_object_or_404
import json

class AdminSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'settings/admin_settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_term'] = AcademicTerm.get_current_term()
        context['terms'] = AcademicTerm.objects.all().order_by('-academic_year', '-term')
        context['term_fees'] = TermFee.objects.select_related('term').order_by('-term__academic_year', '-term__term')
        context['academic_years'] = AcademicYear.objects.all().order_by('-year')
        
        # Get current active year and its terms
        current_year = AcademicYear.objects.filter(is_active=True).first()
        context['current_year'] = current_year
        
        if current_year:
            # Get all terms for this year
            context['current_year_terms'] = AcademicTerm.objects.filter(
                academic_year=current_year.year
            ).order_by('term')
            
            # Get all fees for this year's terms
            context['current_year_fees'] = TermFee.objects.filter(
                term__academic_year=current_year.year
            ).order_by('term__term')
            
            # Calculate totals and average
            fees_list = list(context['current_year_fees'].values_list('amount', flat=True))
            total_fees = sum(fees_list) if fees_list else 0
            average_fee = total_fees / len(fees_list) if fees_list else 0
            
            context['total_annual_fees'] = f"{total_fees:.2f}"
            context['average_fee'] = f"{average_fee:.2f}"
        
        return context

@method_decorator(login_required, name='dispatch')
class AdminProfileUpdateView(UpdateView):
    model = Administrator
    template_name = 'settings/admin_profile.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number']
    success_url = reverse_lazy('admin_settings')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully.')
        return response

@login_required
@require_http_methods(["POST"])
def update_admin_password(request):
    if not request.user.check_password(request.POST.get('current_password')):
        messages.error(request, 'Current password is incorrect.')
        return redirect('admin_settings')

    if request.POST.get('new_password1') != request.POST.get('new_password2'):
        messages.error(request, 'New passwords do not match.')
        return redirect('admin_settings')

    request.user.set_password(request.POST.get('new_password1'))
    request.user.save()
    messages.success(request, 'Password updated successfully.')
    return redirect('login')

@login_required
@require_http_methods(["GET", "POST"])
def create_academic_term(request):
    """Create or update academic terms and their fees for the current year"""
    from datetime import datetime
    
    # Handle GET requests by redirecting to settings
    if request.method == 'GET':
        return redirect('admin_settings')
    
    # Log the request
    print("\n" + "=" * 70)
    print("📍 VIEW CALLED: create_academic_term")
    print(f"Method: {request.method}")
    print(f"User: {request.user}")
    print(f"POST data keys: {list(request.POST.keys())}")
    print("=" * 70)
    
    if request.method != 'POST':
        return redirect('admin_settings')
    
    # Check if user is logged in
    if not request.user.is_authenticated:
        messages.error(request, '❌ You must be logged in.')
        return redirect('login')
    
    try:
        current_year = AcademicYear.objects.filter(is_active=True).first()
        if not current_year:
            messages.error(request, '❌ No active academic year found. Please set one in Admin Panel.')
            print("ERROR: No active academic year")
            return redirect('admin_settings')
        
        print(f"✓ Active year found: {current_year.year}")
        
        created_terms = []
        has_data = False
        errors = []
        
        # Process all three terms (Term 1, 2, 3)
        for term_num in [1, 2, 3]:
            term_key = f'term_{term_num}'
            start_date_key = f'{term_key}_start'
            end_date_key = f'{term_key}_end'
            fee_key = f'{term_key}_fee'
            current_key = f'{term_key}_current'
            
            # Get the data
            start_date = request.POST.get(start_date_key, '').strip()
            end_date = request.POST.get(end_date_key, '').strip()
            fee_amount = request.POST.get(fee_key, '').strip()
            is_current = request.POST.get(current_key) == 'on'
            
            print(f"\n  Term {term_num}:")
            print(f"    start: '{start_date}'")
            print(f"    end:   '{end_date}'")
            print(f"    fee:   '{fee_amount}'")
            print(f"    current: {is_current}")
            
            # Skip if no data
            if not (start_date or end_date or fee_amount):
                print(f"    → SKIP (no data)")
                continue
            
            has_data = True
            
            # MUST have both dates
            if not start_date or not end_date:
                msg = f'Term {term_num}: Need BOTH start AND end dates'
                messages.warning(request, msg)
                print(f"    ❌ {msg}")
                continue
            
            try:
                # Parse dates
                start_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                if start_obj >= end_obj:
                    msg = f'Term {term_num}: Start must be BEFORE end'
                    messages.warning(request, msg)
                    print(f"    ❌ {msg}")
                    continue
                
                print(f"    ✓ Dates valid: {start_obj} → {end_obj}")
                
                # CREATE THE TERM
                term, created = AcademicTerm.objects.update_or_create(
                    academic_year=current_year.year,
                    term=term_num,
                    defaults={
                        'start_date': start_date,
                        'end_date': end_date,
                        'is_current': False  # ALWAYS False on creation - use progression controls
                    }
                )
                print(f"    ✓ Term {term_num} {'CREATED' if created else 'UPDATED'}")
                print(f"    NOTE: is_current set to False. Use Term Progression controls to activate terms.")
                
                # DO NOT mark as current here - only progression system can do that
                print(f"    ✓ Refused to mark as CURRENT (use progression controls instead)")
                
                # CREATE THE FEE
                if fee_amount:
                    try:
                        fee_float = float(fee_amount)
                        if fee_float < 0:
                            msg = f'Term {term_num}: Fee cannot be negative'
                            messages.warning(request, msg)
                            continue
                        
                        term_fee, fee_created = TermFee.objects.update_or_create(
                            term=term,
                            defaults={
                                'amount': fee_float
                            }
                        )
                        print(f"    ✓ Fee ${fee_float} {'CREATED' if fee_created else 'UPDATED'}")
                        created_terms.append(f'Term {term_num}')
                    except ValueError:
                        msg = f'Term {term_num}: Invalid fee amount'
                        messages.warning(request, msg)
                        print(f"    ❌ {msg}")
                        continue
                else:
                    print(f"    ℹ No fee provided")
                    created_terms.append(f'Term {term_num}')
                    
            except ValueError as ve:
                msg = f'Term {term_num}: Date error - {str(ve)}'
                messages.warning(request, msg)
                print(f"    ❌ {msg}")
                continue
            except Exception as e:
                msg = f'Term {term_num}: {str(e)}'
                messages.error(request, msg)
                print(f"    ❌ {msg}")
                continue
        
        # Show results
        print(f"\n  Summary:")
        print(f"    has_data: {has_data}")
        print(f"    saved: {len(created_terms)}")
        
        if created_terms:
            msg = f'✅ Saved {len(created_terms)} term(s): {", ".join(created_terms)}'
            messages.success(request, msg)
            print(f"  ✓ {msg}")
        elif has_data:
            msg = '⚠️ No terms saved - check errors above'
            messages.warning(request, msg)
            print(f"  ⚠️ {msg}")
        else:
            msg = '📝 Fill in at least one term to save'
            messages.info(request, msg)
            print(f"  ℹ {msg}")
            
    except Exception as e:
        msg = f'❌ Error: {str(e)}'
        messages.error(request, msg)
        print(f"  ❌ {msg}")
    finally:
        print("=" * 70 + "\n")
    
    return redirect('admin_settings')

@login_required
@require_http_methods(["POST"])
def set_current_term(request):
    try:
        term_id = request.POST.get('term_id')
        if not term_id:
            messages.error(request, '❌ No term selected.')
            return redirect('admin_settings')

        term = AcademicTerm.objects.get(id=term_id)
        current_term = AcademicTerm.get_current_term()
        
        # Check if trying to move to a previous term
        if current_term and term.term < current_term.term and current_term.academic_year == term.academic_year:
            messages.error(request, '❌ Cannot move back to previous terms. Terms can only progress forward (Term 1 → 2 → 3).')
            return redirect('admin_settings')
        
        # Check if current term can move to next term
        if current_term and current_term.term == term.term - 1 and current_term.academic_year == term.academic_year:
            if current_term.is_completed:
                messages.error(request, f'❌ Cannot change terms. {current_term} has already been completed.')
                return redirect('admin_settings')
        
        # If moving away from current term, mark it as completed
        if current_term and current_term.id != term.id:
            current_term.is_completed = True
            current_term.is_current = False
            current_term.save()
        
        # Set all terms to not current
        AcademicTerm.objects.all().update(is_current=False)
        
        # Set the selected term as current
        term.is_current = True
        term.is_completed = False  # Reset completed flag for the new current term
        term.save()
        
        messages.success(request, f'✅ {term} is now active! {term.start_date.strftime("%B %d")} – {term.end_date.strftime("%B %d, %Y")}')
    except AcademicTerm.DoesNotExist:
        messages.error(request, '❌ Term not found.')
    except Exception as e:
        messages.error(request, f'❌ Error setting current term: {str(e)}')
    
    return redirect('admin_settings')

@login_required
@login_required
@require_http_methods(["POST"])
def update_term_fee(request):
    try:
        term = AcademicTerm.objects.get(id=request.POST.get('term_id'))
        TermFee.objects.create(
            term=term,
            amount=request.POST.get('amount')
        )
        messages.success(request, f'Term fee has been set for {term}.')
    except AcademicTerm.DoesNotExist:
        messages.error(request, 'Term not found.')
    except Exception as e:
        messages.error(request, f'Error setting term fee: {str(e)}')
    return redirect('admin_settings')

@login_required
@require_http_methods(["POST"])
def create_academic_year(request):
    try:
        year = int(request.POST.get('year'))
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active', '') == 'on'
        
        # If setting this year as active, deactivate all others
        if is_active:
            AcademicYear.objects.all().update(is_active=False)
        
        academic_year, created = AcademicYear.objects.get_or_create(
            year=year,
            defaults={
                'start_date': start_date,
                'end_date': end_date,
                'is_active': is_active
            }
        )
        
        if created:
            messages.success(request, f'Academic year {year} has been created successfully.')
        else:
            messages.info(request, f'Academic year {year} already exists.')
            
    except ValueError:
        messages.error(request, 'Invalid year format.')
    except Exception as e:
        messages.error(request, f'Error creating academic year: {str(e)}')
    
    return redirect('admin_settings')

@login_required
@require_http_methods(["POST"])
def set_active_year(request):
    try:
        year_id = request.POST.get('year_id')
        if not year_id:
            messages.error(request, '❌ No year selected.')
            return redirect('admin_settings')

        year = AcademicYear.objects.get(id=year_id)
        current_year = AcademicYear.objects.filter(is_active=True).first()
        
        # Check if trying to move to a previous year
        if current_year and year.year < current_year.year:
            messages.error(request, '❌ Cannot move back to previous years. Academic years can only progress forward.')
            return redirect('admin_settings')
        
        # Check if trying to skip years
        if current_year and year.year > current_year.year + 1:
            messages.error(request, '❌ Cannot skip academic years. You must be on the final year to proceed to the next one.')
            return redirect('admin_settings')
        
        # If trying to move to next year, check if currently on Term 3
        if current_year and year.year > current_year.year:
            if not current_year.is_on_final_term():
                current_term = current_year.get_current_term()
                current_term_name = current_term.get_term_display() if current_term else "Unknown"
                messages.error(request, f'❌ Cannot move to next year yet. You are currently on {current_term_name}. You must complete all terms (reach Term 3) before moving to the next academic year.')
                return redirect('admin_settings')
            
            # Mark current year as completed
            current_year.is_completed = True
            current_year.is_active = False
            current_year.save()
        
        # Deactivate all years
        AcademicYear.objects.all().update(is_active=False)
        
        # Activate the selected year
        year.is_active = True
        year.is_completed = False  # Reset completed flag
        year.save()
        
        messages.success(request, f'✅ Academic Year {year.year} is now active! {year.start_date.strftime("%B %d, %Y")} – {year.end_date.strftime("%B %d, %Y")}')
    except AcademicYear.DoesNotExist:
        messages.error(request, '❌ Academic year not found.')
    except Exception as e:
        messages.error(request, f'❌ Error setting active year: {str(e)}')
    
    return redirect('admin_settings')

# NOTE: The detailed `create_academic_term` handler is defined above and
# performs full validation, creation and updating of terms and fees. The
# legacy simple handler was removed to ensure the enhanced logic is used.

@login_required
@require_http_methods(["POST"])
def create_fee(request):
    try:
        fee_name = request.POST.get('fee_name')
        fee_amount = request.POST.get('fee_amount')
        grade = request.POST.get('grade', '')
        
        if not fee_name or not fee_amount:
            messages.error(request, 'Please fill all required fields.')
            return redirect('admin_settings')
        
        grade_text = f'Grade {grade}' if grade else 'All Grades'
        messages.success(request, f'Fee "{fee_name}" (${fee_amount}) has been added for {grade_text}.')
    except Exception as e:
        messages.error(request, f'Error creating fee: {str(e)}')
    
    return redirect('admin_settings')

@login_required
@require_http_methods(["POST"])
def update_password(request):
    try:
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('admin_settings')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('admin_settings')
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('admin_settings')
        
        request.user.set_password(new_password)
        request.user.save()
        
        messages.success(request, 'Password updated successfully. Please log in again.')
        return redirect('login')
        
    except Exception as e:
        messages.error(request, f'Error updating password: {str(e)}')
        return redirect('admin_settings')