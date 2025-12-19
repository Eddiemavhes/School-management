#!/usr/bin/env python
"""
Management command to archive graduated students who have paid all arrears
"""
from django.core.management.base import BaseCommand
from core.models import Student

class Command(BaseCommand):
    help = 'Archive graduated students who have paid all their fees'

    def handle(self, *args, **options):
        # Find all GRADUATED students who are NOT archived
        graduated = Student.objects.filter(status='GRADUATED', is_archived=False)
        
        self.stdout.write(f"Checking {graduated.count()} graduated students...")
        
        archived_count = 0
        for student in graduated:
            if student.check_and_archive():
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Archived {student.full_name} (Balance: ${student.overall_balance:.2f})"
                    )
                )
                archived_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓✓✓ COMPLETE: {archived_count} students archived as Alumni"
            )
        )
        
        # Show remaining students with arrears
        remaining = Student.objects.filter(status='GRADUATED', is_archived=False)
        if remaining.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  {remaining.count()} students still have outstanding fees:"
                )
            )
            for student in remaining:
                self.stdout.write(
                    f"  • {student.full_name}: ${student.overall_balance:.2f}"
                )
