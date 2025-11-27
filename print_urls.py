import os
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
import django
django.setup()
from django.urls import get_resolver
raw = list(get_resolver().reverse_dict.keys())
names = [str(k) for k in raw if k]
print(json.dumps(sorted(names), indent=2))
