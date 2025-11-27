"""
Fix script: Create missing 2027 balances with correct arrears carryover
This addresses the bug where student balances were not created for the new year during promotion.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models.student import Student
from core.models.fee import StudentBalance, TermFee
from core.models.academic import AcademicTerm
from decimal import Decimal

def fix_2027_balances():
    """Create 2027 balances for promoted students, carrying forward arrears.
    
    IMPORTANT: Graduating students (Grade 7 students) who are promoted to Grade 8:
    - WILL get a 2027 balance
    - But with NO new term fee (term_fee = $0)
    - Only their graduation debt (previous_arrears)
    - They remain active until debt is paid
    - Once debt is cleared, they become alumni
    """
    
    # Get all active students in 2027
    students = Student.objects.filter(is_active=True)
    
    # Get 2027 terms
    terms_2027 = AcademicTerm.objects.filter(academic_year=2027).order_by('term')
    first_term_2027 = terms_2027.first()
    
    if not first_term_2027:
        print("ERROR: No terms found for 2027!")
        return
    
    print(f"Creating balances for First Term 2027...\n")
    
    fixed_count = 0
    graduating_count = 0
    
    for student in students:
        # Get the student's last balance from 2026
        last_2026_balance = StudentBalance.objects.filter(
            student=student,
            term__academic_year=2026
        ).order_by('-term__term').first()
        
        if not last_2026_balance:
            print(f"[SKIP] {student.full_name}: No 2026 balance found - skipping")
            continue
        
        # Check if balance already exists for 2027
        existing_2027 = StudentBalance.objects.filter(
            student=student,
            term__academic_year=2027
        ).exists()
        
        if existing_2027:
            print(f"[OK] {student.full_name}: Balance already exists for 2027 - skipping")
            continue
        
        # Calculate arrears to carry forward (from last 2026 term)
        previous_arrears = last_2026_balance.current_balance
        
        # Check if this is a graduating student
        is_graduating = student.current_class and int(student.current_class.grade) == 7
        
        # Get term fee for first term 2027
        term_fee = TermFee.objects.filter(term=first_term_2027).first()
        if not term_fee:
            print(f"[SKIP] {student.full_name}: No TermFee found for First Term 2027 - skipping")
            continue
            continue
        
        # Create balance for first term 2027
        try:
            if is_graduating:
                # Graduating student: NO new term fee, only graduation debt
                balance_2027_t1 = StudentBalance.objects.create(
                    student=student,
                    term=first_term_2027,
                    term_fee=Decimal('0'),  # No new fees for graduating students
                    previous_arrears=max(Decimal('0'), previous_arrears),  # Graduation debt only
                    amount_paid=Decimal('0')
                )
                
                print(f"[GRAD] {student.full_name}: Grade 7 (Graduating)")
                print(f"      Must clear graduation debt: ${balance_2027_t1.previous_arrears}")
                print(f"      No new term fee")
                print(f"      Total owed: ${balance_2027_t1.current_balance}")
                
                graduating_count += 1
            else:
                # Regular promotion: new term fee + carried arrears
                balance_2027_t1 = StudentBalance.objects.create(
                    student=student,
                    term=first_term_2027,
                    term_fee=term_fee.amount,
                    previous_arrears=max(Decimal('0'), previous_arrears),  # Only positive arrears
                    amount_paid=Decimal('0')
                )
                
                status_str = "[OK]"
                if previous_arrears > 0:
                    status_str += f" (Carried forward ${previous_arrears} arrears)"
                elif previous_arrears < 0:
                    # Student overpaid (credit)
                    status_str += f" (Has ${abs(previous_arrears)} credit)"
                
                print(f"{status_str} {student.full_name}: Created First Term 2027 balance")
                print(f"      Previous Balance (2026 Term 3): ${last_2026_balance.current_balance}")
                print(f"      New Balance (2027 Term 1):")
                print(f"        - Previous Arrears: ${balance_2027_t1.previous_arrears}")
                print(f"        - Term Fee: ${balance_2027_t1.term_fee}")
                print(f"        - Amount Paid: ${balance_2027_t1.amount_paid}")
                print(f"        - Current Balance: ${balance_2027_t1.current_balance}")
            
            print()
            fixed_count += 1
            
        except Exception as e:
            print(f"[ERROR] {student.full_name}: Error creating balance - {str(e)}")
            print()
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: Created {fixed_count} balance(s) for 2027")
    print(f"  - Regular students: {fixed_count - graduating_count}")
    print(f"  - Graduating students: {graduating_count}")
    print(f"{'='*60}\n")
    
    # Verify the fix
    print("Verification of students:")
    print("-" * 60)
    
    verification_students = [
        ('Carol', 'Cross'),
        ('Brandon', 'Brazil'),
        ('Daniel', 'Don')
    ]
    
    for first, last in verification_students:
        student = Student.objects.filter(first_name=first, surname=last).first()
        if student:
            balance_2027 = StudentBalance.objects.filter(
                student=student,
                term__academic_year=2027,
                term__term=1
            ).first()
            
            if balance_2027:
                print(f"\n{first} {last}:")
                print(f"  Grade: {student.current_class.grade if student.current_class else 'N/A'}")
                print(f"  2027 Term 1 Balance: ${balance_2027.current_balance}")
                print(f"  - Term Fee: ${balance_2027.term_fee}")
                print(f"  - Graduation/Regular Debt: ${balance_2027.previous_arrears}")
                print(f"  Overall Balance: ${student.overall_balance}")
            else:
                print(f"\n{first} {last}: No 2027 Term 1 balance found!")

if __name__ == '__main__':
    fix_2027_balances()
