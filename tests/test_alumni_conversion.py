"""
Comprehensive tests for Grade 7 Alumni Conversion System

Tests all aspects of the automatic alumni conversion feature:
- Real-time conversion on payment (signal handler)
- Batch conversion via management command
- Status transition validation
- Edge cases and error conditions
"""
import os
import django
from django.test import TestCase
from django.utils import timezone
from django.core.management import call_command
from decimal import Decimal
from io import StringIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import (
    Student, StudentBalance, AcademicTerm, Payment, Administrator, 
    AcademicYear, Class
)
from core.services.alumni_conversion import AlumniConversionService
from django.core.exceptions import ValidationError


class AlumniConversionTestCase(TestCase):
    """Test suite for alumni conversion functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data for all tests"""
        super().setUpClass()
        
        # Create academic year and terms
        cls.year = AcademicYear.objects.create(year=2027, is_active=True)
        cls.term3 = AcademicTerm.objects.create(
            academic_year=cls.year,
            term=3,
            start_date='2027-07-01',
            end_date='2027-09-30',
            is_current=True
        )
        cls.term2 = AcademicTerm.objects.create(
            academic_year=cls.year,
            term=2,
            start_date='2027-04-01',
            end_date='2027-06-30'
        )
        
        # Create Grade 7 class
        cls.grade7_class = Class.objects.create(
            grade=7,
            section='A',
            academic_year=2027
        )
        
        # Create admin for recording payments
        cls.admin = Administrator.objects.create(
            email='test@school.com',
            is_staff=True,
            is_superuser=True
        )
        cls.admin.set_password('testpass123')
        cls.admin.save()
    
    def setUp(self):
        """Set up test data for each test"""
        # Create a test student
        self.student = Student.objects.create(
            surname='TestStudent',
            first_name='Alumni',
            sex='M',
            date_of_birth='2010-01-01',
            birth_entry_number='TEST123',
            current_class=self.grade7_class,
            status='ENROLLED'
        )
        
        # Initialize balance for Term 3
        self.balance = StudentBalance.initialize_term_balance(self.student, self.term3)
    
    def test_student_created_as_enrolled(self):
        """Test that Grade 7 students start as ENROLLED"""
        self.assertEqual(self.student.status, 'ENROLLED')
        self.assertTrue(self.student.is_active)
    
    def test_alumni_conversion_service_basic(self):
        """Test AlumniConversionService.convert_to_alumni()"""
        result = AlumniConversionService.convert_to_alumni(self.student)
        
        self.assertTrue(result)
        self.student.refresh_from_db()
        self.assertEqual(self.student.status, 'ALUMNI')
        self.assertFalse(self.student.is_active)
        self.assertIsNotNone(self.student.alumni_date)
    
    def test_status_transition_enrolled_to_alumni(self):
        """Test ENROLLED -> ALUMNI status transition"""
        self.student.status = 'ALUMNI'
        # Should not raise ValidationError
        self.student.full_clean()
        self.student.save()
        
        self.assertEqual(self.student.status, 'ALUMNI')
    
    def test_status_transition_active_to_alumni(self):
        """Test ACTIVE -> ALUMNI status transition"""
        # First transition to ACTIVE
        self.student.status = 'ACTIVE'
        self.student.save()
        
        # Then to ALUMNI
        self.student.status = 'ALUMNI'
        self.student.save()
        
        self.assertEqual(self.student.status, 'ALUMNI')
    
    def test_alumni_conversion_on_exact_payment(self):
        """Test alumni conversion when payment brings balance to exactly 0"""
        # Student owes 100
        self.assertEqual(self.balance.current_balance, Decimal('100.00'))
        
        # Make payment of exactly 100
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal('100.00'),
            payment_date=timezone.now().date(),
            term=self.term3,
            payment_method='CASH',
            recorded_by=self.admin
        )
        
        self.student.refresh_from_db()
        self.balance.refresh_from_db()
        
        # Should be converted to alumni
        self.assertEqual(self.student.status, 'ALUMNI')
        self.assertFalse(self.student.is_active)
        self.assertEqual(self.balance.current_balance, Decimal('0.00'))
    
    def test_alumni_conversion_on_overpayment(self):
        """Test alumni conversion when payment exceeds balance (credit)"""
        # Student owes 100
        self.assertEqual(self.balance.current_balance, Decimal('100.00'))
        
        # Make payment of 150 (50 credit)
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal('150.00'),
            payment_date=timezone.now().date(),
            term=self.term3,
            payment_method='CASH',
            recorded_by=self.admin
        )
        
        self.student.refresh_from_db()
        self.balance.refresh_from_db()
        
        # Should be converted to alumni (balance is negative/credit)
        self.assertEqual(self.student.status, 'ALUMNI')
        self.assertEqual(self.balance.current_balance, Decimal('-50.00'))
    
    def test_no_conversion_on_partial_payment(self):
        """Test that partial payment does not convert to alumni"""
        # Student owes 100
        self.assertEqual(self.balance.current_balance, Decimal('100.00'))
        
        # Make partial payment of 50
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            payment_date=timezone.now().date(),
            term=self.term3,
            payment_method='CASH',
            recorded_by=self.admin
        )
        
        self.student.refresh_from_db()
        self.balance.refresh_from_db()
        
        # Should NOT be converted (balance still 50)
        self.assertEqual(self.student.status, 'ENROLLED')
        self.assertTrue(self.student.is_active)
        self.assertEqual(self.balance.current_balance, Decimal('50.00'))
    
    def test_no_conversion_for_non_grade7(self):
        """Test that non-Grade 7 students don't convert on zero balance"""
        # Create a Grade 6 student
        grade6_class = Class.objects.create(
            grade=6,
            section='A',
            academic_year=2027
        )
        grade6_student = Student.objects.create(
            surname='Grade6',
            first_name='Student',
            sex='M',
            date_of_birth='2010-01-01',
            birth_entry_number='G6TEST123',
            current_class=grade6_class,
            status='ENROLLED'
        )
        
        balance = StudentBalance.initialize_term_balance(grade6_student, self.term3)
        
        # Make payment to clear balance
        payment = Payment.objects.create(
            student=grade6_student,
            amount=Decimal('100.00'),
            payment_date=timezone.now().date(),
            term=self.term3,
            payment_method='CASH',
            recorded_by=self.admin
        )
        
        grade6_student.refresh_from_db()
        
        # Should NOT be converted (not Grade 7)
        self.assertEqual(grade6_student.status, 'ENROLLED')
    
    def test_no_conversion_for_non_term3(self):
        """Test that Grade 7 in non-Term 3 don't convert on zero balance"""
        # Make payment for Term 2 (not Term 3)
        balance_term2 = StudentBalance.initialize_term_balance(self.student, self.term2)
        
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal('100.00'),
            payment_date=timezone.now().date(),
            term=self.term2,  # NOT Term 3
            payment_method='CASH',
            recorded_by=self.admin
        )
        
        self.student.refresh_from_db()
        
        # Should NOT be converted (not Term 3)
        self.assertEqual(self.student.status, 'ENROLLED')
    
    def test_batch_conversion_management_command(self):
        """Test batch conversion via management command"""
        # Create another Grade 7 student with zero balance
        student2 = Student.objects.create(
            surname='Second',
            first_name='Student',
            sex='F',
            date_of_birth='2010-01-01',
            birth_entry_number='TEST456',
            current_class=self.grade7_class,
            status='ACTIVE'
        )
        balance2 = StudentBalance.initialize_term_balance(student2, self.term3)
        
        # Create payments to clear balances
        Payment.objects.create(
            student=self.student,
            amount=Decimal('100.00'),
            payment_date=timezone.now().date(),
            term=self.term3,
            payment_method='CASH',
            recorded_by=self.admin
        )
        
        Payment.objects.create(
            student=student2,
            amount=Decimal('100.00'),
            payment_date=timezone.now().date(),
            term=self.term3,
            payment_method='CASH',
            recorded_by=self.admin
        )
        
        # Run management command
        out = StringIO()
        call_command('check_grade7_alumni', stdout=out)
        
        # Verify both students were converted
        self.student.refresh_from_db()
        student2.refresh_from_db()
        
        self.assertEqual(self.student.status, 'ALUMNI')
        self.assertEqual(student2.status, 'ALUMNI')
    
    def test_check_alumni_eligibility(self):
        """Test AlumniConversionService.check_alumni_eligibility()"""
        # Not eligible (balance > 0)
        result = AlumniConversionService.check_alumni_eligibility(self.student, self.term3)
        self.assertFalse(result['eligible'])
        self.assertEqual(result['balance'], Decimal('100.00'))
        
        # Make payment to zero balance
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal('100.00'),
            payment_date=timezone.now().date(),
            term=self.term3,
            payment_method='CASH',
            recorded_by=self.admin
        )
        
        self.balance.refresh_from_db()
        
        # Now eligible
        result = AlumniConversionService.check_alumni_eligibility(self.student, self.term3)
        self.assertTrue(result['eligible'])
        self.assertEqual(result['balance'], Decimal('0.00'))
    
    def test_alumni_cannot_be_deactivated(self):
        """Test that alumni status is final"""
        AlumniConversionService.convert_to_alumni(self.student)
        self.student.refresh_from_db()
        
        # Try to change status back
        self.student.status = 'ACTIVE'
        
        with self.assertRaises(ValidationError):
            self.student.full_clean()
    
    def test_multiple_payments_accumulate(self):
        """Test that multiple partial payments accumulate correctly"""
        # Payment 1: 30
        Payment.objects.create(
            student=self.student,
            amount=Decimal('30.00'),
            payment_date=timezone.now().date(),
            term=self.term3,
            payment_method='CASH',
            recorded_by=self.admin
        )
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.current_balance, Decimal('70.00'))
        self.assertEqual(self.student.status, 'ENROLLED')
        
        # Payment 2: 40
        Payment.objects.create(
            student=self.student,
            amount=Decimal('40.00'),
            payment_date=timezone.now().date(),
            term=self.term3,
            payment_method='CASH',
            recorded_by=self.admin
        )
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.current_balance, Decimal('30.00'))
        self.assertEqual(self.student.status, 'ENROLLED')
        
        # Final payment: 30 → alumni conversion
        Payment.objects.create(
            student=self.student,
            amount=Decimal('30.00'),
            payment_date=timezone.now().date(),
            term=self.term3,
            payment_method='CASH',
            recorded_by=self.admin
        )
        
        self.student.refresh_from_db()
        self.balance.refresh_from_db()
        self.assertEqual(self.student.status, 'ALUMNI')
        self.assertEqual(self.balance.current_balance, Decimal('0.00'))


if __name__ == '__main__':
    import unittest
    unittest.main()
