"""
ArrearsVaultService - Business logic for strict arrears management
Enforces absolute rules: No flexibility, No exceptions, No discretion
"""

from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models.arrears_vault import ArrearsVault, ArrearsPaymentLog


class ArrearsVaultService:
    """
    Service class for managing Arrears Vault records.
    
    STRICT ENFORCEMENT:
    - Only 100% payment accepted
    - No partial payments recorded as progress
    - No waivers, adjustments, or exceptions
    - All records are immutable after creation
    """
    
    @staticmethod
    def create_vault_record(student, graduation_year, final_balance, parent_info=None):
        """
        Create an immutable vault record for a graduated student with arrears.
        
        Args:
            student: Student instance
            graduation_year: Year of graduation (int)
            final_balance: Outstanding balance amount (Decimal)
            parent_info: Optional dict with parent details
        
        Returns:
            ArrearsVault instance
        
        Raises:
            ValidationError if balance is <= 0
        """
        if final_balance <= 0:
            raise ValidationError("Only create vault for students with positive balance")
        
        if ArrearsVault.objects.filter(student_id=student.id).exists():
            raise ValidationError("Student already has vault record")
        
        parent_info = parent_info or {}
        
        vault = ArrearsVault.objects.create(
            student_id=student.id,
            student_full_name=student.full_name,
            student_birth_entry=student.birth_entry_number,
            graduation_year=graduation_year,
            graduation_grade='7',
            fixed_balance=final_balance,
            required_payment=final_balance,
            parent_name=parent_info.get('name', 'Parent/Guardian'),
            parent_phone=parent_info.get('phone', ''),
            parent_email=parent_info.get('email', ''),
        )
        
        return vault
    
    @staticmethod
    def process_payment_strict(vault, amount, payment_method='Manual'):
        """
        Process payment with ABSOLUTE enforcement.
        
        RULES:
        - amount MUST equal fixed_balance exactly
        - Partial payments are REJECTED
        - Escrow is optional but doesn't change balance
        
        Args:
            vault: ArrearsVault instance
            amount: Payment amount (Decimal or float)
            payment_method: How payment was made
        
        Returns:
            dict with 'accepted' (bool), 'message' (str)
        """
        amount = Decimal(str(amount))
        
        # Check if already transitioned
        if vault.transition_date:
            return {
                'accepted': False,
                'message': f'Student already paid in full and transitioned to ALUMNI on {vault.transition_date.date()}',
                'student': vault.student_full_name,
            }
        
        # BINARY CHECK: Exact match only
        if amount == vault.fixed_balance:
            # Process full payment
            try:
                vault.process_full_payment(amount, payment_method)
                return {
                    'accepted': True,
                    'message': f'✅ FULL PAYMENT ACCEPTED - {vault.student_full_name} transitioned to ALUMNI',
                    'student': vault.student_full_name,
                    'amount': str(amount),
                    'new_status': 'ALUMNI',
                    'transition_date': vault.transition_date.isoformat(),
                }
            except Exception as e:
                return {
                    'accepted': False,
                    'message': f'Error processing payment: {str(e)}',
                }
        
        elif amount > 0 and amount < vault.fixed_balance:
            # Partial payment - REJECT but hold in escrow
            vault.hold_partial_payment(amount)
            return {
                'accepted': False,
                'message': f'❌ PARTIAL PAYMENT REJECTED\nRequired: ${vault.fixed_balance}\nReceived: ${amount}\nBalance remains: ${vault.fixed_balance}\n\n${amount} has been held in escrow pending full payment.',
                'student': vault.student_full_name,
                'amount_held': str(amount),
                'required_amount': str(vault.fixed_balance),
                'status': 'GRADUATED_WITH_ARREARS',
            }
        
        elif amount > vault.fixed_balance:
            # Excess payment - REJECT
            return {
                'accepted': False,
                'message': f'❌ EXCESS PAYMENT REJECTED\nRequired: ${vault.fixed_balance}\nReceived: ${amount}\n\nPayment exceeds required amount.',
                'student': vault.student_full_name,
                'required_amount': str(vault.fixed_balance),
            }
        
        else:
            # Invalid amount
            return {
                'accepted': False,
                'message': f'Invalid payment amount: ${amount}',
            }
    
    @staticmethod
    def get_vault_summary():
        """
        Get system-wide summary of arrears vault.
        Shows indefinite nature of the debt.
        """
        from django.db.models import Sum, Count, Min
        
        unpaid = ArrearsVault.objects.filter(status='GRADUATED_WITH_ARREARS')
        paid = ArrearsVault.objects.exclude(status='GRADUATED_WITH_ARREARS')
        
        return {
            'total_in_vault': unpaid.count(),
            'total_arrears': unpaid.aggregate(Sum('fixed_balance'))['fixed_balance__sum'] or Decimal('0'),
            'oldest_graduation_year': unpaid.aggregate(Min('graduation_year'))['graduation_year__min'],
            'total_transitioned_to_alumni': paid.count(),
            'breakdown_by_year': list(
                unpaid.values('graduation_year')
                .annotate(count=Count('id'), total=Sum('fixed_balance'))
                .order_by('-graduation_year')
            ),
            'payment_attempts': unpaid.aggregate(Sum('total_payment_attempts'))['total_payment_attempts__sum'] or 0,
            'total_escrowed': unpaid.aggregate(Sum('total_escrowed'))['total_escrowed__sum'] or Decimal('0'),
            'collection_rate': '0%',  # By design - policy prevents partial payment acceptance
            'policy_enforcement': {
                'no_partial_payments_accepted': True,
                'no_waivers_granted': True,
                'no_payment_plans_offered': True,
                'no_administrative_exceptions': True,
            }
        }
    
    @staticmethod
    def generate_permanent_register(graduation_year=None):
        """
        Generate permanent register of arrears by graduation year.
        Shows indefinite tracking with no write-offs or forgiveness.
        """
        from django.db.models import Sum, Count
        
        unpaid = ArrearsVault.objects.filter(status='GRADUATED_WITH_ARREARS')
        
        if graduation_year:
            unpaid = unpaid.filter(graduation_year=graduation_year)
        
        students = unpaid.order_by('student_full_name').values(
            'student_full_name',
            'student_birth_entry',
            'graduation_year',
            'fixed_balance',
            'created_at',
            'total_payment_attempts',
            'total_escrowed',
        )
        
        return {
            'year': graduation_year,
            'total_count': unpaid.count(),
            'total_arrears': unpaid.aggregate(Sum('fixed_balance'))['fixed_balance__sum'] or Decimal('0'),
            'students': list(students),
            'policy_note': 'All balances remain fixed indefinitely. No statute of limitations. No write-offs.',
        }
