"""
Middleware to detect fresh system state (no school details configured)
"""
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from core.models.school_details import SchoolDetails


class FreshSystemMiddleware(MiddlewareMixin):
    """
    Detects when the system is "fresh" (no school details have been configured).
    Sets request.is_fresh_system to True/False based on SchoolDetails state.
    """
    
    # Default values that indicate a fresh system
    DEFAULT_SCHOOL_NAME = "Your School Name"
    DEFAULT_SCHOOL_MOTTO = "Quality Education for All"
    DEFAULT_SCHOOL_CODE = "SCH001"
    
    def process_request(self, request):
        """Check if system is fresh on each request.

        Cached to avoid hitting the database on every request. Uses
        Django's cache (locmem by default) with a short TTL.
        """
        try:
            cached = cache.get('is_fresh_system')
            if cached is not None:
                request.is_fresh_system = cached.get('value', False)
                request.fresh_system_reason = cached.get('reason')
                return None

            # Use .exists() instead of .count() to avoid full COUNT scan
            if not SchoolDetails.objects.exists():
                request.is_fresh_system = True
                request.fresh_system_reason = "No school details configured"
                cache.set('is_fresh_system', {'value': True, 'reason': request.fresh_system_reason}, 30)
                return None

            # Get the default/primary school details (may create if missing)
            school = SchoolDetails.get_or_create_default()

            # Check if school details are still in default state
            is_fresh = (
                school.school_name == self.DEFAULT_SCHOOL_NAME and
                school.school_motto == self.DEFAULT_SCHOOL_MOTTO and
                school.school_code == self.DEFAULT_SCHOOL_CODE
            )

            request.is_fresh_system = is_fresh
            request.fresh_system_reason = "School details not customized" if is_fresh else None

            # Cache result briefly (30s) to avoid DB queries per-request
            cache.set('is_fresh_system', {'value': is_fresh, 'reason': request.fresh_system_reason}, 30)

        except Exception:
            # If anything goes wrong, assume system is not fresh
            request.is_fresh_system = False
            request.fresh_system_reason = None

        return None
