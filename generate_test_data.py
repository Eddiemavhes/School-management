"""
STEP 13: Comprehensive Test Data Generation Script

Generates realistic test data including:
- 10+ Students with varied profiles
- 3+ Teachers with class assignments
- All grades (1-7) with multiple classes
- Academic years and terms
- Student balances with payments and arrears
- Test cases for edge cases
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from core.models import (
    Student, Class, Administrator, 
    AcademicYear, AcademicTerm, StudentBalance, Payment
)
import random

def clear_test_data():
    """Clear previous test data - OPTIONAL"""
    print("⚠️  Warning: This will NOT delete existing data. Run manually if needed:")
    print("   - Student.objects.all().delete()")
    print("   - Teacher.objects.all().delete()")
    print("   - Class.objects.all().delete()")

def create_academic_structure():
    """Create years, terms, and classes structure"""
    print("\n📅 Creating Academic Structure...")
    
    # Create/get current year
    current_year, _ = AcademicYear.objects.get_or_create(
        year=2025,
        defaults={'is_active': True}
    )
    
    # Create terms
    terms_data = [
        (1, '2025-01-15', '2025-04-15'),
        (2, '2025-04-16', '2025-08-15'),
        (3, '2025-08-16', '2025-12-15'),
    ]
    
    for term_num, start_date, end_date in terms_data:
        term, _ = AcademicTerm.objects.get_or_create(
            academic_year=current_year.year,
            term=term_num,  # Pass integer 1, 2, or 3
            defaults={
                'start_date': start_date,
                'end_date': end_date,
                'is_current': term_num == 2  # Make Term 2 current
            }
        )
    
    print(f"✅ Created/verified {AcademicTerm.objects.filter(academic_year=current_year.year).count()} terms for {current_year.year}")
    return current_year

def create_classes(academic_year):
    """Create all grades with multiple classes"""
    print("\n🏫 Creating Classes...")
    
    grades = [1, 2, 3, 4, 5, 6, 7]  # Use integers 1-7
    sections = ['A', 'B', 'C']
    
    year_int = academic_year.year if hasattr(academic_year, 'year') else academic_year
    
    created_count = 0
    for grade in grades:
        for section in sections:
            obj, created = Class.objects.get_or_create(
                grade=grade,
                section=section,
                academic_year=year_int,
                defaults={'term_fee': Decimal('5000.00')}
            )
            if created:
                created_count += 1
    
    total_classes = Class.objects.filter(academic_year=year_int).count()
    print(f"✅ Created/verified {total_classes} classes ({len(grades)} grades × {len(sections)} sections)")
    return Class.objects.filter(academic_year=year_int)

def create_teachers():
    """Create 3+ teachers with class assignments"""
    print("\n👨‍🏫 Creating Teachers...")
    
    teacher_data = [
        {
            'username': 'mr_johnson',
            'email': 'johnson@school.com',
            'first_name': 'John',
            'last_name': 'Johnson',
        },
        {
            'username': 'ms_smith',
            'email': 'smith@school.com',
            'first_name': 'Sarah',
            'last_name': 'Smith',
        },
        {
            'username': 'mr_williams',
            'email': 'williams@school.com',
            'first_name': 'Michael',
            'last_name': 'Williams',
        },
        {
            'username': 'ms_brown',
            'email': 'brown@school.com',
            'first_name': 'Emily',
            'last_name': 'Brown',
        },
    ]
    
    teachers = []
    created_count = 0
    for data in teacher_data:
        # Create teacher admin user
        username = data['username']
        admin, admin_created = Administrator.objects.get_or_create(
            username=username,
            defaults={
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'is_staff': False,
                'is_superuser': False
            }
        )
        
        if admin_created:
            admin.set_password('teacher123')  # Default password
            admin.save()
            created_count += 1
        
        teachers.append(admin)
    
    print(f"✅ Created/verified {len(teachers)} teachers ({created_count} new)")
    return teachers

def assign_teachers_to_classes(teachers, classes):
    """Assign teachers as class teachers"""
    print("\n🔗 Assigning Teachers to Classes...")
    
    class_list = list(classes)
    teacher_list = list(teachers) * ((len(class_list) // len(teachers)) + 1)
    
    assigned = 0
    for class_obj, teacher in zip(class_list, teacher_list):
        class_obj.teacher = teacher
        class_obj.save()
        assigned += 1
    
    print(f"✅ Assigned {assigned} teachers to classes")

def create_students(classes):
    """Create 10+ diverse students with edge cases"""
    print("\n👥 Creating Students...")
    
    first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 
                   'Henry', 'Iris', 'Jack', 'Karen', 'Leo', 'Maria', 'Nathan', 'Olivia']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 
                  'Miller', 'Davis', 'Rodriguez', 'Martinez']
    
    class_list = list(classes)
    students = []
    created_count = 0
    
    # Create diverse students
    for i in range(15):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        assigned_class = class_list[i % len(class_list)]
        
        # Varied age ranges
        years_old = random.randint(5, 13)
        dob = date.today() - timedelta(days=years_old*365 + random.randint(0, 364))
        
        # Generate student ID
        student_id = f"STU{2025}{i+1:03d}"
        
        student, created = Student.objects.get_or_create(
            student_id=student_id,
            defaults={
                'student_name': first_name,
                'student_surname': last_name,
                'date_of_birth': dob,
                'phone_number': f"555-{1000+i:04d}",
                'gender': random.choice(['Male', 'Female']),
                'student_class': assigned_class,
                'emergency_contact': f"Parent of {first_name}",
                'emergency_contact_phone': f"555-{9000+i:04d}"
            }
        )
        
        if created:
            created_count += 1
            students.append(student)
    
    print(f"✅ Created {created_count} new students (Total: {Student.objects.count()})")
    return students

def create_student_balances(students, academic_year):
    """Create balances with varied payment statuses"""
    print("\n💰 Creating Student Balances...")
    
    year_int = academic_year.year if hasattr(academic_year, 'year') else academic_year
    terms = AcademicTerm.objects.filter(academic_year=year_int)
    created_count = 0
    
    for student in students:
        for term in terms:
            balance, created = StudentBalance.objects.get_or_create(
                student=student,
                term=term,
                defaults={
                    'term_fee': Decimal('5000.00'),
                    'amount_paid': Decimal('0.00'),
                    'previous_arrears': Decimal('0.00')
                }
            )
            
            if created:
                # Simulate various payment scenarios
                rand = random.random()
                
                if rand < 0.3:  # 30% fully paid
                    balance.amount_paid = balance.term_fee
                elif rand < 0.6:  # 30% partial payment
                    balance.amount_paid = balance.term_fee * Decimal(random.uniform(0.3, 0.9))
                elif rand < 0.85:  # 25% unpaid
                    balance.amount_paid = Decimal('0.00')
                else:  # 15% overpaid (edge case)
                    balance.amount_paid = balance.term_fee + Decimal(random.randint(100, 500))
                
                balance.save()
                created_count += 1
    
    print(f"✅ Created {created_count} student balance records")

def create_payments(academic_year):
    """Create payment records"""
    print("\n💳 Creating Payment Records...")
    
    balances = StudentBalance.objects.filter(term__academic_year=academic_year, amount_paid__gt=0)
    created_count = 0
    
    for balance in balances:
        # Create 1-3 payment records per balance
        num_payments = random.randint(1, 3)
        remaining = balance.amount_paid
        
        for _ in range(num_payments):
            if remaining <= 0:
                break
            
            payment_amount = min(remaining, balance.term_fee * Decimal(random.uniform(0.2, 0.8)))
            
            payment, created = Payment.objects.get_or_create(
                student_balance=balance,
                amount=payment_amount,
                payment_date=timezone.now() - timedelta(days=random.randint(0, 90)),
                defaults={
                    'payment_method': random.choice(['cash', 'bank_transfer', 'check']),
                    'reference_number': f"PAY{random.randint(100000, 999999)}"
                }
            )
            
            if created:
                created_count += 1
            
            remaining -= payment_amount
    
    print(f"✅ Created {created_count} payment records")

def create_edge_case_students(classes):
    """Create specific edge case test students"""
    print("\n⚠️  Creating Edge Case Students...")
    
    edge_cases = []
    
    # Edge Case 1: Student with negative balance (overpayment)
    class_obj = classes[0]
    student1, _ = Student.objects.get_or_create(
        student_id='STU2025NEGATIVE',
        defaults={
            'student_name': 'Overpay',
            'student_surname': 'Student',
            'date_of_birth': date(2010, 6, 15),
            'phone_number': '555-9990',
            'gender': 'Male',
            'student_class': class_obj
        }
    )
    edge_cases.append(('Negative Balance', student1))
    
    # Edge Case 2: Student with zero balance
    student2, _ = Student.objects.get_or_create(
        student_id='STU2025ZERO',
        defaults={
            'student_name': 'Zero',
            'student_surname': 'Balance',
            'date_of_birth': date(2010, 8, 20),
            'phone_number': '555-9991',
            'gender': 'Female',
            'student_class': class_obj
        }
    )
    edge_cases.append(('Zero Balance', student2))
    
    # Create balances for edge cases
    year = 2025
    for term in AcademicTerm.objects.filter(academic_year=year):
        # Overpayment
        balance1, _ = StudentBalance.objects.get_or_create(
            student=student1,
            term=term,
            defaults={
                'term_fee': Decimal('5000.00'),
                'amount_paid': Decimal('5500.00'),  # Overpaid by 500
                'previous_arrears': Decimal('0.00')
            }
        )
        
        # Zero balance
        balance2, _ = StudentBalance.objects.get_or_create(
            student=student2,
            term=term,
            defaults={
                'term_fee': Decimal('5000.00'),
                'amount_paid': Decimal('5000.00'),  # Fully paid
                'previous_arrears': Decimal('0.00')
            }
        )
    
    print(f"✅ Created {len(edge_cases)} edge case students:")
    for name, student in edge_cases:
        print(f"   - {name}: {student.student_name} {student.student_surname}")
    
    return edge_cases

def generate_test_report():
    """Generate summary report of test data"""
    print("\n" + "="*60)
    print("📊 TEST DATA GENERATION REPORT")
    print("="*60)
    
    try:
        current_year = AcademicYear.objects.get(year=2025)
    except:
        current_year = {'year': 2025}
    
    print(f"\n📅 Academic Structure:")
    print(f"   Years: {AcademicYear.objects.count()}")
    print(f"   Terms: {AcademicTerm.objects.filter(academic_year=2025).count()}")
    print(f"   Classes: {Class.objects.filter(academic_year=2025).count()}")
    
    print(f"\n👥 Students and Teachers:")
    print(f"   Students: {Student.objects.count()}")
    print(f"   Teachers (Administrators): {Administrator.objects.count()}")
    
    print(f"\n💰 Financial Data:")
    print(f"   Student Balances: {StudentBalance.objects.count()}")
    print(f"   Payment Records: {Payment.objects.count()}")
    
    # Payment status distribution
    balances = StudentBalance.objects.all()
    paid_count = sum(1 for b in balances if b.amount_paid >= b.term_fee + b.previous_arrears)
    partial_count = sum(1 for b in balances if 0 < b.amount_paid < b.term_fee + b.previous_arrears)
    unpaid_count = sum(1 for b in balances if b.amount_paid == 0)
    overpaid_count = sum(1 for b in balances if b.amount_paid > b.term_fee + b.previous_arrears)
    
    print(f"\n📊 Payment Status Distribution:")
    if len(balances) > 0:
        print(f"   Paid (100%): {paid_count} ({paid_count*100//len(balances)}%)")
        print(f"   Partial (1-99%): {partial_count} ({partial_count*100//len(balances)}%)")
        print(f"   Unpaid (0%): {unpaid_count} ({unpaid_count*100//len(balances)}%)")
        print(f"   Overpaid: {overpaid_count}")
    
    # Arrears tracking
    with_arrears = sum(1 for b in balances if b.previous_arrears > 0)
    total_arrears = sum(b.previous_arrears for b in balances)
    print(f"\n📈 Arrears Tracking:")
    print(f"   Students with arrears: {with_arrears}")
    print(f"   Total arrears: ${total_arrears}")
    
    print(f"\n✅ Test data generation complete!")
    print("="*60 + "\n")

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🧪 STEP 13: TEST DATA GENERATION SCRIPT")
    print("="*60)
    
    try:
        # Clear old data warning
        clear_test_data()
        
        # Create academic structure
        academic_year = create_academic_structure()
        
        # Create classes
        classes = create_classes(academic_year)
        
        # Create teachers
        teachers = create_teachers()
        
        # Assign teachers to classes
        assign_teachers_to_classes(teachers, classes)
        
        # Create students
        students = create_students(classes)
        
        # Create student balances
        create_student_balances(students, academic_year)
        
        # Create payments
        create_payments(academic_year)
        
        # Create edge case students
        create_edge_case_students(classes)
        
        # Generate report
        generate_test_report()
        
    except Exception as e:
        print(f"\n❌ Error during test data generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
