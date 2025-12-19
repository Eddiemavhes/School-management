"""
Views for ZIMSEC Grade 7 Examination Management
"""

from django.views.generic import TemplateView, FormView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Avg, Min, Max
from django.http import JsonResponse
from decimal import Decimal
import json

from core.models.student import Student
from core.models import Class, AcademicTerm, StudentTermHistory
from core.models.zimsec import ZimsecResults, Grade7Statistics
from core.forms.zimsec_forms import ZimsecResultsForm, BulkZimsecEntryForm, ZimsecComparisonForm


class ZimsecResultsEntryView(LoginRequiredMixin, TemplateView):
    """Enter ZIMSEC results for Grade 7 students"""
    template_name = 'zimsec/bulk_entry_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current academic term
        current_term = AcademicTerm.get_current_term()
        current_year = current_term.academic_year if current_term else 2027
        
        # Get all Grade 7 classes
        context['classes'] = Class.objects.filter(grade=7)
        
        # Get all available academic years from StudentTermHistory
        all_years = StudentTermHistory.objects.values_list('academic_year', flat=True).distinct().order_by('-academic_year')
        context['years'] = [str(year) for year in all_years] if all_years.exists() else [str(current_year)]
        context['current_year'] = str(current_year)
        context['form'] = BulkZimsecEntryForm()
        
        return context
    
    def post(self, request):
        """Handle bulk ZIMSEC entry - both selection and saving"""
        
        # Check if this is a save operation
        if request.POST.get('save_results') == 'true':
            return self._handle_save_results(request)
        
        # Otherwise it's a selection request - just need academic year
        academic_year = request.POST.get('academic_year')
        
        if not academic_year:
            return redirect('zimsec_entry')
        
        try:
            academic_year = int(academic_year)
        except ValueError:
            return redirect('zimsec_entry')
        
        # Get all Grade 7 students who reached Term 3 in this year
        # This includes ARCHIVED/ALUMNI students - they still need results entered
        # Use StudentTermHistory to find who reached Term 3 (across all Grade 7 classes)
        student_ids = StudentTermHistory.get_zimsec_candidates(academic_year)
        students = Student.objects.filter(id__in=student_ids).order_by('surname', 'first_name')
        
        # If no term history records exist, fall back to all Grade 7 students
        # (for data migration/backward compatibility)
        if not students.exists():
            # Try by current_class first
            students = Student.objects.filter(
                current_class__grade=7,
                is_deleted=False
            ).order_by('surname', 'first_name')
            
            # If still no students, get ALL Grade 7 students (even deleted/archived)
            if not students.exists():
                students = Student.objects.filter(
                    current_class__grade=7
                ).order_by('surname', 'first_name')
        
        context = {
            'academic_year': academic_year,
            'class_name': 'All Grade 7 Classes',
            'students': list(students.values('id', 'surname', 'first_name')),
            'students_json': json.dumps(list(students.values('id', 'surname', 'first_name'))),
            'classes': Class.objects.filter(grade=7),
            'years': [str(academic_year)],
            'current_year': str(academic_year),
        }
        
        return render(request, 'zimsec/bulk_entry_form.html', context)
    
    def _handle_save_results(self, request):
        """Save all ZIMSEC results from form submission"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            academic_year = int(request.POST.get('academic_year'))
            results_data = json.loads(request.POST.get('results_data', '[]'))
            
            logger.info(f'Saving ZIMSEC results: year={academic_year}, count={len(results_data)}')
            
            if not results_data:
                # messages.error(request, 'No results data provided')
                return redirect('zimsec_entry')
            
            saved_count = 0
            failed_count = 0
            failed_students = []
            
            for result_data in results_data:
                try:
                    student_id = result_data.get('student_id')
                    logger.debug(f'Processing student {student_id}')
                    
                    student = Student.objects.get(id=student_id)
                    
                    # Get or create ZIMSEC result
                    result, created = ZimsecResults.objects.update_or_create(
                        student=student,
                        academic_year=academic_year,
                        defaults={
                            'english_units': result_data.get('english_units'),
                            'mathematics_units': result_data.get('mathematics_units'),
                            'science_units': result_data.get('science_units'),
                            'social_studies_units': result_data.get('social_studies_units'),
                            'indigenous_language_units': result_data.get('indigenous_language_units'),
                            'agriculture_units': result_data.get('agriculture_units'),
                        }
                    )
                    saved_count += 1
                    logger.debug(f'Saved result for student {student_id}')
                except Student.DoesNotExist:
                    failed_count += 1
                    failed_students.append(str(student_id))
                    logger.warning(f'Student {student_id} not found')
                except Exception as e:
                    failed_count += 1
                    failed_students.append(str(student_id))
                    logger.error(f'Error saving student {student_id}: {str(e)}')
            
            # Recalculate statistics for the year
            Grade7Statistics.calculate_for_year(academic_year)
            
            success_msg = f'Successfully saved results for {saved_count} students'
            if failed_count > 0:
                success_msg += f'. {failed_count} students failed: {", ".join(failed_students)}'
            
            # messages.success(request, success_msg)
            logger.info(f'ZIMSEC save complete: {saved_count} saved, {failed_count} failed')
            
        except ValueError as e:
            logger.error(f'ValueError processing results: {str(e)}')
            # messages.error(request, f'Invalid data format: {str(e)}')
        except json.JSONDecodeError as e:
            logger.error(f'JSONDecodeError processing results: {str(e)}')
            # messages.error(request, f'Error parsing results data: {str(e)}')
        except Exception as e:
            logger.error(f'Unexpected error saving results: {str(e)}')
            # messages.error(request, f'Unexpected error: {str(e)}')
        
        return redirect('zimsec_results_list')


class ZimsecResultsBatchSaveAPI(LoginRequiredMixin, TemplateView):
    """API endpoint for saving ZIMSEC results in batches to prevent timeout"""
    
    def post(self, request):
        """Save a batch of ZIMSEC results via AJAX"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            data = json.loads(request.body)
            academic_year = int(data.get('academic_year'))
            results_batch = data.get('results', [])
            batch_number = data.get('batch', 0)
            total_batches = data.get('total_batches', 1)
            
            logger.info(f'Saving ZIMSEC batch {batch_number + 1}/{total_batches}: {len(results_batch)} results')
            
            saved_count = 0
            failed_count = 0
            failed_students = []
            
            # Process this batch of results
            for result_data in results_batch:
                try:
                    student_id = result_data.get('student_id')
                    
                    student = Student.objects.get(id=student_id)
                    
                    # Get or create ZIMSEC result
                    result, created = ZimsecResults.objects.update_or_create(
                        student=student,
                        academic_year=academic_year,
                        defaults={
                            'english_units': result_data.get('english_units'),
                            'mathematics_units': result_data.get('mathematics_units'),
                            'science_units': result_data.get('science_units'),
                            'social_studies_units': result_data.get('social_studies_units'),
                            'indigenous_language_units': result_data.get('indigenous_language_units'),
                            'agriculture_units': result_data.get('agriculture_units'),
                        }
                    )
                    saved_count += 1
                except Student.DoesNotExist:
                    failed_count += 1
                    failed_students.append(str(student_id))
                    logger.warning(f'Student {student_id} not found')
                except Exception as e:
                    failed_count += 1
                    failed_students.append(str(student_id))
                    logger.error(f'Error saving student {student_id}: {str(e)}')
            
            # If this is the last batch, recalculate statistics
            is_final_batch = (batch_number + 1 >= total_batches)
            if is_final_batch:
                Grade7Statistics.calculate_for_year(academic_year)
                logger.info(f'ZIMSEC save complete for year {academic_year}')
            
            return JsonResponse({
                'success': True,
                'saved': saved_count,
                'failed': failed_count,
                'failed_students': failed_students,
                'is_final': is_final_batch,
                'batch': batch_number,
                'total_batches': total_batches,
            })
            
        except Exception as e:
            logger.error(f'Error in batch save: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=400)


class ZimsecResultDetailView(LoginRequiredMixin, DetailView):
    """View and edit individual ZIMSEC result"""
    model = ZimsecResults
    template_name = 'zimsec/result_detail.html'
    context_object_name = 'result'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.get_object()
        
        # Subject performance
        context['subjects'] = [
            {
                'name': 'English Language',
                'units': result.english_units,
                'status': result.english_status
            },
            {
                'name': 'Mathematics',
                'units': result.mathematics_units,
                'status': result.mathematics_status
            },
            {
                'name': 'General Science',
                'units': result.science_units,
                'status': result.science_status
            },
            {
                'name': 'Social Studies',
                'units': result.social_studies_units,
                'status': result.social_studies_status
            },
            {
                'name': 'Indigenous Language',
                'units': result.indigenous_language_units,
                'status': result.language_status
            },
            {
                'name': 'Agriculture',
                'units': result.agriculture_units,
                'status': result.agriculture_status
            },
        ]
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Update ZIMSEC result"""
        result = self.get_object()
        form = ZimsecResultsForm(request.POST, instance=result)
        
        if form.is_valid():
            form.save()
            # Recalculate statistics for this year
            Grade7Statistics.calculate_for_year(result.academic_year)
            # messages.success(request, 'ZIMSEC results updated successfully')
            return redirect('zimsec_result_detail', pk=result.pk)
        
        return self.get(request, *args, **kwargs)


class ZimsecResultEditView(LoginRequiredMixin, DetailView):
    """Edit individual ZIMSEC result"""
    model = ZimsecResults
    template_name = 'zimsec/result_edit.html'
    context_object_name = 'result'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.get_object()
        
        if self.request.POST:
            context['form'] = ZimsecResultsForm(self.request.POST, instance=result)
        else:
            context['form'] = ZimsecResultsForm(instance=result)
        
        # Add student info
        context['student'] = result.student
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle result update"""
        result = self.get_object()
        form = ZimsecResultsForm(request.POST, instance=result)
        
        if form.is_valid():
            form.save()
            # Recalculate statistics for this year
            Grade7Statistics.calculate_for_year(result.academic_year)
            # messages.success(request, 'ZIMSEC result updated successfully')
            return redirect('zimsec_result_detail', pk=result.pk)
        
        # If form is invalid, re-display with errors
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class Grade7StatisticsView(LoginRequiredMixin, TemplateView):
    """ZIMSEC Statistics Dashboard - Display comprehensive statistics and analytics"""
    template_name = 'zimsec/statistics.html'
    
    def calculate_advanced_statistics(self, aggregates):
        """Calculate advanced statistical metrics"""
        import numpy as np
        from scipy import stats as scipy_stats
        
        if not aggregates or len(aggregates) < 2:
            return None
        
        agg_array = np.array(aggregates)
        
        # Central Tendency
        mean = float(np.mean(agg_array))
        median = float(np.median(agg_array))
        
        # Calculate mode (most frequent value)
        from collections import Counter
        mode_counter = Counter(aggregates)
        mode_value = mode_counter.most_common(1)[0][0]
        mode_freq = mode_counter.most_common(1)[0][1]
        
        # Dispersion
        std_dev = float(np.std(agg_array, ddof=1))
        variance = float(np.var(agg_array, ddof=1))
        range_val = int(max(aggregates) - min(aggregates))
        min_val = int(min(aggregates))
        max_val = int(max(aggregates))
        
        # Quartiles and IQR
        q1 = float(np.percentile(agg_array, 25))
        q3 = float(np.percentile(agg_array, 75))
        iqr = float(q3 - q1)
        
        # Percentiles
        percentiles = {
            'p10': float(np.percentile(agg_array, 10)),
            'p25': float(np.percentile(agg_array, 25)),
            'p50': float(np.percentile(agg_array, 50)),
            'p75': float(np.percentile(agg_array, 75)),
            'p90': float(np.percentile(agg_array, 90)),
        }
        
        # Skewness and Kurtosis
        skewness = float(scipy_stats.skew(agg_array))
        
        # Determine distribution shape
        if abs(skewness) < 0.5:
            shape = "Normal distribution"
            shape_icon = "↔️"
        elif skewness > 0.5:
            shape = "Right-skewed"
            shape_icon = "↗️"
        else:
            shape = "Left-skewed"
            shape_icon = "↙️"
        
        # Outlier detection using 1.5×IQR rule
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        outliers = [agg for agg in aggregates if agg < lower_bound or agg > upper_bound]
        
        # Color coding for metrics
        def get_mean_color(val):
            if val <= 15:
                return 'green'
            elif val <= 20:
                return 'orange'
            return 'red'
        
        def get_std_dev_color(val):
            if val <= 5:
                return 'green'
            elif val <= 8:
                return 'orange'
            return 'red'
        
        return {
            'mean': round(mean, 1),
            'median': round(median, 1),
            'mode': mode_value,
            'mode_frequency': mode_freq,
            'std_dev': round(std_dev, 1),
            'variance': round(variance, 2),
            'range': range_val,
            'range_display': f"{min_val} to {max_val}",
            'q1': round(q1, 1),
            'q3': round(q3, 1),
            'iqr': round(iqr, 1),
            'percentiles': {k: round(v, 1) for k, v in percentiles.items()},
            'skewness': round(skewness, 2),
            'distribution_shape': shape,
            'shape_icon': shape_icon,
            'outliers': outliers,
            'outlier_count': len(outliers),
            'lower_bound': round(lower_bound, 1),
            'upper_bound': round(upper_bound, 1),
            'mean_color': get_mean_color(mean),
            'std_dev_color': get_std_dev_color(std_dev),
        }
    
    def apply_filters(self, results, filters):
        """Apply all filters to ZIMSEC results"""
        filtered_results = results
        
        # Gender filter (Student model uses 'sex' field)
        if filters.get('gender') and filters['gender'] != 'all':
            gender = filters['gender'].upper()
            filtered_results = [r for r in filtered_results if r.student.sex and r.student.sex.upper() == gender]
        
        # Class filter (OR logic for multiple classes)
        if filters.get('classes') and 'all' not in filters['classes']:
            class_sections = filters['classes']
            filtered_results = [r for r in filtered_results if r.student.current_class and r.student.current_class.section in class_sections]
        
        # Aggregate range filter
        if filters.get('aggregate_min') is not None or filters.get('aggregate_max') is not None:
            min_agg = float(filters.get('aggregate_min', 0))
            max_agg = float(filters.get('aggregate_max', 50))
            filtered_results = [r for r in filtered_results if r.total_aggregate and min_agg <= r.total_aggregate <= max_agg]
        
        # Pass/Fail status filter
        if filters.get('pass_status') and filters['pass_status'] != 'all':
            status = filters['pass_status'].upper()
            filtered_results = [r for r in filtered_results if r.overall_status == status]
        
        # Subject performance filter
        if filters.get('subject') and filters.get('subject_performance'):
            subject_field = {
                'english': 'english_units',
                'mathematics': 'mathematics_units',
                'science': 'science_units',
                'social_studies': 'social_studies_units',
                'language': 'indigenous_language_units',
                'agriculture': 'agriculture_units',
            }.get(filters['subject'].lower())
            
            if subject_field:
                perf_range = filters['subject_performance']
                
                def match_performance(units):
                    if not units:
                        return False
                    if perf_range == 'distinction':
                        return units <= 2
                    elif perf_range == 'credit':
                        return units == 3
                    elif perf_range == 'pass':
                        return 4 <= units <= 5
                    elif perf_range == 'fail':
                        return units >= 6
                    return True
                
                filtered_results = [r for r in filtered_results if match_performance(getattr(r, subject_field, None))]
        
        # Percentile filter
        if filters.get('percentile'):
            aggregates = [r.total_aggregate for r in filtered_results if r.total_aggregate]
            if aggregates:
                import numpy as np
                p10 = float(np.percentile(aggregates, 10))
                p25 = float(np.percentile(aggregates, 25))
                p75 = float(np.percentile(aggregates, 75))
                p90 = float(np.percentile(aggregates, 90))
                
                percentile = filters['percentile']
                if percentile == 'top10':
                    filtered_results = [r for r in filtered_results if r.total_aggregate and r.total_aggregate <= p10]
                elif percentile == 'top25':
                    filtered_results = [r for r in filtered_results if r.total_aggregate and r.total_aggregate <= p25]
                elif percentile == 'middle50':
                    filtered_results = [r for r in filtered_results if r.total_aggregate and p25 <= r.total_aggregate <= p75]
                elif percentile == 'bottom25':
                    filtered_results = [r for r in filtered_results if r.total_aggregate and r.total_aggregate >= p75]
                elif percentile == 'bottom10':
                    filtered_results = [r for r in filtered_results if r.total_aggregate and r.total_aggregate >= p90]
        
        # Outlier filter
        if filters.get('outlier_filter') and filters['outlier_filter'] != 'all':
            aggregates = [r.total_aggregate for r in filtered_results if r.total_aggregate]
            if aggregates and len(aggregates) > 1:
                import numpy as np
                q1 = float(np.percentile(aggregates, 25))
                q3 = float(np.percentile(aggregates, 75))
                iqr = q3 - q1
                lower_bound = q1 - (1.5 * iqr)
                upper_bound = q3 + (1.5 * iqr)
                
                if filters['outlier_filter'] == 'outliers_only':
                    filtered_results = [r for r in filtered_results if r.total_aggregate and (r.total_aggregate < lower_bound or r.total_aggregate > upper_bound)]
                elif filters['outlier_filter'] == 'non_outliers':
                    filtered_results = [r for r in filtered_results if r.total_aggregate and lower_bound <= r.total_aggregate <= upper_bound]
        
        return filtered_results
    
    def get_active_filters_summary(self, filters):
        """Generate a human-readable summary of active filters"""
        summaries = []
        
        if filters.get('gender') and filters['gender'] != 'all':
            summaries.append(f"Gender: {filters['gender'].title()}")
        
        if filters.get('classes') and 'all' not in filters['classes']:
            classes_str = ', '.join(filters['classes'])
            summaries.append(f"Classes: {classes_str}")
        
        if filters.get('aggregate_min') is not None or filters.get('aggregate_max') is not None:
            min_agg = filters.get('aggregate_min', '0')
            max_agg = filters.get('aggregate_max', '50')
            summaries.append(f"Aggregate: {min_agg}-{max_agg} units")
        
        if filters.get('pass_status') and filters['pass_status'] != 'all':
            summaries.append(f"Status: {filters['pass_status'].title()}")
        
        if filters.get('subject') and filters.get('subject_performance'):
            summaries.append(f"{filters['subject'].title()}: {filters['subject_performance'].title()}")
        
        if filters.get('percentile') and filters['percentile'] != 'all':
            percentile_names = {
                'top10': 'Top 10%',
                'top25': 'Top 25%',
                'middle50': 'Middle 50%',
                'bottom25': 'Bottom 25%',
                'bottom10': 'Bottom 10%',
            }
            summaries.append(f"Percentile: {percentile_names.get(filters['percentile'], filters['percentile'])}")
        
        if filters.get('outlier_filter') and filters['outlier_filter'] != 'all':
            if filters['outlier_filter'] == 'outliers_only':
                summaries.append("Show: Outliers Only")
            elif filters['outlier_filter'] == 'non_outliers':
                summaries.append("Show: Non-Outliers Only")
        
        return summaries
    
    def calculate_year_stats(self, academic_year):
        """Calculate statistics for a given academic year"""
        results = list(ZimsecResults.objects.filter(academic_year=academic_year).select_related('student', 'student__current_class'))
        
        if not results:
            return None
        
        total_students = len(results)
        passed_students = sum(1 for r in results if r.overall_status == 'PASS')
        pass_rate = (passed_students / total_students * 100) if total_students > 0 else 0
        
        # Aggregates
        aggregates = [r.total_aggregate for r in results if r.total_aggregate]
        average_aggregate = sum(aggregates) / len(aggregates) if aggregates else 0
        top_aggregate = min(aggregates) if aggregates else None
        
        # Distinction rate (all subjects 1-2 units)
        distinction_count = sum(1 for r in results if all([
            r.english_units and r.english_units <= 2,
            r.mathematics_units and r.mathematics_units <= 2,
            r.science_units and r.science_units <= 2,
            r.social_studies_units and r.social_studies_units <= 2,
            r.indigenous_language_units and r.indigenous_language_units <= 2,
            r.agriculture_units and r.agriculture_units <= 2,
        ]))
        distinction_rate = (distinction_count / total_students * 100) if total_students > 0 else 0
        
        # Subject averages
        subjects = [
            ('english', 'english_units'),
            ('mathematics', 'mathematics_units'),
            ('science', 'science_units'),
            ('social_studies', 'social_studies_units'),
            ('language', 'indigenous_language_units'),
            ('agriculture', 'agriculture_units'),
        ]
        
        subject_averages = {}
        for subject_key, field_name in subjects:
            units_list = [getattr(r, field_name) for r in results if getattr(r, field_name)]
            avg = sum(units_list) / len(units_list) if units_list else 0
            subject_averages[subject_key] = round(avg, 2)
        
        return {
            'year': academic_year,
            'total_students': total_students,
            'passed_students': passed_students,
            'pass_rate': round(pass_rate, 1),
            'average_aggregate': round(average_aggregate, 1),
            'top_aggregate': top_aggregate,
            'distinction_count': distinction_count,
            'distinction_rate': round(distinction_rate, 1),
            'subject_averages': subject_averages,
        }
    
    def calculate_comparison_data(self, years):
        """Calculate year-over-year comparison data for multiple years"""
        import json
        
        if not years:
            return None
        
        # Get statistics for each year
        year_stats = {}
        for year in sorted(years):
            stats = self.calculate_year_stats(year)
            if stats:
                year_stats[year] = stats
        
        if not year_stats:
            return None
        
        sorted_years = sorted(year_stats.keys())
        comparison_data = {
            'years': sorted_years,
            'year_stats': year_stats,
            'changes': {},
            'trends': {},
            'projections': {}
        }
        
        # Calculate year-over-year changes
        metrics_to_track = ['pass_rate', 'average_aggregate', 'distinction_rate', 'total_students']
        subject_keys = list(year_stats[sorted_years[0]]['subject_averages'].keys())
        
        for i in range(len(sorted_years) - 1):
            current_year = sorted_years[i]
            next_year = sorted_years[i + 1]
            key = f"{current_year}_to_{next_year}"
            
            changes = {}
            for metric in metrics_to_track:
                current_val = year_stats[current_year].get(metric, 0)
                next_val = year_stats[next_year].get(metric, 0)
                absolute_change = next_val - current_val
                percent_change = (absolute_change / current_val * 100) if current_val != 0 else 0
                
                changes[metric] = {
                    'absolute': round(absolute_change, 1),
                    'percent': round(percent_change, 1),
                    'trend': 'improving' if (metric == 'pass_rate' or metric == 'distinction_rate' or metric == 'total_students') and absolute_change > 0 
                                   or (metric == 'average_aggregate') and absolute_change < 0
                              else ('declining' if absolute_change != 0 else 'stable')
                }
            
            # Subject changes
            for subject in subject_keys:
                current_val = year_stats[current_year]['subject_averages'].get(subject, 0)
                next_val = year_stats[next_year]['subject_averages'].get(subject, 0)
                absolute_change = next_val - current_val
                
                if subject not in changes:
                    changes[subject] = {}
                changes[subject]['absolute'] = round(absolute_change, 2)
                changes[subject]['trend'] = 'improving' if absolute_change < 0 else ('declining' if absolute_change > 0 else 'stable')
            
            comparison_data['changes'][key] = changes
        
        # Calculate trends (overall direction)
        for metric in metrics_to_track:
            if metric in ['pass_rate', 'distinction_rate', 'total_students']:
                # Higher is better
                trend_values = [year_stats[year].get(metric, 0) for year in sorted_years]
                trend = 'improving' if trend_values[-1] > trend_values[0] else ('declining' if trend_values[-1] < trend_values[0] else 'stable')
            else:
                # Lower is better (for aggregate)
                trend_values = [year_stats[year].get(metric, 0) for year in sorted_years]
                trend = 'improving' if trend_values[-1] < trend_values[0] else ('declining' if trend_values[-1] > trend_values[0] else 'stable')
            comparison_data['trends'][metric] = trend
        
        # Calculate 2028 projections (linear regression)
        if len(sorted_years) >= 2:
            last_year = sorted_years[-1]
            first_year = sorted_years[0]
            year_range = last_year - first_year
            
            for metric in metrics_to_track:
                first_val = year_stats[first_year].get(metric, 0)
                last_val = year_stats[last_year].get(metric, 0)
                annual_change = (last_val - first_val) / year_range if year_range > 0 else 0
                projected_2028 = last_val + annual_change
                
                comparison_data['projections'][metric] = round(projected_2028, 1)
        
        # Prepare chart data (JSON)
        # Trend line chart
        chart_data = {
            'trend_line': json.dumps({
                'labels': sorted_years + [2028],
                'pass_rate': [year_stats[y]['pass_rate'] for y in sorted_years] + [comparison_data['projections'].get('pass_rate', 0)],
                'avg_aggregate': [year_stats[y]['average_aggregate'] for y in sorted_years] + [comparison_data['projections'].get('average_aggregate', 0)],
                'distinction_rate': [year_stats[y]['distinction_rate'] for y in sorted_years] + [comparison_data['projections'].get('distinction_rate', 0)],
            }),
            'subject_comparison': json.dumps({
                'labels': sorted_years,
                **{subject: [year_stats[y]['subject_averages'].get(subject, 0) for y in sorted_years] for subject in subject_keys}
            }),
            'year_cards': json.dumps({
                y: year_stats[y] for y in sorted_years
            })
        }
        
        comparison_data['chart_data'] = chart_data
        return comparison_data
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get academic year from request
        # Handle empty database case
        available_years_list = list(ZimsecResults.objects.values_list('academic_year', flat=True).distinct().order_by('-academic_year'))
        default_year = available_years_list[0] if available_years_list else 2027
        selected_year = int(self.request.GET.get('year', default_year))
        selected_class = self.request.GET.get('class', 'all')
        
        # Get all available years dynamically
        available_years = ZimsecResults.objects.values_list('academic_year', flat=True).distinct().order_by('-academic_year')
        context['available_years'] = list(available_years) if available_years.exists() else []
        context['available_years_list'] = list(available_years) if available_years.exists() else []
        context['selected_year'] = selected_year
        
        # Get all Grade 7 classes
        all_classes = Class.objects.filter(grade=7).order_by('section')
        context['all_classes'] = all_classes
        context['selected_class'] = selected_class
        
        # Extract filters from request
        filters = {
            'gender': self.request.GET.get('gender', 'all'),
            'classes': self.request.GET.getlist('class[]') or [selected_class] if selected_class != 'all' else ['all'],
            'aggregate_min': self.request.GET.get('aggregate_min'),
            'aggregate_max': self.request.GET.get('aggregate_max'),
            'pass_status': self.request.GET.get('pass_status', 'all'),
            'subject': self.request.GET.get('subject'),
            'subject_performance': self.request.GET.get('subject_performance'),
            'percentile': self.request.GET.get('percentile', 'all'),
            'outlier_filter': self.request.GET.get('outlier_filter', 'all'),
        }
        
        # Get students with ZIMSEC results
        results_query = ZimsecResults.objects.filter(academic_year=selected_year).select_related('student', 'student__current_class')
        results = list(results_query)
        
        # Apply filters
        if any(v and v != 'all' for v in filters.values() if v is not None):
            results = self.apply_filters(results, filters)
            context['active_filters'] = self.get_active_filters_summary(filters)
        else:
            context['active_filters'] = []
        
        total_students = len(results)
        original_total = len(list(results_query))
        
        if total_students == 0:
            context['no_data'] = True
            context['message'] = f"No ZIMSEC results found for {selected_year} with applied filters"
            context['filters'] = filters
            return context
        
        context['filters'] = filters
        context['filter_count'] = len([f for f in filters.values() if f and f != 'all'])
        context['total_students_unfiltered'] = original_total
        context['total_students_filtered'] = total_students
        
        # ============ OVERVIEW STATISTICS ============
        passed_students = sum(1 for r in results if r.overall_status == 'PASS')
        overall_pass_rate = (passed_students / total_students * 100) if total_students > 0 else 0
        
        # Calculate average aggregate
        aggregates = [r.total_aggregate for r in results if r.total_aggregate]
        average_aggregate = sum(aggregates) / len(aggregates) if aggregates else 0
        
        # Find top student (lowest aggregate)
        top_student = None
        min_aggregate = float('inf')
        for r in results:
            if r.total_aggregate and r.total_aggregate < min_aggregate:
                min_aggregate = r.total_aggregate
                top_student = {
                    'name': f"{r.student.surname}, {r.student.first_name}",
                    'aggregate': r.total_aggregate,
                    'class': f"Grade {r.student.current_class.grade} Section {r.student.current_class.section}" if r.student.current_class else 'N/A'
                }
        
        context['overview_stats'] = {
            'total_students': total_students,
            'overall_pass_rate': round(overall_pass_rate, 1),
            'average_aggregate': round(average_aggregate, 1),
            'passed_students': passed_students,
            'failed_students': total_students - passed_students,
            'top_student': top_student,
            'pass_rate_color': 'green' if overall_pass_rate >= 85 else ('orange' if overall_pass_rate >= 70 else 'red'),
            'aggregate_color': 'green' if average_aggregate <= 15 else ('orange' if average_aggregate <= 20 else 'red')
        }
        
        # ============ SUBJECT STATISTICS ============
        subjects = [
            ('English', 'english_units'),
            ('Mathematics', 'mathematics_units'),
            ('Science', 'science_units'),
            ('Social Studies', 'social_studies_units'),
            ('Indigenous Language', 'indigenous_language_units'),
            ('Agriculture', 'agriculture_units'),
        ]
        
        subject_stats = []
        for subject_name, field_name in subjects:
            units_list = [getattr(r, field_name) for r in results if getattr(r, field_name)]
            
            if units_list:
                avg_units = sum(units_list) / len(units_list)
                pass_count = sum(1 for u in units_list if u <= 5)
                pass_rate = (pass_count / len(units_list) * 100) if units_list else 0
                distinction_count = sum(1 for u in units_list if u == 1)
                
                subject_stats.append({
                    'name': subject_name,
                    'field': field_name,
                    'avg_units': round(avg_units, 2),
                    'pass_rate': round(pass_rate, 1),
                    'pass_count': pass_count,
                    'distinction_count': distinction_count,
                    'total_count': len(units_list),
                    'color': 'green' if pass_rate >= 90 else ('orange' if pass_rate >= 75 else 'red')
                })
        
        context['subject_stats'] = subject_stats
        
        # ============ CLASS STATISTICS ============
        class_stats = []
        for cls in all_classes:
            class_results = [r for r in results if r.student.current_class and r.student.current_class.section == cls.section]
            
            if class_results:
                class_passed = sum(1 for r in class_results if r.overall_status == 'PASS')
                class_pass_rate = (class_passed / len(class_results) * 100) if class_results else 0
                
                class_aggregates = [r.total_aggregate for r in class_results if r.total_aggregate]
                class_avg_aggregate = sum(class_aggregates) / len(class_aggregates) if class_aggregates else 0
                
                top_agg = min(class_aggregates) if class_aggregates else None
                bottom_agg = max(class_aggregates) if class_aggregates else None
                
                class_stats.append({
                    'name': f"Grade {cls.grade} Section {cls.section}",
                    'section': cls.section,
                    'student_count': len(class_results),
                    'avg_aggregate': round(class_avg_aggregate, 1),
                    'pass_rate': round(class_pass_rate, 1),
                    'passed_count': class_passed,
                    'failed_count': len(class_results) - class_passed,
                    'top_aggregate': top_agg,
                    'bottom_aggregate': bottom_agg,
                    'color': 'green' if class_pass_rate >= 85 else ('orange' if class_pass_rate >= 70 else 'red')
                })
        
        context['class_stats'] = class_stats
        
        # ============ TOP 10 & BOTTOM 10 STUDENTS ============
        # Sort by aggregate
        sorted_results = sorted(results, key=lambda r: r.total_aggregate if r.total_aggregate else float('inf'))
        
        top_performers = []
        for rank, result in enumerate(sorted_results[:10], 1):
            top_performers.append({
                'rank': rank,
                'name': f"{result.student.surname}, {result.student.first_name}",
                'class': f"Grade {result.student.current_class.grade} Section {result.student.current_class.section}" if result.student.current_class else 'N/A',
                'aggregate': result.total_aggregate,
                'status': result.overall_status,
                'percentage': (result.total_aggregate / 54 * 100) if result.total_aggregate else 0
            })
        
        bottom_performers = []
        for rank, result in enumerate(sorted_results[-10:], total_students - 9):
            bottom_performers.append({
                'rank': rank,
                'name': f"{result.student.surname}, {result.student.first_name}",
                'class': f"Grade {result.student.current_class.grade} Section {result.student.current_class.section}" if result.student.current_class else 'N/A',
                'aggregate': result.total_aggregate,
                'status': result.overall_status,
                'percentage': (result.total_aggregate / 54 * 100) if result.total_aggregate else 0
            })
        
        context['top_performers'] = top_performers
        context['bottom_performers'] = bottom_performers
        
        # ============ CHART DATA (JSON FORMAT) ============
        import json
        
        # Subject performance chart data
        subject_labels = [s['name'] for s in subject_stats]
        subject_passes = [s['pass_count'] for s in subject_stats]
        subject_pass_rates = [s['pass_rate'] for s in subject_stats]
        
        context['subject_pass_json'] = json.dumps({
            'labels': subject_labels,
            'data': subject_pass_rates,
        })
        
        # Pass/Fail distribution
        context['passfail_json'] = json.dumps({
            'labels': ['Passed', 'Failed'],
            'data': [passed_students, total_students - passed_students],
        })
        
        # Class performance data
        class_labels = [cs['section'] for cs in class_stats]
        class_avg_aggregates = [cs['avg_aggregate'] for cs in class_stats]
        class_pass_rates = [cs['pass_rate'] for cs in class_stats]
        
        context['class_comparison_json'] = json.dumps({
            'labels': class_labels,
            'avg_aggregates': class_avg_aggregates,
            'pass_rates': class_pass_rates,
        })
        
        # Aggregate distribution
        aggregate_ranges = [0, 0, 0, 0]
        for agg in aggregates:
            if agg <= 12:
                aggregate_ranges[0] += 1
            elif agg <= 18:
                aggregate_ranges[1] += 1
            elif agg <= 24:
                aggregate_ranges[2] += 1
            else:
                aggregate_ranges[3] += 1
        
        context['aggregate_json'] = json.dumps({
            'labels': ['Excellent (≤12)', 'Good (13-18)', 'Average (19-24)', 'Below Avg (25+)'],
            'data': aggregate_ranges,
        })
        
        # Add distribution flag and JSON for template
        context['distribution'] = True
        context['distribution_json'] = context['aggregate_json']
        
        # ============ YEAR COMPARISON DATA ============
        # Check if comparison mode is enabled
        comparison_mode = self.request.GET.get('comparison_mode', 'off') == 'on'
        selected_years_param = self.request.GET.get('years', '')
        
        context['comparison_mode'] = comparison_mode
        context['available_years_list'] = sorted(list(available_years), reverse=True)
        
        if comparison_mode and selected_years_param:
            # Parse selected years from comma-separated list
            try:
                selected_years = [int(y.strip()) for y in selected_years_param.split(',')]
                comparison_data = self.calculate_comparison_data(selected_years)
                
                if comparison_data:
                    context['comparison_data'] = comparison_data
                    context['comparison_years'] = sorted(selected_years)
                    context['comparison_available'] = True
                    # Include chart data
                    context['trend_line_json'] = comparison_data['chart_data']['trend_line']
                    context['subject_comparison_json'] = comparison_data['chart_data']['subject_comparison']
                    context['year_cards_json'] = comparison_data['chart_data']['year_cards']
            except (ValueError, TypeError):
                pass
        
        # ============ ADVANCED STATISTICS ============
        advanced_stats = self.calculate_advanced_statistics(aggregates)
        context['advanced_stats'] = advanced_stats
        
        return context


class YearComparisonView(LoginRequiredMixin, TemplateView):
    """Compare ZIMSEC results across multiple years with trends and projections"""
    template_name = 'zimsec/year_comparison.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get available years - only those with actual ZIMSEC data
        available_years = sorted(
            set(ZimsecResults.objects.filter(academic_year__isnull=False).values_list('academic_year', flat=True).distinct()),
            reverse=True
        )
        context['available_years_list'] = available_years
        
        # Get years from URL parameters
        years_param = self.request.GET.get('years', '')
        comparison_years = []
        
        if years_param:
            try:
                comparison_years = sorted([int(y.strip()) for y in years_param.split(',') if y.strip()])
            except ValueError:
                comparison_years = []
        else:
            # Default to current academic year only
            current_term = AcademicTerm.get_current_term()
            default_year = current_term.academic_year if current_term else 2026
            if available_years and default_year in available_years:
                comparison_years = [default_year]
            elif available_years:
                comparison_years = [available_years[0]]  # Fallback to most recent year with data
        
        context['comparison_years'] = comparison_years
        context['comparison_available'] = len(comparison_years) > 0
        
        # If we have years selected, calculate comparison data
        if comparison_years:
            try:
                # Create a view instance to call the method
                view_instance = Grade7StatisticsView()
                comparison_data = view_instance.calculate_comparison_data(comparison_years)
                context['comparison_data'] = comparison_data
                
                # Build year cards JSON for JavaScript
                year_cards = {}
                for year in comparison_years:
                    if year in comparison_data['year_stats']:
                        stats = comparison_data['year_stats'][year]
                        year_cards[year] = {
                            'total_students': stats.get('total_students', 0),
                            'pass_rate': f"{stats.get('pass_rate', 0):.1f}",
                            'average_aggregate': f"{stats.get('average_aggregate', 0):.2f}",
                            'distinction_rate': f"{stats.get('distinction_rate', 0):.1f}",
                            'top_aggregate': stats.get('top_aggregate', 'N/A'),
                        }
                
                import json
                context['year_cards_json'] = json.dumps(year_cards)
                
            except Exception as e:
                # messages.error(self.request, f'Error calculating comparison: {str(e)}')
                context['comparison_available'] = False
        
        return context


class ZimsecResultsListView(LoginRequiredMixin, ListView):
    """List all ZIMSEC results for a given year"""
    model = ZimsecResults
    template_name = 'zimsec/results_list.html'
    context_object_name = 'results'
    paginate_by = 50
    
    def get_queryset(self):
        academic_year = self.request.GET.get('year')
        queryset = ZimsecResults.objects.all()
        
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        else:
            # Default to the current academic year
            current_term = AcademicTerm.get_current_term()
            default_year = current_term.academic_year if current_term else 2026
            queryset = queryset.filter(academic_year=default_year)
        
        return queryset.order_by('-total_aggregate')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_years'] = ZimsecResults.objects.values_list('academic_year', flat=True).distinct().order_by('-academic_year')
        # Default to current academic year
        current_term = AcademicTerm.get_current_term()
        default_year = current_term.academic_year if current_term else 2026
        context['selected_year'] = int(self.request.GET.get('year', default_year))
        return context


class ZimsecStatisticsView(LoginRequiredMixin, TemplateView):
    """ZIMSEC Statistics Dashboard - Display comprehensive statistics and analytics"""
    template_name = 'zimsec/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get academic year from request - default to current
        current_term = AcademicTerm.get_current_term()
        default_year = current_term.academic_year if current_term else 2026
        selected_year = int(self.request.GET.get('year', default_year))
        selected_class = self.request.GET.get('class', 'all')
        
        # Get all available years
        available_years = ZimsecResults.objects.values_list('academic_year', flat=True).distinct().order_by('-academic_year')
        context['available_years'] = list(available_years) if available_years.exists() else [2027]
        context['selected_year'] = selected_year
        
        # Get all Grade 7 classes
        all_classes = Class.objects.filter(grade=7).order_by('section')
        context['all_classes'] = all_classes
        context['selected_class'] = selected_class
        
        # Get students with ZIMSEC results
        results_query = ZimsecResults.objects.filter(academic_year=selected_year).select_related('student', 'student__current_class')
        
        if selected_class != 'all':
            results_query = results_query.filter(student__current_class__section=selected_class)
        
        results = list(results_query)
        total_students = len(results)
        
        if total_students == 0:
            context['no_data'] = True
            context['message'] = f"No ZIMSEC results found for {selected_year}"
            return context
        
        # ============ OVERVIEW STATISTICS ============
        passed_students = sum(1 for r in results if r.overall_status == 'PASS')
        overall_pass_rate = (passed_students / total_students * 100) if total_students > 0 else 0
        
        # Calculate average aggregate
        aggregates = [r.total_aggregate for r in results if r.total_aggregate]
        average_aggregate = sum(aggregates) / len(aggregates) if aggregates else 0
        
        # Find top student (lowest aggregate)
        top_student = None
        min_aggregate = float('inf')
        for r in results:
            if r.total_aggregate and r.total_aggregate < min_aggregate:
                min_aggregate = r.total_aggregate
                top_student = {
                    'name': f"{r.student.surname}, {r.student.first_name}",
                    'aggregate': r.total_aggregate,
                    'class': r.student.current_class.name if r.student.current_class else 'N/A'
                }
        
        context['overview_stats'] = {
            'total_students': total_students,
            'overall_pass_rate': round(overall_pass_rate, 1),
            'average_aggregate': round(average_aggregate, 1),
            'passed_students': passed_students,
            'failed_students': total_students - passed_students,
            'top_student': top_student,
            'pass_rate_color': 'green' if overall_pass_rate >= 85 else ('orange' if overall_pass_rate >= 70 else 'red'),
            'aggregate_color': 'green' if average_aggregate <= 15 else ('orange' if average_aggregate <= 20 else 'red')
        }
        
        # ============ SUBJECT STATISTICS ============
        subjects = [
            ('English', 'english_units'),
            ('Mathematics', 'mathematics_units'),
            ('Science', 'science_units'),
            ('Social Studies', 'social_studies_units'),
            ('Indigenous Language', 'indigenous_language_units'),
            ('Agriculture', 'agriculture_units'),
        ]
        
        subject_stats = []
        for subject_name, field_name in subjects:
            units_list = [getattr(r, field_name) for r in results if getattr(r, field_name)]
            
            if units_list:
                avg_units = sum(units_list) / len(units_list)
                pass_count = sum(1 for u in units_list if u <= 5)
                pass_rate = (pass_count / len(units_list) * 100) if units_list else 0
                distinction_count = sum(1 for u in units_list if u == 1)
                
                subject_stats.append({
                    'name': subject_name,
                    'field': field_name,
                    'avg_units': round(avg_units, 2),
                    'pass_rate': round(pass_rate, 1),
                    'pass_count': pass_count,
                    'distinction_count': distinction_count,
                    'total_count': len(units_list),
                    'color': 'green' if pass_rate >= 90 else ('orange' if pass_rate >= 75 else 'red')
                })
        
        context['subject_stats'] = subject_stats
        
        # ============ CLASS STATISTICS ============
        class_stats = []
        for cls in all_classes:
            class_results = [r for r in results if r.student.current_class and r.student.current_class.section == cls.section]
            
            if class_results:
                class_passed = sum(1 for r in class_results if r.overall_status == 'PASS')
                class_pass_rate = (class_passed / len(class_results) * 100) if class_results else 0
                
                class_aggregates = [r.total_aggregate for r in class_results if r.total_aggregate]
                class_avg_aggregate = sum(class_aggregates) / len(class_aggregates) if class_aggregates else 0
                
                top_agg = min(class_aggregates) if class_aggregates else None
                bottom_agg = max(class_aggregates) if class_aggregates else None
                
                class_stats.append({
                    'name': f"Grade {cls.grade} Section {cls.section}",
                    'section': cls.section,
                    'student_count': len(class_results),
                    'avg_aggregate': round(class_avg_aggregate, 1),
                    'pass_rate': round(class_pass_rate, 1),
                    'passed_count': class_passed,
                    'failed_count': len(class_results) - class_passed,
                    'top_aggregate': top_agg,
                    'bottom_aggregate': bottom_agg,
                    'color': 'green' if class_pass_rate >= 85 else ('orange' if class_pass_rate >= 70 else 'red')
                })
        
        context['class_stats'] = class_stats
        
        # ============ TOP 10 & BOTTOM 10 STUDENTS ============
        # Sort by aggregate
        sorted_results = sorted(results, key=lambda r: r.total_aggregate if r.total_aggregate else float('inf'))
        
        top_performers = []
        for rank, result in enumerate(sorted_results[:10], 1):
            top_performers.append({
                'rank': rank,
                'name': f"{result.student.surname}, {result.student.first_name}",
                'class': result.student.current_class.name if result.student.current_class else 'N/A',
                'aggregate': result.total_aggregate,
                'status': result.overall_status,
                'percentage': (result.total_aggregate / 54 * 100) if result.total_aggregate else 0
            })
        
        bottom_performers = []
        for rank, result in enumerate(sorted_results[-10:], total_students - 9):
            bottom_performers.append({
                'rank': rank,
                'name': f"{result.student.surname}, {result.student.first_name}",
                'class': result.student.current_class.name if result.student.current_class else 'N/A',
                'aggregate': result.total_aggregate,
                'status': result.overall_status,
                'percentage': (result.total_aggregate / 54 * 100) if result.total_aggregate else 0
            })
        
        context['top_performers'] = top_performers
        context['bottom_performers'] = bottom_performers
        
        # ============ DISTRIBUTION & CHARTS DATA ============
        # Aggregate distribution (6-12, 13-18, 19-24, 25-30, 31+)
        distribution = {
            '6-12': 0,
            '13-18': 0,
            '19-24': 0,
            '25-30': 0,
            '31+': 0
        }
        
        for result in results:
            if result.total_aggregate:
                agg = result.total_aggregate
                if 6 <= agg <= 12:
                    distribution['6-12'] += 1
                elif 13 <= agg <= 18:
                    distribution['13-18'] += 1
                elif 19 <= agg <= 24:
                    distribution['19-24'] += 1
                elif 25 <= agg <= 30:
                    distribution['25-30'] += 1
                else:
                    distribution['31+'] += 1
        
        context['distribution'] = distribution
        context['distribution_json'] = json.dumps({
            'labels': list(distribution.keys()),
            'data': list(distribution.values())
        })
        
        # Subject pass rates for chart
        subject_pass_data = {s['name']: s['pass_rate'] for s in subject_stats}
        context['subject_pass_json'] = json.dumps({
            'labels': list(subject_pass_data.keys()),
            'data': list(subject_pass_data.values())
        })
        
        # Class comparison data
        class_data = {
            'labels': [c['name'] for c in class_stats],
            'avg_aggregates': [c['avg_aggregate'] for c in class_stats],
            'pass_rates': [c['pass_rate'] for c in class_stats]
        }
        context['class_comparison_json'] = json.dumps(class_data)
        
        # Pass/Fail pie chart
        context['passfail_json'] = json.dumps({
            'labels': ['Passed', 'Failed'],
            'data': [passed_students, total_students - passed_students],
            'colors': ['#28a745', '#dc3545']
        })
        
        return context


class ExportMixin:
    """Mixin to provide export functionality"""
    
    def get_export_data(self, results, year):
        """Get data for exports"""
        from core.services.export_service import generate_statistics_snapshot, generate_subject_statistics
        
        stats = generate_statistics_snapshot(results, year)
        subject_stats = generate_subject_statistics(results)
        
        return {
            'stats': stats,
            'subject_stats': subject_stats,
            'results': results,
            'year': year
        }


class ExportPowerPointView(LoginRequiredMixin, ExportMixin, TemplateView):
    """Export statistics as PowerPoint presentation"""
    
    def get(self, request, *args, **kwargs):
        from core.services.export_service import PowerPointExporter, generate_statistics_snapshot, generate_subject_statistics
        from django.http import FileResponse
        import os
        from tempfile import NamedTemporaryFile
        
        # Get year from request
        year = int(request.GET.get('year', 2027))
        
        # Get results
        results = list(ZimsecResults.objects.filter(academic_year=year).select_related('student', 'student__current_class'))
        
        if not results:
            # messages.error(request, f"No ZIMSEC results found for {year}")
            return redirect('grade7_statistics')
        
        # Generate statistics
        stats = generate_statistics_snapshot(results, year)
        subject_stats = generate_subject_statistics(results)
        
        # Create PowerPoint
        pptx = PowerPointExporter(
            title=f"ZIMSEC {year} Examination Analysis",
            created_by=request.user.full_name or request.user.username
        )
        
        pptx.add_title_slide(school_name="School Name", year=year)
        pptx.add_executive_summary_slide(stats)
        pptx.add_performance_overview_slide(results)
        pptx.add_subject_analysis_slide(subject_stats)
        pptx.add_class_comparison_slide({
            f"Grade 7{cls.section}": {
                'pass_rate': sum(1 for r in results if r.student.current_class == cls and r.overall_status == 'PASS') / max(len([r for r in results if r.student.current_class == cls]), 1) * 100,
                'count': len([r for r in results if r.student.current_class == cls])
            }
            for cls in Class.objects.filter(grade=7)
        })
        pptx.add_recommendations_slide([
            "Focus on Mathematics and Science improvement initiatives",
            "Increase fee payment collection to improve resource allocation",
            "Implement peer tutoring programs for struggling students",
            "Regular performance reviews and intervention planning"
        ])
        
        # Save to temporary file and read into memory
        from io import BytesIO
        file_buffer = BytesIO()
        pptx.save(file_buffer)
        file_buffer.seek(0)
        
        # Serve file from memory
        response = FileResponse(file_buffer, content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
        response['Content-Disposition'] = f'attachment; filename="ZIMSEC_{year}_Report.pptx"'
        return response


class ExportExcelView(LoginRequiredMixin, ExportMixin, TemplateView):
    """Export statistics and data as Excel workbook"""
    
    def get(self, request, *args, **kwargs):
        from core.services.export_service import ExcelExporter, generate_statistics_snapshot, generate_subject_statistics
        from django.http import FileResponse
        from tempfile import NamedTemporaryFile
        
        year = int(request.GET.get('year', 2027))
        
        # Get results
        results = list(ZimsecResults.objects.filter(academic_year=year).select_related('student', 'student__current_class'))
        
        if not results:
            # messages.error(request, f"No ZIMSEC results found for {year}")
            return redirect('grade7_statistics')
        
        # Generate statistics
        stats = generate_statistics_snapshot(results, year)
        subject_stats = generate_subject_statistics(results)
        
        # Create Excel workbook
        exporter = ExcelExporter()
        exporter.add_raw_data_sheet(results)
        exporter.add_statistics_sheet(stats)
        exporter.add_subject_analysis_sheet(subject_stats)
        
        # Save to temporary file
        # Save to memory and serve
        from io import BytesIO
        file_buffer = BytesIO()
        exporter.save(file_buffer)
        file_buffer.seek(0)
        
        # Serve file from memory
        response = FileResponse(file_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="ZIMSEC_{year}_Data.xlsx"'
        return response


class ExportPDFView(LoginRequiredMixin, ExportMixin, TemplateView):
    """Export statistics as PDF report"""
    
    def get(self, request, *args, **kwargs):
        from core.services.export_service import PDFExporter, generate_statistics_snapshot
        from core.models.school_details import SchoolDetails
        from django.http import FileResponse
        from tempfile import NamedTemporaryFile
        
        year = int(request.GET.get('year', 2027))
        
        # Get results
        results = list(ZimsecResults.objects.filter(academic_year=year).select_related('student', 'student__current_class'))
        
        if not results:
            # messages.error(request, f"No ZIMSEC results found for {year}")
            return redirect('grade7_statistics')
        
        # Generate statistics
        stats = generate_statistics_snapshot(results, year)
        
        # Get school details
        school = SchoolDetails.get_or_create_default()
        school_name = school.school_name
        
        # Create PDF
        pdf_exporter = PDFExporter(
            title=f"ZIMSEC {year} Examination Report",
            school_name=school_name
        )
        
        content_data = {
            'summary': [
                f"This report provides a comprehensive analysis of ZIMSEC examination results for {year}.",
                f"A total of {stats['total_students']} students were examined across all Grade 7 classes.",
                f"The overall pass rate achieved was {stats['pass_rate']:.1f}%, with an average aggregate of {stats['avg_aggregate']:.1f}.",
            ],
            'pass_rate': stats['pass_rate'],
            'avg_aggregate': stats['avg_aggregate'],
            'distinction_rate': stats['distinction_rate'],
            'total_students': stats['total_students'],
        }
        
        # Save to temporary file
        # Generate PDF to BytesIO
        from io import BytesIO
        file_buffer = BytesIO()
        pdf_exporter.generate_report_to_buffer(file_buffer, content_data)
        file_buffer.seek(0)
        
        # Serve file from memory
        response = FileResponse(file_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ZIMSEC_{year}_Report.pdf"'
        return response


class ExportDetailedResultsView(LoginRequiredMixin, ExportMixin, TemplateView):
    """Export detailed ZIMSEC results by class and student"""
    
    def get(self, request, *args, **kwargs):
        from core.services.export_service import DetailedResultsPDFExporter
        from core.models.school_details import SchoolDetails
        from django.http import FileResponse
        from io import BytesIO
        from django.db.models import Prefetch
        
        year = int(request.GET.get('year', 2027))
        
        # Get results with related student and class data
        results = list(ZimsecResults.objects.filter(
            academic_year=year
        ).select_related('student', 'student__current_class'))
        
        if not results:
            messages.error(request, f"No ZIMSEC results found for {year}")
            return redirect('grade7_statistics')
        
        # Group results by class
        results_by_class = {}
        for result in results:
            # Use str() on the class object which calls __str__ method: "Grade X[A|B]"
            class_name = str(result.student.current_class) if result.student.current_class else "Unassigned"
            if class_name not in results_by_class:
                results_by_class[class_name] = []
            results_by_class[class_name].append(result)
        
        # Get school details
        school = SchoolDetails.get_or_create_default()
        school_name = school.school_name
        
        # Create PDF
        pdf_exporter = DetailedResultsPDFExporter(
            title=f"ZIMSEC {year} Detailed Results",
            school_name=school_name
        )
        
        # Generate PDF to BytesIO
        file_buffer = BytesIO()
        pdf_exporter.export_to_buffer(file_buffer, results_by_class)
        file_buffer.seek(0)
        
        # Serve file from memory
        response = FileResponse(file_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ZIMSEC_{year}_Detailed_Results.pdf"'
        return response


class ExportGrade7CompletionView(LoginRequiredMixin, ExportMixin, TemplateView):
    """Export Grade 7 Completion Report"""
    
    def get(self, request, *args, **kwargs):
        from core.services.grade7_exporter import Grade7CompletionPDFExporter
        from core.models.school_details import SchoolDetails
        from django.http import FileResponse
        from io import BytesIO
        from core.models import ZimsecResults
        
        # Get all students with ZIMSEC results (completed Grade 7)
        students_with_results = ZimsecResults.objects.values_list('student_id', flat=True).distinct()
        students = Student.objects.filter(
            id__in=students_with_results
        ).select_related('current_class').order_by('surname', 'first_name')
        
        if not students.exists():
            messages.error(request, "No students with ZIMSEC results found in the system")
            return redirect('grade7_statistics')
        
        # Group students by class (use their class when they had results, or current class)
        students_by_class = {}
        for student in students:
            # Try to get the class from their first ZIMSEC result, fall back to current class
            try:
                result = student.zimsec_results.first()
                class_name = result.class_name if hasattr(result, 'class_name') and result.class_name else str(student.current_class) if student.current_class else "Grade 7 (2026)"
            except:
                class_name = str(student.current_class) if student.current_class else "Grade 7 (2026)"
            
            if class_name not in students_by_class:
                students_by_class[class_name] = []
            students_by_class[class_name].append(student)
        
        # Get school details
        school = SchoolDetails.get_or_create_default()
        school_name = school.school_name
        
        # Create PDF
        pdf_exporter = Grade7CompletionPDFExporter(school_name=school_name)
        
        # Generate PDF to BytesIO
        file_buffer = pdf_exporter.export_to_buffer(students_by_class)
        
        # Serve file from memory
        response = FileResponse(file_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Grade7_Completion_Report.pdf"'
        return response


class ExportHTMLView(LoginRequiredMixin, ExportMixin, TemplateView):
    """Export interactive HTML dashboard"""
    
    def get(self, request, *args, **kwargs):
        from core.services.export_service import HTMLDashboardExporter, generate_statistics_snapshot
        from django.http import FileResponse
        from tempfile import NamedTemporaryFile
        
        year = int(request.GET.get('year', 2027))
        
        # Get results
        results = list(ZimsecResults.objects.filter(academic_year=year).select_related('student', 'student__current_class'))
        
        if not results:
            # messages.error(request, f"No ZIMSEC results found for {year}")
            return redirect('grade7_statistics')
        
        # Generate statistics
        stats = generate_statistics_snapshot(results, year)
        
        # Create HTML dashboard
        html_exporter = HTMLDashboardExporter(title=f"ZIMSEC {year} Interactive Dashboard")
        
        dashboard_data = {
            'statistics': stats,
            'generated_at': stats.get('generated_at'),
        }
        
        # Save to temporary file
        # Generate HTML and serve
        from io import BytesIO
        from tempfile import NamedTemporaryFile
        import os
        
        # Create temporary file for HTML generation (since html_exporter needs a path)
        with NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as tmp:
            tmp_path = tmp.name
        
        html_exporter.generate_dashboard(tmp_path, dashboard_data)
        
        # Read file content and delete temp file
        with open(tmp_path, 'rb') as f:
            file_buffer = BytesIO(f.read())
        os.unlink(tmp_path)
        
        file_buffer.seek(0)
        # Serve file from memory
        response = FileResponse(file_buffer, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="ZIMSEC_{year}_Dashboard.html"'
        return response
