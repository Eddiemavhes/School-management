#!/usr/bin/env python
"""
Django Management Command: Process Alumni Batch

Usage: python manage.py process_alumni_batch

This command:
1. Runs daily via cron or Celery
2. Finds all eligible alumni (Grade 7, Term 3, balance <= 0)
3. Converts any that were missed to ALUMNI status
4. Fixes any incorrectly configured alumni records
5. Logs all changes for audit trail

This is a safety net to catch:
- Manual updates that bypass signals
- Database errors during conversion
- Payment processing issues
- Race conditions in signal handling
"""

from django.core.management.base import BaseCommand
from core.services.alumni_conversion import AlumniConversionService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process Grade 7 students to alumni status - runs daily to catch any missed conversions'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Alumni Batch Processing...\n')
        )
        
        # Run batch processing
        results = AlumniConversionService.batch_process_alumni_candidates()
        
        # Display results
        self.stdout.write(
            f'\nProcessed: {results["processed"]} Grade 7 students'
        )
        self.stdout.write(
            f'Converted: {results["converted"]} to Alumni status'
        )
        
        if results['errors']:
            self.stdout.write(
                self.style.WARNING(f'\nErrors encountered ({len(results["errors"])}):')
            )
            for error in results['errors']:
                self.stdout.write(
                    self.style.ERROR(f'  - {error}')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nNo errors encountered')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\nAlumni Batch Processing Complete!')
        )
