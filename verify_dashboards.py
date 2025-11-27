#!/usr/bin/env python
"""
STEP 9 Dashboard Implementation Verification
Confirms all three dashboard views are working with proper data
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Administrator, Class, Student, AcademicTerm, StudentBalance, Payment
from core.views.dashboard_views import AdminDashboardView, ClassDashboardView, StudentDashboardView

def test_admin_dashboard():
    """Test AdminDashboardView context data"""
    print("\n📊 ADMIN DASHBOARD VIEW")
    print("=" * 50)
    
    view = AdminDashboardView()
    view.request = type('Request', (), {
        'user': Administrator.objects.filter(is_superuser=True).first()
    })()
    
    context = view.get_context_data()
    
    checks = [
        ('total_students', context.get('total_students', 0) > 0),
        ('total_classes', context.get('total_classes', 0) > 0),
        ('total_arrears', context.get('total_arrears', 0) >= 0),
        ('collection_rate', 'collection_rate' in context),
        ('students_with_arrears', 'students_with_arrears' in context),
        ('6-term history data', 'term_collected' in context),
        ('class_distribution', 'class_distribution_labels' in context),
        ('balance_distribution', 'balance_paid_count' in context),
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    return all(result for _, result in checks)

def test_class_dashboard():
    """Test ClassDashboardView with a real class"""
    print("\n📚 CLASS DASHBOARD VIEW")
    print("=" * 50)
    
    class_obj = Class.objects.first()
    if not class_obj:
        print("❌ No classes found in database")
        return False
    
    print(f"Testing with class: {class_obj.grade} {class_obj.section}")
    
    view = ClassDashboardView()
    view.request = type('Request', (), {
        'user': Administrator.objects.filter(is_superuser=True).first()
    })()
    view.kwargs = {'class_id': class_obj.id}
    
    context = view.get_context_data()
    
    checks = [
        ('class_obj', context.get('class_obj') == class_obj),
        ('students', 'students' in context),
        ('class_fee_collected', 'class_fee_collected' in context),
        ('class_fee_due', 'class_fee_due' in context),
        ('class_total_arrears', 'class_total_arrears' in context),
        ('collection_rate', 'class_collection_rate' in context),
        ('gender_distribution', 'gender_labels' in context),
        ('age_distribution', 'age_labels' in context),
        ('students_needing_attention', 'students_needing_attention' in context),
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    return all(result for _, result in checks)

def test_student_dashboard():
    """Test StudentDashboardView with a real student"""
    print("\n👤 STUDENT DASHBOARD VIEW")
    print("=" * 50)
    
    student = Student.objects.first()
    if not student:
        print("❌ No students found in database")
        return False
    
    print(f"Testing with student: {student.get_full_name()}")
    
    view = StudentDashboardView()
    view.request = type('Request', (), {
        'user': Administrator.objects.filter(is_superuser=True).first()
    })()
    view.kwargs = {'student_id': student.id}
    
    context = view.get_context_data()
    
    checks = [
        ('student', context.get('student') == student),
        ('current_balance_obj', 'current_balance_obj' in context or 'current_balance' in context),
        ('all_balances', 'all_balances' in context),
        ('all_payments', 'all_payments' in context),
        ('collection_rate', 'collection_rate' in context),
        ('arrears_timeline', 'arrears_timeline_labels' in context),
        ('payment_method_distribution', 'payment_method_labels' in context),
        ('projected_next_terms', 'projected_next_terms' in context),
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    return all(result for _, result in checks)

def test_database_status():
    """Show current data status"""
    print("\n💾 DATABASE STATUS")
    print("=" * 50)
    
    print(f"✅ Classes: {Class.objects.count()}")
    print(f"✅ Students: {Student.objects.count()}")
    print(f"✅ Academic Terms: {AcademicTerm.objects.count()}")
    print(f"✅ Student Balances: {StudentBalance.objects.count()}")
    print(f"✅ Payments: {Payment.objects.count()}")
    
    # Show arrears summary
    current_term = AcademicTerm.get_current_term()
    if current_term:
        balances = StudentBalance.objects.filter(term=current_term)
        total_arrears = sum(float(b.previous_arrears) for b in balances)
        print(f"✅ Current Term Arrears Total: ${total_arrears:.2f}")
    
    return True

def main():
    """Run all verification tests"""
    print("\n" + "=" * 60)
    print("🎯 STEP 9 - THREE DASHBOARD VIEWS VERIFICATION")
    print("=" * 60)
    
    results = {
        'Admin Dashboard': test_admin_dashboard(),
        'Class Dashboard': test_class_dashboard(),
        'Student Dashboard': test_student_dashboard(),
        'Database Status': test_database_status(),
    }
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"\n✅ Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All dashboard views verified and working correctly!")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
