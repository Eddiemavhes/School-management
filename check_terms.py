#!/usr/bin/env python
import os
import sys
import django

os.chdir(r'c:\Users\Admin\Desktop\School management')
sys.path.insert(0, r'c:\Users\Admin\Desktop\School management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from core.models import AcademicTerm

print("=" * 80)
print("CHECKING ACADEMIC TERMS")
print("=" * 80)
print()

terms = AcademicTerm.objects.all().order_by('academic_year', 'term')
for t in terms:
    print(f"{t}: is_current={t.is_current}")

print()

# Check if Term 3 exists for 2026
term3_2026 = AcademicTerm.objects.filter(academic_year=2026, term=3).first()
if term3_2026:
    print(f"✓ Third Term 2026 EXISTS")
    print(f"  is_current: {term3_2026.is_current}")
else:
    print(f"❌ Third Term 2026 DOES NOT EXIST")
