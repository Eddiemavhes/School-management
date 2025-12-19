"""
Advanced analytical tools and comparison features
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages

# Try to import scipy and numpy, but make them optional
try:
    from scipy import stats as scipy_stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    scipy_stats = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

from core.models.zimsec import ZimsecResults
from core.models import Class
import json


class ComparisonView(LoginRequiredMixin, TemplateView):
    """Advanced comparison mode for ZIMSEC data"""
    template_name = 'zimsec/comparison_advanced.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check if scipy is available before processing"""
        if not SCIPY_AVAILABLE or not NUMPY_AVAILABLE:
            messages.error(request, "Advanced analytics not available. Please contact administrator.")
            return redirect('admin_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        year = int(self.request.GET.get('year', 2027))
        comparison_type = self.request.GET.get('type', 'year')  # year, class, subject, gender
        
        context['year'] = year
        context['comparison_type'] = comparison_type
        context['comparison_types'] = [
            ('year', 'Year-over-Year'),
            ('class', 'Class vs Class'),
            ('subject', 'Subject vs Subject'),
            ('gender', 'Gender Comparison'),
        ]
        
        # Get comparison data based on type
        results_current = list(ZimsecResults.objects.filter(academic_year=year).select_related('student', 'student__current_class'))
        
        if comparison_type == 'class':
            context['comparison_data'] = self._get_class_comparison(results_current)
        elif comparison_type == 'subject':
            context['comparison_data'] = self._get_subject_comparison(results_current)
        elif comparison_type == 'gender':
            context['comparison_data'] = self._get_gender_comparison(results_current)
        else:  # year
            results_previous = list(ZimsecResults.objects.filter(academic_year=year-1).select_related('student', 'student__current_class'))
            context['comparison_data'] = self._get_year_comparison(results_current, results_previous, year)
        
        return context
    
    def _get_year_comparison(self, current, previous, year):
        """Compare current year with previous year"""
        def calc_stats(results):
            if not results:
                return {}
            passed = sum(1 for r in results if r.overall_status == 'PASS')
            aggregates = [r.total_aggregate for r in results if r.total_aggregate]
            return {
                'total': len(results),
                'pass_rate': passed / len(results) * 100 if results else 0,
                'passed': passed,
                'failed': len(results) - passed,
                'avg_aggregate': sum(aggregates) / len(aggregates) if aggregates else 0,
            }
        
        current_stats = calc_stats(current)
        previous_stats = calc_stats(previous)
        
        # Statistical significance
        if current and previous:
            t_stat, p_value = scipy_stats.ttest_ind(
                [r.total_aggregate for r in current if r.total_aggregate],
                [r.total_aggregate for r in previous if r.total_aggregate],
                equal_var=False
            )
        else:
            t_stat, p_value = 0, 1.0
        
        return {
            'type': 'year',
            f'year_{year}': current_stats,
            f'year_{year-1}': previous_stats,
            'statistical_test': {
                'test_name': 't-test',
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'interpretation': 'Statistically significant difference' if p_value < 0.05 else 'No significant difference',
                'effect_size': self._calculate_cohens_d(current, previous),
            }
        }
    
    def _get_class_comparison(self, results):
        """Compare classes side-by-side"""
        classes = Class.objects.filter(grade=7)
        class_stats = {}
        
        for cls in classes:
            class_results = [r for r in results if r.student.current_class == cls]
            if class_results:
                passed = sum(1 for r in class_results if r.overall_status == 'PASS')
                aggregates = [r.total_aggregate for r in class_results if r.total_aggregate]
                
                class_stats[f'Grade 7{cls.section}'] = {
                    'total': len(class_results),
                    'pass_rate': passed / len(class_results) * 100,
                    'passed': passed,
                    'failed': len(class_results) - passed,
                    'avg_aggregate': sum(aggregates) / len(aggregates) if aggregates else 0,
                    'distinction_count': sum(1 for r in class_results if r.total_aggregate and r.total_aggregate <= 13),
                }
        
        # ANOVA test for significance
        class_lists = [
            [r.total_aggregate for r in results if r.student.current_class == cls and r.total_aggregate]
            for cls in classes
        ]
        class_lists = [c for c in class_lists if len(c) > 0]
        
        if len(class_lists) > 1:
            f_stat, p_value = scipy_stats.f_oneway(*class_lists)
        else:
            f_stat, p_value = 0, 1.0
        
        return {
            'type': 'class',
            'classes': class_stats,
            'statistical_test': {
                'test_name': 'ANOVA',
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'interpretation': 'Significant difference between classes' if p_value < 0.05 else 'No significant difference between classes',
            }
        }
    
    def _get_subject_comparison(self, results):
        """Compare subjects side-by-side"""
        subjects = {
            'English': 'english_units',
            'Mathematics': 'mathematics_units',
            'Science': 'science_units',
            'Social Studies': 'social_studies_units',
            'Indigenous Language': 'indigenous_language_units',
        }
        
        subject_stats = {}
        subject_lists = []
        
        for subject_name, field_name in subjects.items():
            values = [getattr(r, field_name) for r in results if getattr(r, field_name) is not None]
            
            if values:
                passed = sum(1 for v in values if v >= 4)
                subject_stats[subject_name] = {
                    'avg_units': sum(values) / len(values),
                    'pass_rate': passed / len(values) * 100,
                    'distinction_rate': sum(1 for v in values if v >= 8) / len(values) * 100,
                    'credit_rate': sum(1 for v in values if 6 <= v < 8) / len(values) * 100,
                    'count': len(values),
                }
                subject_lists.append(values)
        
        # Chi-square test for pass rates
        if len(subject_lists) > 1:
            chi2, p_value, dof, expected = scipy_stats.chi2_contingency(
                [[sum(1 for v in s if v >= 4), sum(1 for v in s if v < 4)] for s in subject_lists]
            )
        else:
            chi2, p_value, dof, expected = 0, 1.0, 0, None
        
        return {
            'type': 'subject',
            'subjects': subject_stats,
            'statistical_test': {
                'test_name': 'Chi-Square',
                'chi_statistic': float(chi2),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'interpretation': 'Subjects show significant performance differences' if p_value < 0.05 else 'Subjects show similar performance',
            }
        }
    
    def _get_gender_comparison(self, results):
        """Compare male vs female students"""
        male_results = [r for r in results if r.student.sex == 'M']
        female_results = [r for r in results if r.student.sex == 'F']
        
        def get_gender_stats(gender_results):
            if not gender_results:
                return {}
            passed = sum(1 for r in gender_results if r.overall_status == 'PASS')
            aggregates = [r.total_aggregate for r in gender_results if r.total_aggregate]
            return {
                'total': len(gender_results),
                'pass_rate': passed / len(gender_results) * 100 if gender_results else 0,
                'passed': passed,
                'failed': len(gender_results) - passed,
                'avg_aggregate': sum(aggregates) / len(aggregates) if aggregates else 0,
                'distinction_count': sum(1 for r in gender_results if r.total_aggregate and r.total_aggregate <= 13),
            }
        
        male_stats = get_gender_stats(male_results)
        female_stats = get_gender_stats(female_results)
        
        # T-test
        male_aggs = [r.total_aggregate for r in male_results if r.total_aggregate]
        female_aggs = [r.total_aggregate for r in female_results if r.total_aggregate]
        
        if male_aggs and female_aggs:
            t_stat, p_value = scipy_stats.ttest_ind(male_aggs, female_aggs, equal_var=False)
        else:
            t_stat, p_value = 0, 1.0
        
        return {
            'type': 'gender',
            'Male': male_stats,
            'Female': female_stats,
            'statistical_test': {
                'test_name': 't-test',
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'interpretation': 'Significant gender performance difference' if p_value < 0.05 else 'No significant gender difference',
                'effect_size': self._calculate_cohens_d_for_groups(male_aggs, female_aggs),
            }
        }
    
    def _calculate_cohens_d(self, group1, group2):
        """Calculate Cohen's d effect size"""
        agg1 = [r.total_aggregate for r in group1 if r.total_aggregate]
        agg2 = [r.total_aggregate for r in group2 if r.total_aggregate]
        
        if not agg1 or not agg2:
            return 0
        
        return self._calculate_cohens_d_for_groups(agg1, agg2)
    
    def _calculate_cohens_d_for_groups(self, group1, group2):
        """Calculate Cohen's d for two groups"""
        if not group1 or not group2:
            return 0
        
        mean1 = np.mean(group1)
        mean2 = np.mean(group2)
        std1 = np.std(group1, ddof=1)
        std2 = np.std(group2, ddof=1)
        n1, n2 = len(group1), len(group2)
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0
        
        cohens_d = (mean1 - mean2) / pooled_std
        return round(float(cohens_d), 3)


class PredictionView(LoginRequiredMixin, TemplateView):
    """Predictive forecasting for 2028 and beyond"""
    template_name = 'zimsec/predictions.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check if scipy is available before processing"""
        if not SCIPY_AVAILABLE or not NUMPY_AVAILABLE:
            messages.error(request, "Advanced analytics not available. Please contact administrator.")
            return redirect('admin_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current academic year
        from core.models.academic import AcademicTerm
        current_term = AcademicTerm.get_current_term()
        current_year = current_term.academic_year if current_term else 2026
        
        # Get historical data - only for years that have actual ZIMSEC results
        all_years = sorted(set(ZimsecResults.objects.filter(academic_year__isnull=False).values_list('academic_year', flat=True).distinct()))
        
        
        # If we have less than 2 years, we can't do meaningful predictions
        if len(all_years) < 1:
            # No data at all
            context['predictions'] = {
                'pass_rate_2025': 0,
                'pass_rate_2026': 0,
                'pass_rate_2027': 0,
                'pass_rate_2028': 0,
                'pass_rate_2028_range': "0% - 0%",
                'pass_rate_trend': {
                    'change_2025_2026': 0,
                    'change_2026_2027': 0,
                    'change_2027_2028': 0,
                },
                'agg_2025': 0,
                'agg_2026': 0,
                'agg_2027': 0,
                'agg_2028': 0,
                'agg_2028_range': "0 - 0",
            }
            return context
        
        # Get results for actual years
        historical_results = {}
        for year in all_years:
            historical_results[year] = list(ZimsecResults.objects.filter(academic_year=year))
        
        def get_pass_rate(results):
            if not results:
                return 0
            return sum(1 for r in results if r.overall_status == 'PASS') / len(results) * 100
        
        def get_avg_agg(results):
            if not results:
                return 0
            aggs = [r.total_aggregate for r in results if r.total_aggregate]
            return sum(aggs) / len(aggs) if aggs else 0
        
        # Get pass rates and averages for all historical years
        pass_rates_dict = {year: get_pass_rate(historical_results[year]) for year in all_years}
        avg_aggs_dict = {year: get_avg_agg(historical_results[year]) for year in all_years}
        
        # For display, show 2025, 2026, 2027 (use 0 if not available)
        pass_rate_2025 = pass_rates_dict.get(2025, 0)
        pass_rate_2026 = pass_rates_dict.get(2026, 0)
        pass_rate_2027 = pass_rates_dict.get(2027, 0)
        
        agg_2025 = avg_aggs_dict.get(2025, 0)
        agg_2026 = avg_aggs_dict.get(2026, 0)
        agg_2027 = avg_aggs_dict.get(2027, 0)
        
        pass_rates = [pass_rate_2025, pass_rate_2026, pass_rate_2027]
        avg_aggs = [agg_2025, agg_2026, agg_2027]
        
        # Linear regression prediction - use only actual years with data
        years_with_data = np.array(all_years)
        pass_rates_with_data = np.array([pass_rates_dict[year] for year in all_years])
        avg_aggs_with_data = np.array([avg_aggs_dict[year] for year in all_years])
        
        # Predict next year (current_year + 1)
        projection_year = current_year + 1
        
        # Linear regression prediction for next year
        if len(years_with_data) >= 2:
            z_pass = np.polyfit(years_with_data, pass_rates_with_data, 1)
            p_pass = np.poly1d(z_pass)
            pred_pass = float(p_pass(projection_year))
        else:
            pred_pass = pass_rates_with_data[-1] if len(pass_rates_with_data) > 0 else 0
        
        if len(years_with_data) >= 2:
            z_agg = np.polyfit(years_with_data, avg_aggs_with_data, 1)
            p_agg = np.poly1d(z_agg)
            pred_agg = float(p_agg(projection_year))
        else:
            pred_agg = avg_aggs_with_data[-1] if len(avg_aggs_with_data) > 0 else 0
        
        # Confidence intervals (simplified)
        pred_pass_lower = max(0, pred_pass - 5)
        pred_pass_upper = min(100, pred_pass + 5)
        
        pred_agg_lower = max(0, pred_agg - 0.5)
        pred_agg_upper = min(50, pred_agg + 0.5)
        
        # Build year cards only for years with actual data
        year_cards = []
        for year in all_years:
            year_cards.append({
                'year': year,
                'pass_rate': round(pass_rates_dict[year], 1),
                'avg_agg': round(avg_aggs_dict[year], 2),
            })
        
        # Build trend analysis ONLY for consecutive years with actual data
        trend_lines = []
        if len(all_years) >= 2:
            # We have multiple years - show trends between them
            for i in range(len(all_years) - 1):
                year1 = all_years[i]
                year2 = all_years[i + 1]
                pass_change = pass_rates_dict[year2] - pass_rates_dict[year1]
                agg_change = avg_aggs_dict[year2] - avg_aggs_dict[year1]
                trend_lines.append({
                    'label': f"{year1}→{year2}",
                    'pass_change': round(pass_change, 1),
                    'agg_change': round(agg_change, 2),
                })
            # Add projection for next year
            if len(all_years) > 0:
                last_year = all_years[-1]
                pass_change_proj = pred_pass - pass_rates_dict[last_year]
                agg_change_proj = pred_agg - avg_aggs_dict[last_year]
                trend_lines.append({
                    'label': f"Projected {last_year}→{projection_year}",
                    'pass_change': round(pass_change_proj, 1),
                    'agg_change': round(agg_change_proj, 2),
                })
        elif len(all_years) == 1:
            # Only one year of data - show projection only
            year1 = all_years[0]
            pass_change_proj = pred_pass - pass_rates_dict[year1]
            agg_change_proj = pred_agg - avg_aggs_dict[year1]
            trend_lines.append({
                'label': f"Projected {year1}→{projection_year}",
                'pass_change': round(pass_change_proj, 1),
                'agg_change': round(agg_change_proj, 2),
            })
        
        context['predictions'] = {
            'pass_rate_2025': round(pass_rate_2025, 1),
            'pass_rate_2026': round(pass_rate_2026, 1),
            'pass_rate_2027': round(pass_rate_2027, 1),
            'pass_rate_projection': round(pred_pass, 1),
            'pass_rate_projection_range': f"{round(pred_pass_lower, 1)}% - {round(pred_pass_upper, 1)}%",
            'pass_rate_trend_lines': trend_lines,
            
            'agg_2025': round(agg_2025, 2),
            'agg_2026': round(agg_2026, 2),
            'agg_2027': round(agg_2027, 2),
            'agg_projection': round(pred_agg, 2),
            'agg_projection_range': f"{round(pred_agg_lower, 2)} - {round(pred_agg_upper, 2)}",
            'year_cards': year_cards,
        }
        context['available_years'] = all_years
        context['projection_year'] = projection_year
        context['current_year'] = current_year
        
        return context


class StatisticalTestsView(LoginRequiredMixin, TemplateView):
    """Perform statistical tests on ZIMSEC data"""
    template_name = 'zimsec/statistical_tests.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check if scipy is available before processing"""
        if not SCIPY_AVAILABLE or not NUMPY_AVAILABLE:
            messages.error(request, "Advanced analytics not available. Please contact administrator.")
            return redirect('admin_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Handle statistical test requests"""
        try:
            test_type = request.POST.get('test_type', 'ttest')
            year = int(request.POST.get('year', 2027))
            
            results = list(ZimsecResults.objects.filter(academic_year=year).select_related('student'))
            
            if test_type == 'ttest':
                return self._perform_ttest(request, results)
            elif test_type == 'anova':
                return self._perform_anova(request, results)
            elif test_type == 'chi_square':
                return self._perform_chi_square(request, results)
            elif test_type == 'correlation':
                return self._perform_correlation(request, results)
            else:
                return JsonResponse({'error': f'Unknown test type: {test_type}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _perform_ttest(self, request, results):
        """Perform independent samples t-test"""
        group1_type = request.POST.get('group1', 'gender_M')
        group2_type = request.POST.get('group2', 'gender_F')
        metric = request.POST.get('metric', 'aggregate')
        
        group1 = self._get_group_data(results, group1_type, metric)
        group2 = self._get_group_data(results, group2_type, metric)
        
        if not group1 or not group2:
            return JsonResponse({'error': 'Insufficient data for comparison'}, status=400)
        
        t_stat, p_value = scipy_stats.ttest_ind(group1, group2, equal_var=False)
        cohens_d = self._calculate_cohens_d_for_groups(group1, group2)
        
        return JsonResponse({
            'test_name': 'Independent Samples t-test',
            'test_statistic': round(float(t_stat), 4),
            'p_value': round(float(p_value), 4),
            'significant': bool(p_value < 0.05),
            'group1_mean': round(np.mean(group1), 2),
            'group2_mean': round(np.mean(group2), 2),
            'cohens_d': cohens_d,
            'interpretation': f"Mean difference: {round(np.mean(group1) - np.mean(group2), 2)}"
        })
    
    def _perform_anova(self, request, results):
        """Perform ANOVA test"""
        metric = request.POST.get('metric', 'aggregate')
        
        classes = Class.objects.filter(grade=7)
        groups = []
        
        for cls in classes:
            class_data = self._get_class_data(results, cls, metric)
            if class_data:
                groups.append(class_data)
        
        if len(groups) < 2:
            return JsonResponse({'error': 'Insufficient groups for ANOVA'}, status=400)
        
        f_stat, p_value = scipy_stats.f_oneway(*groups)
        
        return JsonResponse({
            'test_name': 'One-Way ANOVA',
            'test_statistic': round(float(f_stat), 4),
            'p_value': round(float(p_value), 4),
            'significant': bool(p_value < 0.05),
            'groups_compared': len(groups),
            'interpretation': 'Significant differences between groups' if p_value < 0.05 else 'No significant differences between groups'
        })
    
    def _get_group_data(self, results, group_type, metric):
        """Get data for a specific group"""
        if group_type.startswith('gender_'):
            gender = group_type.split('_')[1]
            group_results = [r for r in results if r.student.sex == gender]
        else:
            group_results = results
        
        if metric == 'aggregate':
            return [r.total_aggregate for r in group_results if r.total_aggregate]
        elif metric == 'pass_status':
            return [1 if r.overall_status == 'PASS' else 0 for r in group_results]
        else:
            return []
    
    def _get_class_data(self, results, cls, metric):
        """Get data for a specific class"""
        class_results = [r for r in results if r.student.current_class == cls]
        
        if metric == 'aggregate':
            return [r.total_aggregate for r in class_results if r.total_aggregate]
        else:
            return []
    
    def _calculate_cohens_d_for_groups(self, group1, group2):
        """Calculate Cohen's d for two groups"""
        if not group1 or not group2:
            return 0
        
        mean1 = np.mean(group1)
        mean2 = np.mean(group2)
        std1 = np.std(group1, ddof=1)
        std2 = np.std(group2, ddof=1)
        n1, n2 = len(group1), len(group2)
        
        pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0
        
        cohens_d = (mean1 - mean2) / pooled_std
        return round(float(cohens_d), 3)

    def _perform_correlation(self, request, results):
        """Perform correlation analysis"""
        if len(results) < 3:
            return JsonResponse({'error': 'Insufficient data for correlation analysis'}, status=400)
        
        # Get aggregate and distinction rate data
        aggregates = [r.total_aggregate for r in results if r.total_aggregate]
        
        if len(aggregates) < 3:
            return JsonResponse({'error': 'Insufficient aggregate data for correlation'}, status=400)
        
        # Simple correlation: pass rate vs aggregate
        pass_status = [1 if r.overall_status == 'PASS' else 0 for r in results if r.total_aggregate]
        
        # Pearson correlation
        correlation, p_value = scipy_stats.pearsonr(aggregates, pass_status)
        
        return JsonResponse({
            'test_name': 'Pearson Correlation',
            'test_statistic': round(float(correlation), 4),
            'p_value': round(float(p_value), 4),
            'significant': bool(p_value < 0.05),
            'interpretation': 'Strong positive correlation between aggregate and pass status' if correlation > 0.7 else 'Moderate to weak correlation'
        })

    def _perform_chi_square(self, request, results):
        """Perform chi-square test for independence"""
        if len(results) < 4:
            return JsonResponse({'error': 'Insufficient data for chi-square test'}, status=400)
        
        # Create contingency table: Gender vs Pass/Fail status
        from pandas import crosstab
        
        data = []
        for r in results:
            if r.student:
                data.append({
                    'gender': r.student.sex,
                    'status': r.overall_status
                })
        
        if len(data) < 4:
            return JsonResponse({'error': 'Insufficient data for chi-square test'}, status=400)
        
        import pandas as pd
        df = pd.DataFrame(data)
        contingency = crosstab(df['gender'], df['status'])
        
        # Perform chi-square test
        chi2, p_value, dof, expected = scipy_stats.chi2_contingency(contingency)
        
        return JsonResponse({
            'test_name': 'Chi-Square Test of Independence',
            'test_statistic': round(float(chi2), 4),
            'p_value': round(float(p_value), 4),
            'significant': bool(p_value < 0.05),
            'interpretation': 'Significant association between gender and pass status' if p_value < 0.05 else 'No significant association between gender and pass status'
        })
