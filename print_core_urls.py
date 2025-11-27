import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','school_management.settings')
import django
django.setup()
import core.urls as u
print([p.name for p in u.urlpatterns])
print(len(u.urlpatterns))
for p in u.urlpatterns:
    print(repr(p))
