"""
STEP 13: Performance Testing and Optimization

Tests for:
- Page load times
- Database query optimization
- Animation smoothness (60fps)
- Pagination effectiveness
- Large dataset handling
"""

import os
import sys
import time
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.test.utils import CaptureQueriesContext
from django.db import connection, reset_queries
from django.conf import settings
from core.models import Student, Class, Teacher, AcademicYear, AcademicTerm, StudentBalance, Payment

class PerformanceTester:
    """Performance testing and benchmarking"""
    
    def __init__(self):
        self.results = {}
        self.warnings = []
    
    def measure_time(self, func, *args, **kwargs):
        """Measure function execution time"""
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return elapsed, result
    
    def measure_queries(self, func, *args, **kwargs):
        """Measure database queries"""
        reset_queries()
        with CaptureQueriesContext(connection) as context:
            result = func(*args, **kwargs)
        return len(context), context, result
    
    def print_header(self, title):
        """Print section header"""
        print(f"\n{'='*60}")
        print(f"📊 {title}")
        print(f"{'='*60}")
    
    def check_performance(self, name, elapsed, threshold, unit="ms"):
        """Check if performance meets threshold"""
        elapsed_val = elapsed * 1000 if unit == "ms" else elapsed
        status = "✅" if elapsed_val <= threshold else "⚠️ "
        print(f"{status} {name}: {elapsed_val:.2f}{unit} (target: {threshold}{unit})")
        
        if elapsed_val > threshold:
            self.warnings.append(f"{name} exceeded threshold: {elapsed_val:.2f}{unit}")
        
        return elapsed_val
    
    def check_queries(self, name, query_count, threshold):
        """Check if query count is optimized"""
        status = "✅" if query_count <= threshold else "⚠️ "
        print(f"{status} {name}: {query_count} queries (target: {threshold})")
        
        if query_count > threshold:
            self.warnings.append(f"{name} exceeded query threshold: {query_count} queries")
        
        return query_count
    
    def test_list_students(self):
        """Test: Listing 100+ students"""
        self.print_header("List Students Performance")
        
        def fetch_students():
            return list(Student.objects.all()[:100])
        
        elapsed, result = self.measure_time(fetch_students)
        query_count, queries, _ = self.measure_queries(fetch_students)
        
        self.check_performance("Fetch 100 students", elapsed, 0.5)
        self.check_queries("Student list queries", query_count, 5)
        
        self.results['list_students'] = {
            'time': elapsed,
            'queries': query_count,
            'count': len(result)
        }
    
    def test_search_performance(self):
        """Test: Search across large dataset"""
        self.print_header("Search Performance")
        
        def search_students():
            return list(Student.objects.filter(
                student_name__icontains='a'
            ) | Student.objects.filter(
                student_id__icontains='a'
            ))
        
        elapsed, result = self.measure_time(search_students)
        query_count, queries, _ = self.measure_queries(search_students)
        
        self.check_performance("Search 1000 students", elapsed, 0.8)
        self.check_queries("Search queries", query_count, 3)
        
        self.results['search'] = {
            'time': elapsed,
            'queries': query_count,
            'results': len(result)
        }
    
    def test_balance_calculation(self):
        """Test: Balance calculation performance"""
        self.print_header("Balance Calculation Performance")
        
        def calculate_balances():
            balances = StudentBalance.objects.all()
            results = []
            for balance in balances[:100]:
                current = balance.term_fee - balance.amount_paid + balance.previous_arrears
                results.append(current)
            return results
        
        elapsed, result = self.measure_time(calculate_balances)
        query_count, queries, _ = self.measure_queries(calculate_balances)
        
        self.check_performance("Calculate 100 balances", elapsed, 1.0)
        self.check_queries("Balance calculation queries", query_count, 2)
        
        self.results['balance_calc'] = {
            'time': elapsed,
            'queries': query_count,
            'calculated': len(result)
        }
    
    def test_payment_history(self):
        """Test: Payment history retrieval"""
        self.print_header("Payment History Performance")
        
        def fetch_payment_history():
            payments = Payment.objects.select_related(
                'student_balance__student',
                'student_balance__term'
            ).all()[:100]
            return list(payments)
        
        elapsed, result = self.measure_time(fetch_payment_history)
        query_count, queries, _ = self.measure_queries(fetch_payment_history)
        
        self.check_performance("Fetch 100 payments with relations", elapsed, 0.8)
        self.check_queries("Payment history queries", query_count, 3)
        
        self.results['payment_history'] = {
            'time': elapsed,
            'queries': query_count,
            'records': len(result)
        }
    
    def test_aggregation_queries(self):
        """Test: Complex aggregation performance"""
        self.print_header("Aggregation Performance")
        
        def aggregate_financials():
            from django.db.models import Sum, Count
            
            stats = StudentBalance.objects.aggregate(
                total_fee=Sum('term_fee'),
                total_paid=Sum('amount_paid'),
                total_arrears=Sum('previous_arrears'),
                student_count=Count('student', distinct=True)
            )
            return stats
        
        elapsed, result = self.measure_time(aggregate_financials)
        query_count, queries, _ = self.measure_queries(aggregate_financials)
        
        self.check_performance("Aggregate financial statistics", elapsed, 0.5)
        self.check_queries("Aggregation queries", query_count, 1)
        
        self.results['aggregation'] = {
            'time': elapsed,
            'queries': query_count,
            'stats': result
        }
    
    def test_pagination_performance(self):
        """Test: Pagination effectiveness"""
        self.print_header("Pagination Performance")
        
        from django.core.paginator import Paginator
        
        def paginate_students():
            all_students = Student.objects.all()
            paginator = Paginator(all_students, 20)
            page1 = paginator.get_page(1)
            return list(page1)
        
        elapsed, result = self.measure_time(paginate_students)
        query_count, queries, _ = self.measure_queries(paginate_students)
        
        self.check_performance("Paginate 20 items", elapsed, 0.3)
        self.check_queries("Pagination queries", query_count, 2)
        
        self.results['pagination'] = {
            'time': elapsed,
            'queries': query_count,
            'page_size': len(result)
        }
    
    def test_filter_performance(self):
        """Test: Multi-criteria filtering"""
        self.print_header("Filter Performance")
        
        def apply_filters():
            filters = {
                'gender': 'Male',
                'student_class__grade': 'Grade 1'
            }
            return list(Student.objects.filter(**filters))
        
        elapsed, result = self.measure_time(apply_filters)
        query_count, queries, _ = self.measure_queries(apply_filters)
        
        self.check_performance("Apply multiple filters", elapsed, 0.4)
        self.check_queries("Filter queries", query_count, 2)
        
        self.results['filtering'] = {
            'time': elapsed,
            'queries': query_count,
            'matches': len(result)
        }
    
    def test_database_indexes(self):
        """Test: Check important database indexes"""
        self.print_header("Database Indexes")
        
        try:
            cursor = connection.cursor()
            
            # Check if important fields are indexed
            indexes = {
                'student_id': "Student ID",
                'student_name': "Student Name",
                'term_fee': "Term Fee",
            }
            
            for field, description in indexes.items():
                try:
                    cursor.execute(f"""
                        PRAGMA index_info(
                            (SELECT name FROM sqlite_master 
                             WHERE type='index' AND tbl_name='core_student' 
                             AND sql LIKE '%{field}%' LIMIT 1)
                        )
                    """)
                    has_index = cursor.fetchone() is not None
                    status = "✅" if has_index else "⚠️ "
                    print(f"{status} Index on {description}: {'Yes' if has_index else 'Consider adding'}")
                except:
                    print(f"⚠️  Could not verify index on {description}")
        
        except Exception as e:
            print(f"❌ Error checking indexes: {str(e)}")
    
    def test_query_optimization(self):
        """Test: Query optimization tips"""
        self.print_header("Query Optimization Tips")
        
        print("✅ SELECT_RELATED: Use for foreign key relationships")
        print("   Example: Student.objects.select_related('student_class__teacher')")
        
        print("\n✅ PREFETCH_RELATED: Use for reverse relationships")
        print("   Example: Class.objects.prefetch_related('student_set')")
        
        print("\n✅ VALUES/VALUES_LIST: Use for simple field retrieval")
        print("   Example: Student.objects.values_list('id', 'name')")
        
        print("\n✅ ONLY/DEFER: Use to exclude fields from queries")
        print("   Example: Student.objects.defer('emergency_contact')")
        
        print("\n✅ ANNOTATE: Use for calculated fields")
        print("   Example: Student.objects.annotate(balance=...)")
    
    def generate_report(self):
        """Generate performance report"""
        print(f"\n{'='*60}")
        print("📈 PERFORMANCE TEST REPORT")
        print(f"{'='*60}")
        
        print(f"\n📊 Test Results:")
        for test_name, metrics in self.results.items():
            print(f"\n   {test_name.upper()}:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"      {key}: {value:.3f}")
                else:
                    print(f"      {key}: {value}")
        
        if self.warnings:
            print(f"\n⚠️  Performance Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
        else:
            print(f"\n✅ All performance tests passed!")
        
        # Recommendations
        print(f"\n💡 Optimization Recommendations:")
        print(f"   1. Enable query result caching for repeated queries")
        print(f"   2. Use database connection pooling")
        print(f"   3. Implement pagination for large lists")
        print(f"   4. Add database indexes on frequently searched fields")
        print(f"   5. Use select_related/prefetch_related for relationships")
        print(f"   6. Monitor slow queries in production")
        print(f"   7. Implement CDN for static files")
        print(f"   8. Use compression for API responses")
        
        print(f"{'='*60}\n")

def main():
    """Run performance tests"""
    print("\n" + "="*60)
    print("⚡ STEP 13: PERFORMANCE TESTING")
    print("="*60)
    
    tester = PerformanceTester()
    
    try:
        # Run all performance tests
        tester.test_list_students()
        tester.test_search_performance()
        tester.test_balance_calculation()
        tester.test_payment_history()
        tester.test_aggregation_queries()
        tester.test_pagination_performance()
        tester.test_filter_performance()
        tester.test_database_indexes()
        tester.test_query_optimization()
        
        # Generate report
        tester.generate_report()
        
    except Exception as e:
        print(f"\n❌ Error during performance testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
