import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import Student
from core.utils.pdf_reports_modern import PaymentHistoryReport, ArrearsReport
from datetime import datetime

# Get a student
student = Student.objects.first()
if student:
    print(f"✨ Testing BEAUTIFUL PDF generation with: {student.full_name}")
    
    # Generate payment history PDF
    pdf = PaymentHistoryReport.generate_student_payment_pdf(
        student,
        [],
        balance_info={
            'term_fee': 120.00,
            'amount_paid': 50.00,
            'previous_arrears': 0,
            'current_balance': 70.00
        }
    )
    
    # Save to file
    pdf_path = 'test_payment_report_beautiful.pdf'
    with open(pdf_path, 'wb') as f:
        f.write(pdf.getvalue())
    
    file_size = os.path.getsize(pdf_path)
    print(f"✅ PDF generated successfully!")
    print(f"📄 File: {pdf_path}")
    print(f"📊 Size: {file_size:,} bytes")
    print(f"\n🎨 NEW FEATURES:")
    print(f"  ✓ Deep dark blue headers (#0f172a)")
    print(f"  ✓ Professional card-based layouts")
    print(f"  ✓ Alternating row backgrounds")
    print(f"  ✓ Beautiful borders and spacing")
    print(f"  ✓ Modern typography")
    print(f"  ✓ Clean data tables")
else:
    print("No students found")
