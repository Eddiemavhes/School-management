#!/usr/bin/env python
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

# Test the API directly
url = "http://127.0.0.1:8000/api/student-balance/64/"
print("Testing API: GET " + url)
print("=" * 60)

try:
    response = requests.get(url)
    data = response.json()
    
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    for key, value in data.items():
        if key == 'student_name':
            print(f"  Student: {value}")
        elif key == 'total_outstanding':
            print(f"  ✓ total_outstanding: ${value}")
        elif key == 'current_balance':
            print(f"  current_balance: ${value}")
        elif key == 'term_fee':
            print(f"  term_fee: ${value}")
        elif key == 'payment_priority':
            print(f"  payment_priority: {value}")
    
    print(f"\n{'✓ SUCCESS' if data.get('total_outstanding') == 1080.0 else '✗ FAILED'}")
    print(f"Expected total_outstanding: $1080.00")
    print(f"Actual total_outstanding: ${data.get('total_outstanding')}")
    
except Exception as e:
    print(f"Error: {e}")
