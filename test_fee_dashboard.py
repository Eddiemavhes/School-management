import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student, StudentBalance
from core.utils.pdf_reports_modern import PaymentHistoryReport

# Collect all student data
students_data = []
for student in Student.objects.all()[:10]:
    # Get balance info
    balance_obj = StudentBalance.objects.filter(student=student).first()
    
    if balance_obj:
        students_data.append({
            'name': student.full_name,
            'class': student.current_class,
            'term_fee': balance_obj.term_fee,
            'amount_paid': balance_obj.amount_paid,
            'current_balance': balance_obj.current_balance,
            'id': student.id
        })

if students_data:
    print(f"✨ Generating BEAUTIFUL Fee Dashboard PDF")
    print(f"📊 Students: {len(students_data)}")
    
    # Generate fee dashboard PDF
    pdf = PaymentHistoryReport.generate_fee_dashboard_pdf("First Term 2027", students_data)
    
    # Save to file
    pdf_path = 'test_fee_dashboard_beautiful.pdf'
    with open(pdf_path, 'wb') as f:
        f.write(pdf.getvalue())
    
    file_size = os.path.getsize(pdf_path)
    print(f"✅ PDF generated successfully!")
    print(f"📄 File: {pdf_path}")
    print(f"📊 Size: {file_size:,} bytes")
    print(f"\n🎨 ENHANCED STYLING:")
    print(f"  ✓ Light blue card backgrounds (#f0f7ff)")
    print(f"  ✓ Strong blue table headers (#1e3a8a)")
    print(f"  ✓ Subtle blue borders (#bfdbfe)")
    print(f"  ✓ Better contrast and readability")
    print(f"  ✓ Professional spacing throughout")
else:
    print("No students found")
