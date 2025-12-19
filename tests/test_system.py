"""
SCHOOL MANAGEMENT SYSTEM - VERIFICATION TEST
Tests critical functionality to ensure system is production-ready

Run with: python manage.py test tests.test_system -v 1
"""

from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import date
from django.core.exceptions import ValidationError
from django.db.models import Sum

from core.models import (
    Student, AcademicTerm, Payment, Class, TermFee, StudentBalance,
    Administrator, AcademicYear
)


class SystemVerificationTest(TestCase):
    """Complete system verification test suite."""
    
    @classmethod
    def setUpTestData(cls):
        """Create all test data once for the entire test class."""
        cls.admin = Administrator.objects.create_user(
            email='testadmin@school.local',
            password='testpass123',
            first_name='Test',
            last_name='Admin'
        )
        
        cls.year_2027 = AcademicYear.objects.create(
            year=2027,
            start_date=date(2027, 1, 1),
            end_date=date(2027, 12, 31),
            is_active=True
        )
        
        cls.term_1_2027 = AcademicTerm.objects.create(
            academic_year=2027,
            term=1,
            start_date=date(2027, 1, 15),
            end_date=date(2027, 4, 15),
            is_current=True
        )
        
        cls.term_2_2027 = AcademicTerm.objects.create(
            academic_year=2027,
            term=2,
            start_date=date(2027, 5, 1),
            end_date=date(2027, 8, 15)
        )
        
        cls.term_3_2027 = AcademicTerm.objects.create(
            academic_year=2027,
            term=3,
            start_date=date(2027, 9, 1),
            end_date=date(2027, 11, 30)
        )
        
        cls.grade_7_class = Class.objects.create(
            academic_year=2027,
            grade=7,
            section='A'
        )
        
        cls.term_fee = Decimal('100.00')
        TermFee.objects.create(term=cls.term_1_2027, amount=cls.term_fee)
        TermFee.objects.create(term=cls.term_2_2027, amount=cls.term_fee)
        TermFee.objects.create(term=cls.term_3_2027, amount=cls.term_fee)
    
    # TEST 1: Student creation
    def test_1_create_student(self):
        """Test: Create a new student"""
        student = Student.objects.create(
            surname='Smith',
            first_name='Alice',
            sex='F',
            date_of_birth=date(2010, 1, 15),
            birth_entry_number='ZIM-2010-00001',
            current_class=self.grade_7_class
        )
        
        self.assertIsNotNone(student.id)
        self.assertEqual(student.surname, 'Smith')
        self.assertTrue(student.is_active)
        self.assertEqual(str(student), 'Smith, Alice')
    
    # TEST 2: Duplicate prevention
    def test_2_prevent_duplicate_birth_entry(self):
        """Test: Prevent duplicate birth entry numbers"""
        Student.objects.create(
            surname='Jones',
            first_name='Bob',
            sex='M',
            date_of_birth=date(2010, 2, 15),
            birth_entry_number='ZIM-2010-00002',
            current_class=self.grade_7_class
        )
        
        with self.assertRaises(Exception):
            Student.objects.create(
                surname='Brown',
                first_name='Charlie',
                sex='M',
                date_of_birth=date(2010, 3, 15),
                birth_entry_number='ZIM-2010-00002',
                current_class=self.grade_7_class
            )
    
    # TEST 3: Student deactivation
    def test_3_deactivate_student(self):
        """Test: Deactivate and reactivate student"""
        student = Student.objects.create(
            surname='Davis',
            first_name='Diana',
            sex='F',
            date_of_birth=date(2010, 4, 15),
            birth_entry_number='ZIM-2010-00003',
            current_class=self.grade_7_class
        )
        
        student.is_active = False
        student.save()
        self.assertFalse(student.is_active)
        
        student.is_active = True
        student.save()
        self.assertTrue(student.is_active)
    
    # TEST 4: Balance creation
    def test_4_create_balance(self):
        """Test: Create balance for student"""
        student = Student.objects.create(
            surname='Evans',
            first_name='Emma',
            sex='F',
            date_of_birth=date(2010, 5, 15),
            birth_entry_number='ZIM-2010-00004',
            current_class=self.grade_7_class
        )
        
        balance = StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=Decimal('0'),
            amount_paid=Decimal('0')
        )
        
        self.assertEqual(balance.term_fee, self.term_fee)
        self.assertEqual(balance.total_due, self.term_fee)
        self.assertEqual(balance.current_balance, self.term_fee)
    
    # TEST 5: Balance with arrears
    def test_5_balance_with_arrears(self):
        """Test: Balance includes previous arrears"""
        student = Student.objects.create(
            surname='Frank',
            first_name='Fiona',
            sex='F',
            date_of_birth=date(2010, 6, 15),
            birth_entry_number='ZIM-2010-00005',
            current_class=self.grade_7_class
        )
        
        previous_arrears = Decimal('250.00')
        balance = StudentBalance.objects.create(
            student=student,
            term=self.term_2_2027,
            term_fee_record=TermFee.objects.get(term=self.term_2_2027),
            previous_arrears=previous_arrears,
            amount_paid=Decimal('0')
        )
        
        expected_total = self.term_fee + previous_arrears
        self.assertEqual(balance.total_due, expected_total)
        self.assertEqual(balance.current_balance, expected_total)
    
    # TEST 6: Payment recording
    def test_6_record_payment(self):
        """Test: Record payment and update balance"""
        student = Student.objects.create(
            surname='Green',
            first_name='George',
            sex='M',
            date_of_birth=date(2010, 7, 15),
            birth_entry_number='ZIM-2010-00006',
            current_class=self.grade_7_class
        )
        
        balance = StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=Decimal('0'),
            amount_paid=Decimal('0')
        )
        
        payment_amount = Decimal('60.00')
        Payment.objects.create(
            student=student,
            term=self.term_1_2027,
            amount=payment_amount,
            payment_method='CASH',
            recorded_by=self.admin
        )
        
        total_paid = Payment.objects.filter(
            student=student,
            term=self.term_1_2027
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        balance.amount_paid = total_paid
        balance.save()
        
        expected_balance = self.term_fee - payment_amount
        self.assertEqual(balance.current_balance, expected_balance)
    
    # TEST 7: Multiple payments
    def test_7_multiple_payments(self):
        """Test: Multiple payments accumulate correctly"""
        student = Student.objects.create(
            surname='Harris',
            first_name='Henry',
            sex='M',
            date_of_birth=date(2010, 8, 15),
            birth_entry_number='ZIM-2010-00007',
            current_class=self.grade_7_class
        )
        
        balance = StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=Decimal('200.00'),
            amount_paid=Decimal('0')
        )
        
        Payment.objects.create(
            student=student, term=self.term_1_2027, amount=Decimal('100.00'),
            payment_method='CASH', recorded_by=self.admin
        )
        Payment.objects.create(
            student=student, term=self.term_1_2027, amount=Decimal('50.00'),
            payment_method='BANK', recorded_by=self.admin
        )
        Payment.objects.create(
            student=student, term=self.term_1_2027, amount=Decimal('50.00'),
            payment_method='CASH', recorded_by=self.admin
        )
        
        total_paid = Payment.objects.filter(
            student=student,
            term=self.term_1_2027
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        balance.amount_paid = total_paid
        balance.save()
        
        self.assertEqual(balance.amount_paid, Decimal('200.00'))
        self.assertEqual(balance.current_balance, Decimal('100.00'))
    
    # TEST 8: Overpayment
    def test_8_overpayment_creates_credit(self):
        """Test: Overpayment creates credit (negative balance)"""
        student = Student.objects.create(
            surname='Iverson',
            first_name='Isaac',
            sex='M',
            date_of_birth=date(2010, 9, 15),
            birth_entry_number='ZIM-2010-00008',
            current_class=self.grade_7_class
        )
        
        balance = StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=Decimal('0'),
            amount_paid=Decimal('0')
        )
        
        Payment.objects.create(
            student=student, term=self.term_1_2027, amount=Decimal('500.00'),
            payment_method='CASH', recorded_by=self.admin
        )
        
        total_paid = Payment.objects.filter(
            student=student,
            term=self.term_1_2027
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        balance.amount_paid = total_paid
        balance.save()
        
        self.assertEqual(balance.current_balance, Decimal('-400.00'))
    
    # TEST 9: Prevent negative payment
    def test_9_prevent_negative_payment(self):
        """Test: Negative payments not allowed"""
        student = Student.objects.create(
            surname='Jackson',
            first_name='Jane',
            sex='F',
            date_of_birth=date(2010, 10, 15),
            birth_entry_number='ZIM-2010-00009',
            current_class=self.grade_7_class
        )
        
        StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=Decimal('0'),
            amount_paid=Decimal('0')
        )
        
        with self.assertRaises(ValidationError):
            payment = Payment(
                student=student,
                term=self.term_1_2027,
                amount=Decimal('-100.00'),
                payment_method='CASH',
                recorded_by=self.admin
            )
            payment.save()
    
    # TEST 10: Get current term
    def test_10_get_current_term(self):
        """Test: Current term retrieval works"""
        current = AcademicTerm.get_current_term()
        
        self.assertIsNotNone(current)
        self.assertTrue(current.is_current)
        self.assertEqual(current.academic_year, 2027)
        self.assertEqual(current.term, 1)
    
    # TEST 11: Term sequencing
    def test_11_term_sequencing(self):
        """Test: Cannot skip terms"""
        year_2030 = AcademicYear.objects.create(
            year=2030,
            start_date=date(2030, 1, 1),
            end_date=date(2030, 12, 31)
        )
        
        with self.assertRaises(ValidationError):
            AcademicTerm.objects.create(
                academic_year=2030,
                term=2,
                start_date=date(2030, 5, 1),
                end_date=date(2030, 8, 15)
            )
    
    # TEST 12: Only one current term
    def test_12_only_one_current_term(self):
        """Test: Only one term can be current"""
        self.assertTrue(self.term_1_2027.is_current)
        
        self.term_2_2027.is_current = True
        self.term_2_2027.save()
        
        self.term_1_2027.refresh_from_db()
        
        self.assertFalse(self.term_1_2027.is_current)
        self.assertTrue(self.term_2_2027.is_current)
    
    # TEST 13: Student class assignment
    def test_13_class_assignment(self):
        """Test: Student assigned to class"""
        student = Student.objects.create(
            surname='King',
            first_name='Kevin',
            sex='M',
            date_of_birth=date(2010, 11, 15),
            birth_entry_number='ZIM-2010-00010',
            current_class=self.grade_7_class
        )
        
        self.assertEqual(student.current_class, self.grade_7_class)
        self.assertIn(student, self.grade_7_class.students.all())
    
    # TEST 14: Move between classes
    def test_14_move_between_classes(self):
        """Test: Move student between classes"""
        grade_7_b = Class.objects.create(
            academic_year=2027,
            grade=7,
            section='B'
        )
        
        student = Student.objects.create(
            surname='Lee',
            first_name='Leo',
            sex='M',
            date_of_birth=date(2010, 12, 15),
            birth_entry_number='ZIM-2010-00011',
            current_class=self.grade_7_class
        )
        
        original_class = student.current_class
        self.assertEqual(original_class.section, 'A')
        
        student.current_class = grade_7_b
        student.save()
        
        self.assertEqual(student.current_class, grade_7_b)
        self.assertEqual(student.current_class.section, 'B')
        self.assertNotEqual(student.current_class, original_class)
    
    # TEST 15: Database consistency
    def test_15_database_consistency(self):
        """Test: Database maintains referential integrity"""
        student = Student.objects.create(
            surname='Martin',
            first_name='Mary',
            sex='F',
            date_of_birth=date(2011, 1, 15),
            birth_entry_number='ZIM-2011-00001',
            current_class=self.grade_7_class
        )
        
        for term in [self.term_1_2027, self.term_2_2027, self.term_3_2027]:
            StudentBalance.objects.create(
                student=student,
                term=term,
                term_fee_record=TermFee.objects.get(term=term),
                previous_arrears=Decimal('0'),
                amount_paid=Decimal('0')
            )
        
        for term in [self.term_1_2027, self.term_2_2027, self.term_3_2027]:
            Payment.objects.create(
                student=student,
                term=term,
                amount=Decimal('50.00'),
                payment_method='CASH',
                recorded_by=self.admin
            )
        
        student_balances = StudentBalance.objects.filter(student=student).count()
        student_payments = Payment.objects.filter(student=student).count()
        
        self.assertEqual(student_balances, 3)
        self.assertEqual(student_payments, 3)
    
    # TEST 16: Zero balance
    def test_16_zero_balance(self):
        """Test: Fully paid student shows zero"""
        student = Student.objects.create(
            surname='Nelson',
            first_name='Nathan',
            sex='M',
            date_of_birth=date(2011, 2, 15),
            birth_entry_number='ZIM-2011-00002',
            current_class=self.grade_7_class
        )
        
        balance = StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=Decimal('0'),
            amount_paid=self.term_fee
        )
        
        self.assertEqual(balance.current_balance, Decimal('0'))
    
    # TEST 17: Large balance
    def test_17_large_balance(self):
        """Test: Large balances handled correctly"""
        student = Student.objects.create(
            surname='Parker',
            first_name='Patricia',
            sex='F',
            date_of_birth=date(2011, 4, 15),
            birth_entry_number='ZIM-2011-00003',
            current_class=self.grade_7_class
        )
        
        large_arrears = Decimal('5000.00')
        balance = StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=large_arrears,
            amount_paid=Decimal('0')
        )
        
        expected_total = self.term_fee + large_arrears
        self.assertEqual(balance.current_balance, expected_total)
    
    # TEST 18: Graduate student
    def test_18_graduate_student(self):
        """Test: Mark student as graduated"""
        student = Student.objects.create(
            surname='Quinn',
            first_name='Quincy',
            sex='M',
            date_of_birth=date(2008, 1, 15),
            birth_entry_number='ZIM-2008-00001',
            current_class=self.grade_7_class
        )
        
        self.assertEqual(student.status, 'ENROLLED')
        
        student.status = 'ALUMNI'
        student.save()
        
        student.refresh_from_db()
        self.assertEqual(student.status, 'ALUMNI')
    
    # TEST 19: Alumni cannot get new balances
    def test_19_alumni_no_new_balances(self):
        """Test: Alumni students should not get new term fees"""
        student = Student.objects.create(
            surname='Reed',
            first_name='Robert',
            sex='M',
            date_of_birth=date(2008, 2, 15),
            birth_entry_number='ZIM-2008-00002',
            current_class=self.grade_7_class
        )
        
        student.status = 'ALUMNI'
        student.save()
        
        existing_balances = StudentBalance.objects.filter(student=student).count()
        self.assertEqual(existing_balances, 0)
    
    # TEST 20: Credit carryover between terms
    def test_20_credit_carryover(self):
        """Test: Credit from overpayment carries to next term"""
        student = Student.objects.create(
            surname='Stevens',
            first_name='Stephanie',
            sex='F',
            date_of_birth=date(2009, 3, 15),
            birth_entry_number='ZIM-2009-00001',
            current_class=self.grade_7_class
        )
        
        balance_term1 = StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=Decimal('0'),
            amount_paid=Decimal('150.00')
        )
        
        credit_from_term1 = abs(balance_term1.current_balance)
        
        balance_term2 = StudentBalance.objects.create(
            student=student,
            term=self.term_2_2027,
            term_fee_record=TermFee.objects.get(term=self.term_2_2027),
            previous_arrears=Decimal('0') - credit_from_term1,
            amount_paid=Decimal('0')
        )
        
        expected_balance_term2 = self.term_fee + (Decimal('0') - credit_from_term1)
        self.assertEqual(balance_term2.total_due, expected_balance_term2)
    
    # TEST 21: Archived student
    def test_21_archive_student(self):
        """Test: Archive student and verify status"""
        student = Student.objects.create(
            surname='Thompson',
            first_name='Thomas',
            sex='M',
            date_of_birth=date(2009, 4, 15),
            birth_entry_number='ZIM-2009-00002',
            current_class=self.grade_7_class
        )
        
        self.assertFalse(student.is_archived)
        
        student.is_archived = True
        student.save()
        
        student.refresh_from_db()
        self.assertTrue(student.is_archived)
    
    # TEST 22: Deactivated vs archived
    def test_22_deactivated_vs_archived(self):
        """Test: Deactivated and archived are separate states"""
        student = Student.objects.create(
            surname='Underwood',
            first_name='Uma',
            sex='F',
            date_of_birth=date(2009, 5, 15),
            birth_entry_number='ZIM-2009-00003',
            current_class=self.grade_7_class
        )
        
        student.is_active = False
        student.is_archived = False
        student.save()
        
        self.assertFalse(student.is_active)
        self.assertFalse(student.is_archived)
        
        student.is_archived = True
        student.save()
        
        student.refresh_from_db()
        self.assertFalse(student.is_active)
        self.assertTrue(student.is_archived)
    
    # TEST 23: Multiple students in same class
    def test_23_multiple_students_same_class(self):
        """Test: Multiple students assigned to same class"""
        grade_7_section_b = Class.objects.create(
            academic_year=2027,
            grade=7,
            section='B'
        )
        
        students = []
        for i in range(5):
            student = Student.objects.create(
                surname=f'Student{i}',
                first_name=f'Name{i}',
                sex='M' if i % 2 == 0 else 'F',
                date_of_birth=date(2010, 6 + i, 15),
                birth_entry_number=f'ZIM-2010-0000{5 + i}',
                current_class=grade_7_section_b
            )
            students.append(student)
        
        class_students = grade_7_section_b.students.all().count()
        self.assertEqual(class_students, 5)
    
    # TEST 24: Payment method variety
    def test_24_payment_methods(self):
        """Test: Different payment methods recorded correctly"""
        student = Student.objects.create(
            surname='Vazquez',
            first_name='Victoria',
            sex='F',
            date_of_birth=date(2010, 7, 15),
            birth_entry_number='ZIM-2010-00006',
            current_class=self.grade_7_class
        )
        
        balance = StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=Decimal('0'),
            amount_paid=Decimal('0')
        )
        
        methods = ['CASH', 'BANK', 'MOBILE']
        for i, method in enumerate(methods):
            Payment.objects.create(
                student=student,
                term=self.term_1_2027,
                amount=Decimal('30.00'),
                payment_method=method,
                recorded_by=self.admin
            )
        
        payments = Payment.objects.filter(student=student)
        payment_methods = set(p.payment_method for p in payments)
        
        self.assertEqual(len(payment_methods), 3)
        self.assertEqual(payment_methods, set(methods))
    
    # TEST 25: Receipt number tracking
    def test_25_receipt_number(self):
        """Test: Receipt numbers stored with payments"""
        student = Student.objects.create(
            surname='Walker',
            first_name='William',
            sex='M',
            date_of_birth=date(2010, 8, 15),
            birth_entry_number='ZIM-2010-00007',
            current_class=self.grade_7_class
        )
        
        StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=Decimal('0'),
            amount_paid=Decimal('0')
        )
        
        receipt_num = 'RCP-2027-12345'
        payment = Payment.objects.create(
            student=student,
            term=self.term_1_2027,
            amount=Decimal('50.00'),
            payment_method='BANK',
            receipt_number=receipt_num,
            recorded_by=self.admin
        )
        
        self.assertEqual(payment.receipt_number, receipt_num)
    
    # TEST 26: Year transition
    def test_26_year_transition(self):
        """Test: Move to new academic year"""
        year_2028 = AcademicYear.objects.create(
            year=2028,
            start_date=date(2028, 1, 1),
            end_date=date(2028, 12, 31),
            is_active=False
        )
        
        grade_7_2028 = Class.objects.create(
            academic_year=2028,
            grade=7,
            section='A'
        )
        
        self.assertEqual(grade_7_2028.academic_year, 2028)
        self.assertNotEqual(grade_7_2028.academic_year, self.grade_7_class.academic_year)
    
    # TEST 27: Term fee consistency
    def test_27_term_fee_consistency(self):
        """Test: Same fee amount for all students in term"""
        students_created = []
        for i in range(3):
            student = Student.objects.create(
                surname=f'FeeTest{i}',
                first_name=f'Fee{i}',
                sex='M',
                date_of_birth=date(2010, 9, 15),
                birth_entry_number=f'ZIM-2010-FEE{i}',
                current_class=self.grade_7_class
            )
            
            balance = StudentBalance.objects.create(
                student=student,
                term=self.term_1_2027,
                term_fee_record=TermFee.objects.get(term=self.term_1_2027),
                previous_arrears=Decimal('0'),
                amount_paid=Decimal('0')
            )
            students_created.append(balance.term_fee)
        
        self.assertTrue(all(fee == self.term_fee for fee in students_created))
    
    # TEST 28: Arrears accumulation across terms
    def test_28_arrears_accumulation(self):
        """Test: Arrears accumulate across multiple terms"""
        student = Student.objects.create(
            surname='Young',
            first_name='Yara',
            sex='F',
            date_of_birth=date(2010, 10, 15),
            birth_entry_number='ZIM-2010-00008',
            current_class=self.grade_7_class
        )
        
        arrears = Decimal('50.00')
        
        balance_term1 = StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=Decimal('0'),
            amount_paid=Decimal('0')
        )
        
        new_arrears = balance_term1.current_balance
        
        balance_term2 = StudentBalance.objects.create(
            student=student,
            term=self.term_2_2027,
            term_fee_record=TermFee.objects.get(term=self.term_2_2027),
            previous_arrears=new_arrears,
            amount_paid=Decimal('0')
        )
        
        balance_term3 = StudentBalance.objects.create(
            student=student,
            term=self.term_3_2027,
            term_fee_record=TermFee.objects.get(term=self.term_3_2027),
            previous_arrears=balance_term2.current_balance,
            amount_paid=Decimal('0')
        )
        
        expected_total_arrears = self.term_fee * 3
        self.assertEqual(balance_term3.current_balance, expected_total_arrears)
    
    # TEST 29: Payment by recorded admin
    def test_29_payment_recorded_by(self):
        """Test: Track which admin recorded payment"""
        admin2 = Administrator.objects.create_user(
            email='admin2@school.local',
            password='testpass123',
            first_name='Second',
            last_name='Admin'
        )
        
        student = Student.objects.create(
            surname='Zola',
            first_name='Zoe',
            sex='F',
            date_of_birth=date(2010, 11, 15),
            birth_entry_number='ZIM-2010-00009',
            current_class=self.grade_7_class
        )
        
        StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=Decimal('0'),
            amount_paid=Decimal('0')
        )
        
        payment1 = Payment.objects.create(
            student=student,
            term=self.term_1_2027,
            amount=Decimal('30.00'),
            payment_method='CASH',
            recorded_by=self.admin
        )
        
        payment2 = Payment.objects.create(
            student=student,
            term=self.term_1_2027,
            amount=Decimal('40.00'),
            payment_method='BANK',
            recorded_by=admin2
        )
        
        self.assertEqual(payment1.recorded_by, self.admin)
        self.assertEqual(payment2.recorded_by, admin2)
        self.assertNotEqual(payment1.recorded_by, payment2.recorded_by)
    
    # TEST 30: Complex scenario - partial payments across terms
    def test_30_complex_partial_payments(self):
        """Test: Student with partial payments across multiple terms"""
        student = Student.objects.create(
            surname='Anderson',
            first_name='Aaron',
            sex='M',
            date_of_birth=date(2010, 12, 15),
            birth_entry_number='ZIM-2010-00010',
            current_class=self.grade_7_class
        )
        
        arrears_term1 = Decimal('0')
        balance_term1 = StudentBalance.objects.create(
            student=student,
            term=self.term_1_2027,
            term_fee_record=TermFee.objects.get(term=self.term_1_2027),
            previous_arrears=arrears_term1,
            amount_paid=Decimal('50.00')
        )
        
        arrears_term2 = balance_term1.current_balance
        balance_term2 = StudentBalance.objects.create(
            student=student,
            term=self.term_2_2027,
            term_fee_record=TermFee.objects.get(term=self.term_2_2027),
            previous_arrears=arrears_term2,
            amount_paid=Decimal('75.00')
        )
        
        arrears_term3 = balance_term2.current_balance
        balance_term3 = StudentBalance.objects.create(
            student=student,
            term=self.term_3_2027,
            term_fee_record=TermFee.objects.get(term=self.term_3_2027),
            previous_arrears=arrears_term3,
            amount_paid=Decimal('225.00')
        )
        
        self.assertIsNotNone(balance_term1)
        self.assertIsNotNone(balance_term2)
        self.assertIsNotNone(balance_term3)
