import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
import django
django.setup()

from core.models.academic import update_student_balance
from django.core.exceptions import RelatedObjectDoesNotExist

class FakePayment:
    def __init__(self, pk, student, amount):
        self.pk = pk
        self.student = student
        self.amount = amount

    def __getattr__(self, item):
        # Simulate missing related object for 'term'
        if item == 'term':
            raise RelatedObjectDoesNotExist('Payment has no term')
        raise AttributeError(item)

print('Running signal guard test...')

# Create a minimal fake student object with required attributes
class FakeStudent:
    def __init__(self, id):
        self.id = id

fake_student = FakeStudent(id=9999)

fake = FakePayment(pk=12345, student=fake_student, amount=100)

# Call the receiver directly - should not raise
try:
    update_student_balance(sender=None, instance=fake, created=True)
    print('PASS: update_student_balance handled missing term without raising')
except Exception as e:
    print('FAIL: update_student_balance raised:', type(e).__name__, str(e))
    raise
