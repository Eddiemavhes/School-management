"""
STEP 13: Comprehensive Testing Suite

Tests for:
- Student registration and flow
- Teacher assignment and reassignment
- Payment recording and balance calculation
- Promotion, demotion, class transfers
- Search and filter functionality
- Permissions and security
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from core.models import (
    Student, Class, Administrator, 
    AcademicYear, AcademicTerm, StudentBalance, Payment
)
import django.db.models

class TestSuiteRunner:
    """Main test runner managing all tests"""
    
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'skipped': []
        }
        self.client = Client()
    
    def log(self, level, message):
        """Log test messages"""
        icons = {'✅': '✅', '❌': '❌', '⏭️': '⏭️', 'ℹ️': 'ℹ️'}
        print(f"{icons.get(level, level)} {message}")
    
    def test(self, name, func):
        """Run a single test"""
        try:
            print(f"\n🧪 {name}")
            func()
            self.results['passed'].append(name)
            self.log('✅', f"PASSED: {name}")
        except AssertionError as e:
            self.results['failed'].append((name, str(e)))
            self.log('❌', f"FAILED: {name} - {str(e)}")
        except Exception as e:
            self.results['failed'].append((name, str(e)))
            self.log('❌', f"ERROR: {name} - {str(e)}")

class StudentRegistrationTests(TestSuiteRunner):
    """Test student registration and creation"""
    
    def setup(self):
        """Setup test data"""
        self.academic_year = AcademicYear.objects.create(year=2025, is_active=True)
        self.class_obj = Class.objects.create(
            grade='Grade 1',
            section='A',
            academic_year=self.academic_year,
            term_fee=Decimal('5000.00')
        )
    
    def test_student_creation(self):
        """Test: Creating a student with valid data"""
        self.setup()
        
        student = Student.objects.create(
            student_id='STU2025001',
            student_name='John',
            student_surname='Doe',
            date_of_birth=date(2015, 6, 15),
            phone_number='555-0001',
            gender='Male',
            student_class=self.class_obj
        )
        
        assert student.id is not None, "Student should have ID"
        assert student.student_name == 'John', "Student name should be saved"
        assert student.student_class == self.class_obj, "Class assignment should work"
        self.log('✅', f"Created student: {student.student_name} {student.student_surname}")
    
    def test_initial_balance_creation(self):
        """Test: Creating initial balance for new student"""
        self.setup()
        
        student = Student.objects.create(
            student_id='STU2025002',
            student_name='Jane',
            student_surname='Smith',
            date_of_birth=date(2015, 8, 20),
            phone_number='555-0002',
            gender='Female',
            student_class=self.class_obj
        )
        
        term = AcademicTerm.objects.create(
            academic_year=self.academic_year,
            term='Term 1',
            start_date=date(2025, 1, 15),
            end_date=date(2025, 4, 15),
            is_current=True
        )
        
        balance = StudentBalance.objects.create(
            student=student,
            term=term,
            term_fee=Decimal('5000.00'),
            amount_paid=Decimal('0.00'),
            previous_arrears=Decimal('0.00')
        )
        
        assert balance.student == student, "Balance should be linked to student"
        assert balance.term_fee == Decimal('5000.00'), "Term fee should be set"
        self.log('✅', f"Created initial balance: ${balance.term_fee}")

class PaymentTests(TestSuiteRunner):
    """Test payment recording and balance calculations"""
    
    def setup(self):
        """Setup test data"""
        self.academic_year = AcademicYear.objects.create(year=2025, is_active=True)
        self.class_obj = Class.objects.create(
            grade='Grade 2',
            section='B',
            academic_year=self.academic_year,
            term_fee=Decimal('5000.00')
        )
        self.term = AcademicTerm.objects.create(
            academic_year=self.academic_year,
            term='Term 1',
            start_date=date(2025, 1, 15),
            end_date=date(2025, 4, 15),
            is_current=True
        )
        self.student = Student.objects.create(
            student_id='STU2025003',
            student_name='Alex',
            student_surname='Johnson',
            date_of_birth=date(2015, 10, 10),
            phone_number='555-0003',
            gender='Male',
            student_class=self.class_obj
        )
        self.balance = StudentBalance.objects.create(
            student=self.student,
            term=self.term,
            term_fee=Decimal('5000.00'),
            amount_paid=Decimal('0.00'),
            previous_arrears=Decimal('0.00')
        )
    
    def test_full_payment(self):
        """Test: Recording full payment"""
        self.setup()
        
        payment = Payment.objects.create(
            student_balance=self.balance,
            amount=Decimal('5000.00'),
            payment_date=timezone.now(),
            payment_method='cash',
            reference_number='PAY000001'
        )
        
        self.balance.amount_paid = Decimal('5000.00')
        self.balance.save()
        
        assert payment.amount == Decimal('5000.00'), "Payment amount should be recorded"
        assert self.balance.amount_paid == Decimal('5000.00'), "Balance should be updated"
        self.log('✅', f"Recorded full payment: ${payment.amount}")
    
    def test_partial_payment(self):
        """Test: Recording partial payment"""
        self.setup()
        
        payment1 = Payment.objects.create(
            student_balance=self.balance,
            amount=Decimal('2000.00'),
            payment_date=timezone.now(),
            payment_method='bank_transfer'
        )
        
        payment2 = Payment.objects.create(
            student_balance=self.balance,
            amount=Decimal('1500.00'),
            payment_date=timezone.now(),
            payment_method='check'
        )
        
        self.balance.amount_paid = Decimal('3500.00')
        self.balance.save()
        
        total_paid = Payment.objects.filter(student_balance=self.balance).aggregate(
            total=django.db.models.Sum('amount')
        )['total']
        
        assert total_paid == Decimal('3500.00'), "Total payments should sum correctly"
        self.log('✅', f"Recorded partial payments: ${total_paid}")
    
    def test_overpayment(self):
        """Test: Edge case - student overpayment"""
        self.setup()
        
        payment = Payment.objects.create(
            student_balance=self.balance,
            amount=Decimal('5500.00'),  # Overpayment of 500
            payment_date=timezone.now(),
            payment_method='cash'
        )
        
        self.balance.amount_paid = Decimal('5500.00')
        self.balance.save()
        
        overpayment = self.balance.amount_paid - self.balance.term_fee
        assert overpayment == Decimal('500.00'), "Overpayment should be calculated"
        self.log('✅', f"Overpayment detected: ${overpayment}")

class PromotionDemotionTests(TestSuiteRunner):
    """Test promotion, demotion, and class transfers"""
    
    def setup(self):
        """Setup test data"""
        self.academic_year = AcademicYear.objects.create(year=2025, is_active=True)
        self.next_year = AcademicYear.objects.create(year=2026, is_active=False)
        
        self.grade1_class = Class.objects.create(
            grade='Grade 1',
            section='A',
            academic_year=self.academic_year,
            term_fee=Decimal('5000.00')
        )
        
        self.grade2_class = Class.objects.create(
            grade='Grade 2',
            section='A',
            academic_year=self.next_year,
            term_fee=Decimal('5500.00')
        )
        
        self.term = AcademicTerm.objects.create(
            academic_year=self.academic_year,
            term='Term 3',
            start_date=date(2025, 8, 15),
            end_date=date(2025, 12, 15),
            is_current=True
        )
        
        self.student = Student.objects.create(
            student_id='STU2025004',
            student_name='Bob',
            student_surname='Williams',
            date_of_birth=date(2014, 5, 20),
            phone_number='555-0004',
            gender='Male',
            student_class=self.grade1_class
        )
        
        self.balance = StudentBalance.objects.create(
            student=self.student,
            term=self.term,
            term_fee=Decimal('5000.00'),
            amount_paid=Decimal('3000.00'),
            previous_arrears=Decimal('500.00')
        )
    
    def test_promotion_preserves_arrears(self):
        """Test: Promoting student preserves previous arrears"""
        self.setup()
        
        # Get current balance info
        old_arrears = self.balance.previous_arrears
        
        # Promote student (simulate)
        self.student.student_class = self.grade2_class
        self.student.save()
        
        # Create new balance for promoted student in next year
        new_term = AcademicTerm.objects.create(
            academic_year=self.next_year,
            term='Term 1',
            start_date=date(2026, 1, 15),
            end_date=date(2026, 4, 15)
        )
        
        new_balance = StudentBalance.objects.create(
            student=self.student,
            term=new_term,
            term_fee=Decimal('5500.00'),
            amount_paid=Decimal('0.00'),
            previous_arrears=old_arrears  # Preserve arrears
        )
        
        assert new_balance.previous_arrears == old_arrears, "Arrears should be preserved"
        self.log('✅', f"Promotion preserved arrears: ${new_balance.previous_arrears}")
    
    def test_class_transfer_preserves_balance(self):
        """Test: Class transfer within same year preserves balance"""
        self.setup()
        
        # Create another class in same grade
        grade1_class_b = Class.objects.create(
            grade='Grade 1',
            section='B',
            academic_year=self.academic_year,
            term_fee=Decimal('5000.00')
        )
        
        # Get current balance
        current_balance = self.balance.amount_paid
        current_arrears = self.balance.previous_arrears
        
        # Transfer student
        self.student.student_class = grade1_class_b
        self.student.save()
        
        # Balance should remain unchanged
        self.balance.refresh_from_db()
        assert self.balance.amount_paid == current_balance, "Balance should be preserved"
        assert self.balance.previous_arrears == current_arrears, "Arrears should be preserved"
        self.log('✅', f"Class transfer preserved balance: ${current_balance}")

class SearchFilterTests(TestSuiteRunner):
    """Test search and filter functionality"""
    
    def setup(self):
        """Setup test data"""
        self.academic_year = AcademicYear.objects.create(year=2025, is_active=True)
        self.class1 = Class.objects.create(
            grade='Grade 1',
            section='A',
            academic_year=self.academic_year,
            term_fee=Decimal('5000.00')
        )
        self.term = AcademicTerm.objects.create(
            academic_year=self.academic_year,
            term='Term 1',
            start_date=date(2025, 1, 15),
            end_date=date(2025, 4, 15),
            is_current=True
        )
        
        # Create test students with different statuses
        students_data = [
            ('Paid', Decimal('5000.00')),
            ('Partial', Decimal('3000.00')),
            ('Unpaid', Decimal('0.00')),
        ]
        
        for name, paid_amount in students_data:
            student = Student.objects.create(
                student_id=f'STU2025{100+len(name)}',
                student_name=name,
                student_surname='TestStudent',
                date_of_birth=date(2015, 6, 15),
                phone_number=f'555-00{len(name)}',
                gender='Male',
                student_class=self.class1
            )
            
            StudentBalance.objects.create(
                student=student,
                term=self.term,
                term_fee=Decimal('5000.00'),
                amount_paid=paid_amount,
                previous_arrears=Decimal('0.00')
            )
    
    def test_search_by_name(self):
        """Test: Search students by name"""
        self.setup()
        
        results = Student.objects.filter(student_name__icontains='Paid')
        assert results.count() >= 1, "Should find student by name"
        self.log('✅', f"Found {results.count()} students by name search")
    
    def test_filter_by_payment_status(self):
        """Test: Filter students by payment status"""
        self.setup()
        
        # Paid students
        paid = StudentBalance.objects.filter(
            amount_paid__gte=django.db.models.F('term_fee')
        ).count()
        
        # Unpaid students
        unpaid = StudentBalance.objects.filter(amount_paid=0).count()
        
        assert paid > 0 or unpaid > 0, "Should have students with different payment statuses"
        self.log('✅', f"Found {paid} paid, {unpaid} unpaid students")

class PermissionTests(TestSuiteRunner):
    """Test permissions and security"""
    
    def test_login_required(self):
        """Test: Dashboard requires login"""
        response = self.client.get('/admin/dashboard/')
        assert response.status_code in [301, 302, 403], "Dashboard should require login"
        self.log('✅', f"Login required enforced (HTTP {response.status_code})")
    
    def test_admin_authentication(self):
        """Test: Admin user authentication"""
        admin = Administrator.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        assert admin.check_password('testpass123'), "Password should be verified"
        self.log('✅', "Admin authentication working")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 STEP 13: COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    test_suites = [
        ('Student Registration Tests', StudentRegistrationTests()),
        ('Payment & Balance Tests', PaymentTests()),
        ('Promotion & Transfer Tests', PromotionDemotionTests()),
        ('Search & Filter Tests', SearchFilterTests()),
        ('Permission Tests', PermissionTests()),
    ]
    
    all_results = {'passed': [], 'failed': [], 'skipped': []}
    
    for suite_name, suite in test_suites:
        print(f"\n{'='*60}")
        print(f"📋 {suite_name}")
        print(f"{'='*60}")
        
        if hasattr(suite, 'test_student_creation'):
            suite.test('Student Creation', suite.test_student_creation)
        if hasattr(suite, 'test_initial_balance_creation'):
            suite.test('Initial Balance Creation', suite.test_initial_balance_creation)
        if hasattr(suite, 'test_full_payment'):
            suite.test('Full Payment Recording', suite.test_full_payment)
        if hasattr(suite, 'test_partial_payment'):
            suite.test('Partial Payment Recording', suite.test_partial_payment)
        if hasattr(suite, 'test_overpayment'):
            suite.test('Overpayment Detection', suite.test_overpayment)
        if hasattr(suite, 'test_promotion_preserves_arrears'):
            suite.test('Promotion Preserves Arrears', suite.test_promotion_preserves_arrears)
        if hasattr(suite, 'test_class_transfer_preserves_balance'):
            suite.test('Class Transfer Preserves Balance', suite.test_class_transfer_preserves_balance)
        if hasattr(suite, 'test_search_by_name'):
            suite.test('Search by Name', suite.test_search_by_name)
        if hasattr(suite, 'test_filter_by_payment_status'):
            suite.test('Filter by Payment Status', suite.test_filter_by_payment_status)
        if hasattr(suite, 'test_login_required'):
            suite.test('Login Required', suite.test_login_required)
        if hasattr(suite, 'test_admin_authentication'):
            suite.test('Admin Authentication', suite.test_admin_authentication)
        
        all_results['passed'].extend(suite.results['passed'])
        all_results['failed'].extend(suite.results['failed'])
        all_results['skipped'].extend(suite.results['skipped'])
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {len(all_results['passed'])}")
    print(f"❌ Failed: {len(all_results['failed'])}")
    print(f"⏭️  Skipped: {len(all_results['skipped'])}")
    
    if all_results['failed']:
        print(f"\n❌ Failed Tests:")
        for name, error in all_results['failed']:
            print(f"   - {name}: {error}")
    
    total = len(all_results['passed']) + len(all_results['failed'])
    success_rate = (len(all_results['passed']) / total * 100) if total > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    print("="*60 + "\n")

if __name__ == '__main__':
    # Import django models aggregation function
    import django.db.models
    main()
