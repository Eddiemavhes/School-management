import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from django.urls import get_resolver

resolver = get_resolver()

def print_urls(patterns, prefix=''):
    for pattern in patterns:
        full_path = prefix + str(pattern.pattern)
        if 'api' in full_path or 'payment' in full_path or 'student' in full_path:
            name = getattr(pattern, 'name', 'unnamed')
            print(f'{full_path} -> {name}')
        
        if hasattr(pattern, 'url_patterns'):
            print_urls(pattern.url_patterns, full_path)

print('=== API and Student/Payment URLs ===')
print_urls(resolver.url_patterns)
