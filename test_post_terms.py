#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','school_management.settings')
django.setup()

from django.test import Client
from core.models import Administrator, AcademicTerm, TermFee, AcademicYear

# Set admin password to known value
admin = Administrator.objects.filter(email='admin@admin.com').first()
if not admin:
    print('No admin user found')
    exit(1)
admin.set_password('testpass123')
admin.save()
print('Admin password set to testpass123')

c = Client()
logged_in = c.login(username='admin@admin.com', password='testpass123')
print('Logged in:', logged_in)

# Ensure active year exists
year = AcademicYear.objects.filter(is_active=True).first()
print('Active year:', year.year if year else None)

post_data = {
    'term_1_start':'2026-01-01',
    'term_1_end':'2026-03-31',
    'term_1_fee':'1500',
    'term_1_current':'on',
    'term_2_start':'2026-04-01',
    'term_2_end':'2026-08-31',
    'term_2_fee':'1600',
    'term_3_start':'2026-09-01',
    'term_3_end':'2026-12-31',
    'term_3_fee':'1700'
}

# Provide a valid Host header to avoid DisallowedHost during tests
resp = c.post('/settings/terms/create/', post_data, follow=True, HTTP_HOST='127.0.0.1')
print('POST status code:', resp.status_code)
print('Redirect chain:', resp.redirect_chain)

terms = AcademicTerm.objects.filter(academic_year=year.year)
print('Terms count after post:', terms.count())
for t in terms:
    print('Term', t.term, t.start_date, t.end_date, 'current=', t.is_current)
    fee = TermFee.objects.filter(term=t).first()
    print('  fee:', fee.amount if fee else 'None')
