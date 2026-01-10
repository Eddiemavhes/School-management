from django.test import TestCase
from django.test import TestCase
from decimal import Decimal
from core.models import Class, AcademicTerm, TermFee, Student, StudentBalance, ECDClassProfile, ECDClassFee, AcademicYear
from django.core.exceptions import ValidationError


class ECDFeatureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Academic year and term
        AcademicYear.objects.create(year=2026, start_date='2026-01-01', end_date='2026-12-31', is_active=True)
        cls.term = AcademicTerm.objects.create(academic_year=2026, term=1, start_date='2026-01-01', end_date='2026-03-31', is_current=True)

        # Create an ECD class (ECDA = Early Childhood Development A)
        cls.ecd_class = Class.objects.create(grade='ECDA', section='A', academic_year=2026)

        # Create TermFee for ECD
        cls.term_fee = TermFee.objects.create(term=cls.term, grade_level='ECD', amount=Decimal('100.00'))

        # Create ECDClassProfile with small capacity
        cls.ecd_profile = ECDClassProfile.objects.create(cls=cls.ecd_class, capacity=1, premium=True, meal_plan_fee=Decimal('10.00'))

        # ECDClassFee extra
        cls.ecd_extra = ECDClassFee.objects.create(cls=cls.ecd_class, term=cls.term, amount=Decimal('25.00'), description='Materials')

    def test_capacity_enforced_on_assignment(self):
        # Create first student and assign to class (should succeed)
        s1 = Student.objects.create(surname='One', first_name='A', sex='M', date_of_birth='2019-01-01', birth_entry_number='BE1', current_class=self.ecd_class)
        # Create second student, assigning should raise ValidationError on save
        s2 = Student(surname='Two', first_name='B', sex='F', date_of_birth='2019-02-02', birth_entry_number='BE2', current_class=self.ecd_class)
        with self.assertRaises(ValidationError):
            s2.full_clean()

    def test_balance_includes_ecd_extra(self):
        s = Student.objects.create(surname='Three', first_name='C', sex='M', date_of_birth='2019-03-03', birth_entry_number='BE3', current_class=self.ecd_class)
        # Initialize balance
        bal = StudentBalance.initialize_term_balance(s, self.term)
        self.assertIsNotNone(bal)
        # base fee
        base = bal.term_fee_record.amount
        # total term_fee should include ECDClassProfile meal_plan_fee ($10) + ECDClassFee extras ($25)
        # Total should be $100 + $10 + $25 = $135
        self.assertEqual(bal.term_fee, base + Decimal('10.00') + Decimal('25.00'))