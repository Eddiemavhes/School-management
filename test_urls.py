#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.urls import reverse, get_resolver

# Test URL resolution
try:
    print('✅ create_academic_year:', reverse('create_academic_year'))
    print('✅ set_active_year:', reverse('set_active_year'))
except Exception as e:
    print('❌ Error:', e)
    resolver = get_resolver()
    print('\nAll URL patterns:')
    for pattern in resolver.url_patterns:
        if 'settings' in str(pattern.pattern):
            print(f"  {pattern.pattern} -> {pattern.name}")
