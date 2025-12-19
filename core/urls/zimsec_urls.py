"""
ZIMSEC Grade 7 Examination Management URLs
"""

from django.urls import path
from core.views.zimsec_views import (
    ZimsecResultsEntryView,
    ZimsecResultDetailView,
    ZimsecResultEditView,
    Grade7StatisticsView,
    YearComparisonView,
    ZimsecResultsListView,
    ZimsecResultsBatchSaveAPI,
)

urlpatterns = [
    # ZIMSEC Results Entry
    path('zimsec/entry/', ZimsecResultsEntryView.as_view(), name='zimsec_entry'),
    path('zimsec/result/<int:pk>/', ZimsecResultDetailView.as_view(), name='zimsec_result_detail'),
    path('zimsec/result/<int:pk>/edit/', ZimsecResultEditView.as_view(), name='zimsec_result_edit'),
    path('zimsec/results/', ZimsecResultsListView.as_view(), name='zimsec_results_list'),
    
    # ZIMSEC API Endpoints
    path('api/zimsec/batch-save/', ZimsecResultsBatchSaveAPI.as_view(), name='zimsec_batch_save'),
    
    # ZIMSEC Statistics and Reports
    path('zimsec/statistics/', Grade7StatisticsView.as_view(), name='grade7_statistics'),
    path('zimsec/comparison/', YearComparisonView.as_view(), name='year_comparison'),
]
