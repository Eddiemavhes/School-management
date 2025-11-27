#!/usr/bin/env python
"""
Test script to simulate form submission
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.test import Client
from core.models import AcademicYear, AcademicTerm
from django.contrib.auth import authenticate

# Create a test client
client = Client()

# First, login
print("Logging in...")
login_success = client.login(username='admin@admin.com', password='your_password_here')
if not login_success:
    print("❌ Login failed - trying with a different password")
    # Try default Django admin credentials
    login_success = client.login(username='admin@admin.com', password='admin123')
    if not login_success:
        print("❌ Login failed - please update the password in this script")
        exit(1)

print("✓ Logged in successfully")

# Prepare the form data
form_data = {
    'csrfmiddlewaretoken': client.cookies.get('csrftoken', ''),
    'term_1_start': '2026-01-01',
    'term_1_end': '2026-03-31',
    'term_1_fee': '1000',
    'term_1_current': 'on',
    'term_2_start': '2026-04-01',
    'term_2_end': '2026-08-31',
    'term_2_fee': '1000',
    'term_3_start': '2026-09-01',
    'term_3_end': '2026-12-31',
    'term_3_fee': '1000',
}

print(f"\nSubmitting form data: {form_data}")

# Submit the form
response = client.post('/settings/terms/create/', form_data)

print(f"\nResponse status: {response.status_code}")
print(f"Redirect URL: {response.url if response.status_code in [301, 302] else 'N/A'}")

# Check the database
print("\n" + "=" * 60)
print("CHECKING DATABASE")
print("=" * 60)

terms = AcademicTerm.objects.all()
print(f"\nAcademic Terms created: {terms.count()}")
for t in terms:
    print(f"  - Term {t.term} {t.academic_year}: {t.start_date} to {t.end_date} (Current={t.is_current})")
