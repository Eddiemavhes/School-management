"""
Custom middleware to handle session errors gracefully
"""

import logging
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class SessionErrorHandlerMiddleware:
    """
    Middleware that catches and logs session-related errors without crashing requests.
    This handles cases where sessions might be deleted during concurrent requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Check if this is a session-related error
            error_str = str(e)
            if 'session' in error_str.lower() or 'SessionInterrupted' in str(type(e).__name__):
                logger.warning(
                    f"Session error during {request.method} {request.path}: {error_str}. "
                    "User will be re-authenticated on next request."
                )
                # Clear the session to force re-authentication
                if hasattr(request, 'session'):
                    try:
                        request.session.flush()
                    except Exception as flush_err:
                        logger.warning(f"Failed to flush session: {flush_err}")
                
                # Return a safe response
                return HttpResponse(
                    "Session error. Please refresh and log in again.",
                    status=302,
                    headers={'Location': '/login/'}
                )
            else:
                # Re-raise non-session errors
                raise

