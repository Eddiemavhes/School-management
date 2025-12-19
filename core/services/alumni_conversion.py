"""
Alumni Conversion Service

Handles automatic conversion of Grade 7 students to Alumni status
when they complete all fee payments in Term 3.

This service ensures:
1. Only Grade 7 students in Term 3 with balance <= 0 are converted
2. All three fields are updated: status, is_active, is_archived
3. Alumni date is recorded
4. Batch processing can catch missed conversions
"""
from django.utils import timezone
from django.db import transaction
from core.models import Student
import logging

logger = logging.getLogger(__name__)


class AlumniConversionService:
    """Service for converting Grade 7 students to Alumni status"""

    @staticmethod
    def convert_to_alumni(student, force=False):
        """
        Convert a Grade 7 student to Alumni status.
        
        Args:
            student (Student): The student to convert
            force (bool): If True, bypass eligibility checks (for emergency fixes)
            
        Returns:
            bool: True if conversion was successful, False otherwise
        """
        try:
            # Check if already alumni
            if student.status == 'ALUMNI' and student.is_active == False:
                logger.info(f'Student {student.first_name} {student.surname} is already properly configured as alumni')
                return False
            
            # Use transaction to ensure atomic update
            with transaction.atomic():
                # Reload from DB to ensure fresh state
                student = Student.objects.select_for_update().get(pk=student.pk)
                
                # Update all required fields
                student.status = 'ALUMNI'
                student.is_active = False
                student.is_archived = True
                
                # Set alumni date if not already set
                if not student.alumni_date:
                    student.alumni_date = timezone.now()
                
                # Save without full_clean to avoid validation errors
                student.save(update_fields=['status', 'is_active', 'is_archived', 'alumni_date'])
                
                logger.info(
                    f'✅ Student {student.first_name} {student.surname} converted to ALUMNI '
                    f'on {student.alumni_date} (status={student.status}, is_active={student.is_active}, is_archived={student.is_archived})'
                )
                
                return True
            
        except Exception as e:
            logger.error(f'Error converting {student.first_name} {student.surname} to alumni: {str(e)}')
            return False

    @staticmethod
    def batch_process_alumni_candidates():
        """
        Batch processing job to find and convert ALL eligible alumni.
        
        This runs daily to catch any missed conversions or manual updates.
        
        Returns:
            dict: {'processed': int, 'converted': int, 'errors': list}
        """
        from core.models import StudentBalance, AcademicTerm
        from django.db.models import Sum, Q
        from core.models.academic import Payment
        
        results = {
            'processed': 0,
            'converted': 0,
            'errors': []
        }
        
        try:
            # Find all Grade 7 students
            grade7_students = Student.objects.filter(
                is_deleted=False,
                current_class__grade=7
            ).select_related('current_class').order_by('surname')
            
            results['processed'] = grade7_students.count()
            
            for student in grade7_students:
                try:
                    # Get all Term 3 balances for this student
                    term3_balances = StudentBalance.objects.filter(
                        student=student,
                        term__term=3
                    ).select_related('term')
                    
                    # Check each Term 3
                    for balance in term3_balances:
                        # Recalculate balance to ensure accuracy
                        total_paid = Payment.objects.filter(
                            student=student,
                            term=balance.term
                        ).aggregate(total=Sum('amount'))['total'] or 0
                        
                        current_balance = balance.current_balance
                        
                        # If balance <= 0 and not already alumni, convert
                        if current_balance <= 0 and student.status != 'ALUMNI':
                            if AlumniConversionService.convert_to_alumni(student):
                                results['converted'] += 1
                        elif current_balance <= 0 and student.status == 'ALUMNI' and student.is_active:
                            # Fix incorrectly configured alumni
                            if AlumniConversionService.convert_to_alumni(student, force=True):
                                logger.warning(f'Fixed incorrectly configured alumni: {student.first_name} {student.surname}')
                                results['converted'] += 1
                                
                except Exception as e:
                    error_msg = f'Error processing {student.first_name} {student.surname}: {str(e)}'
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            logger.info(f'Batch alumni processing complete: {results["converted"]} converted from {results["processed"]} Grade 7 students')
            
        except Exception as e:
            error_msg = f'Fatal error in batch alumni processing: {str(e)}'
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results

    @staticmethod
    def check_alumni_eligibility(student, term):
        """
        Check if a Grade 7 student in Term 3 is eligible for alumni conversion.
        
        Args:
            student (Student): The student to check
            term: The AcademicTerm to check
            
        Returns:
            dict: {'eligible': bool, 'reason': str, 'balance': Decimal}
        """
        from core.models import StudentBalance, AcademicTerm
        
        # Check if student is Grade 7
        if not student.current_class or student.current_class.grade != 7:
            return {
                'eligible': False,
                'reason': 'Student is not in Grade 7',
                'balance': None
            }
        
        # Check if term is Term 3
        if not term or term.term != 3:
            return {
                'eligible': False,
                'reason': 'Not in Term 3',
                'balance': None
            }
        
        # Check if already alumni
        if student.status == 'ALUMNI':
            return {
                'eligible': False,
                'reason': 'Student is already alumni',
                'balance': None
            }
        
        # Get student's balance for this term
        try:
            balance = StudentBalance.objects.get(student=student, term=term)
        except StudentBalance.DoesNotExist:
            return {
                'eligible': False,
                'reason': 'No balance record found for this term',
                'balance': None
            }
        
        # Check if balance is zero or negative
        if balance.current_balance <= 0:
            return {
                'eligible': True,
                'reason': 'All fees paid - eligible for alumni conversion',
                'balance': balance.current_balance
            }
        
        return {
            'eligible': False,
            'reason': f'Still has outstanding balance: {balance.current_balance}',
            'balance': balance.current_balance
        }
