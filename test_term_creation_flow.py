#!/usr/bin/env python
"""
Comprehensive test of term creation flow:
1. Login with admin@admin.com / AdminPassword123
2. POST term data to /settings/terms/create/
3. Verify terms are saved to database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import AcademicTerm, TermFee, AcademicYear
from datetime import datetime, timedelta

User = get_user_model()
client = Client()

print("\n" + "="*70)
print("🧪 TESTING TERM CREATION FLOW")
print("="*70)

# Step 1: Verify admin account exists
print("\n[1] Checking admin account...")
try:
    admin = User.objects.get(email='admin@admin.com')
    print(f"✓ Admin found: {admin.email}")
    print(f"  - is_active: {admin.is_active}")
    print(f"  - is_staff: {admin.is_staff}")
    print(f"  - is_superuser: {admin.is_superuser}")
except User.DoesNotExist:
    print("✗ Admin not found")
    exit(1)

# Step 2: Test login
print("\n[2] Testing login...")
login_success = client.login(username='admin@admin.com', password='AdminPassword123')
if login_success:
    print("✓ Login successful")
else:
    print("✗ Login failed")
    exit(1)

# Step 3: Verify active year
print("\n[3] Checking for active academic year...")
active_year = AcademicYear.objects.filter(is_active=True).first()
if not active_year:
    print("✗ No active academic year - creating one...")
    active_year = AcademicYear.objects.create(
        year=2025,
        start_date='2025-01-01',
        end_date='2025-12-31',
        is_active=True
    )
    print(f"✓ Created year {active_year.year}")
else:
    print(f"✓ Active year: {active_year.year}")

# Step 4: Clear existing terms for this year
print("\n[4] Clearing existing terms...")
AcademicTerm.objects.filter(academic_year=active_year.year).delete()
TermFee.objects.filter(term__academic_year=active_year.year).delete()
print("✓ Cleared")

# Step 5: POST term data
print("\n[5] Posting term data to /settings/terms/create/...")
today = datetime.now().date()
term_data = {
    'term_1_start': '2025-01-15',
    'term_1_end': '2025-03-31',
    'term_1_fee': '1000',
    'term_1_current': 'on',
    
    'term_2_start': '2025-04-01',
    'term_2_end': '2025-06-30',
    'term_2_fee': '1200',
    
    'term_3_start': '2025-07-01',
    'term_3_end': '2025-09-30',
    'term_3_fee': '950',
}

response = client.post('/settings/terms/create/', term_data)
print(f"  Status code: {response.status_code}")
print(f"  Redirect URL: {response.url if hasattr(response, 'url') else 'N/A'}")

# Step 6: Check if terms were created
print("\n[6] Checking database for created terms...")
terms = AcademicTerm.objects.filter(academic_year=active_year.year).order_by('term')
print(f"  Terms found: {terms.count()}")

if terms.count() > 0:
    for term in terms:
        print(f"\n  ✓ Term {term.term}:")
        print(f"    - Start: {term.start_date}")
        print(f"    - End: {term.end_date}")
        print(f"    - Is Current: {term.is_current}")
        fee = TermFee.objects.filter(term=term).first()
        if fee:
            print(f"    - Fee: ${fee.amount}")
else:
    print("  ✗ No terms found - POST may have failed silently")

# Step 7: Summary
print("\n" + "="*70)
success = terms.count() == 3
if success:
    print("✅ SUCCESS: All 3 terms were created and saved!")
else:
    print(f"❌ FAILURE: Expected 3 terms, got {terms.count()}")
print("="*70 + "\n")
