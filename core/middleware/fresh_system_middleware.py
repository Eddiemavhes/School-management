"""
Middleware to detect fresh system state (no school details configured)
"""
from django.utils.deprecation import MiddlewareMixin
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
        """Check if system is fresh on each request"""
        try:
            # Check if any SchoolDetails exist
            if SchoolDetails.objects.count() == 0:
                request.is_fresh_system = True
                request.fresh_system_reason = "No school details configured"
                return None
            
            # Get the default/primary school details
            school = SchoolDetails.get_or_create_default()
            
            # Check if school details are still in default state
            is_fresh = (
                school.school_name == self.DEFAULT_SCHOOL_NAME and
                school.school_motto == self.DEFAULT_SCHOOL_MOTTO and
                school.school_code == self.DEFAULT_SCHOOL_CODE
            )
            
            request.is_fresh_system = is_fresh
            if is_fresh:
                request.fresh_system_reason = "School details not customized"
            else:
                request.fresh_system_reason = None
                
        except Exception:
            # If anything goes wrong, assume system is not fresh
            request.is_fresh_system = False
            request.fresh_system_reason = None
        
        return None
