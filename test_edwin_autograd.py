import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from decimal import Decimal
from core.models import Student
from core.models.academic import Payment, AcademicTerm
from core.models.fee import StudentBalance

print("=== TESTING EDWIN'S AUTO-GRADUATION ===\n")

edwin = Student.objects.filter(first_name='Edwin').first()
if not edwin:
    print("Edwin not found!")
    exit()

print(f"Before payment:")
print(f"  Edwin's balance: ${edwin.overall_balance}")
print(f"  Edwin's status: {edwin.status}")
print(f"  Edwin's is_active: {edwin.is_active}\n")

# Get the latest term with balance
latest_balance = StudentBalance.objects.filter(student=edwin).order_by('-term__academic_year', '-term__term').first()
if not latest_balance:
    print("No balance found!")
    exit()

print(f"Latest balance: {latest_balance.term} = ${latest_balance.current_balance}")
print(f"Creating payment of ${latest_balance.current_balance}...\n")

# Create payment to clear the balance
try:
    # Get admin user for recorded_by
    from core.models import Administrator
    admin = Administrator.objects.first()
    
    payment = Payment.objects.create(
        student=edwin,
        term=latest_balance.term,
        amount=Decimal(str(latest_balance.current_balance)),
        payment_method='CASH',
        receipt_number='AUTO-GRAD-TEST-001',
        reference_number='Auto-graduation test',
        recorded_by=admin
    )
    print(f"✅ Payment created: ID={payment.id}, Amount=${payment.amount}")
except Exception as e:
    print(f"❌ Error creating payment: {e}")
    import traceback
    traceback.print_exc()
    exit()

# Refresh to get updated values
edwin.refresh_from_db()

print(f"\nAfter payment:")
print(f"  Edwin's balance: ${edwin.overall_balance}")
print(f"  Edwin's status: {edwin.status}")
print(f"  Edwin's is_active: {edwin.is_active}")
print(f"  Edwin's is_archived: {edwin.is_archived}")

if edwin.status == 'GRADUATED' and not edwin.is_active and edwin.is_archived:
    print(f"\n✅✅✅ SUCCESS! Edwin auto-graduated to Alumni!")
else:
    print(f"\n❌ Auto-graduation did not trigger")
