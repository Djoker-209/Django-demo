# Concept: MIDDLEWARE
# Django calls middleware in ORDER (top-down on request, bottom-up on response).
# Each middleware can:
#   process_request(request)            → runs BEFORE the view
#   process_response(request, response) → runs AFTER the view
#   process_exception(request, exception) → runs if view raises an exception

import time
import logging
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Logs method, path, status code, duration, and username for EVERY request.
    Written to settings.LOG_FILE and Python's logging system.
    """

    def process_request(self, request):
        # Hook: called before the view
        # Attach a start timestamp to the request object
        request._start_time = time.monotonic()

    def process_response(self, request, response):
        # Hook: called after the view returns
        duration_ms = 0
        if hasattr(request, '_start_time'):
            duration_ms = (time.monotonic() - request._start_time) * 1000

        line = (
            f"{request.method} {request.path} "
            f"→ {response.status_code} "
            f"[{duration_ms:.1f}ms] "
            f"user={getattr(request.user, 'username', 'anonymous')}"
        )

        # Write to log file
        try:
            with open(settings.LOG_FILE, 'a') as f:
                f.write(line + '\n')
        except Exception:
            pass  # never crash the app because of a logging failure

        logger.info(line)
        return response


class CustomErrorMiddleware(MiddlewareMixin):
    """
    Catches unhandled exceptions.
    Returns JSON for API clients (Accept: application/json),
    re-raises for HTML clients (Django's 500 handler takes over).
    """

    def process_exception(self, request, exception):
        if request.headers.get('Accept') == 'application/json':
            logger.exception("Unhandled exception on %s", request.path)
            return JsonResponse(
                {'error': 'Internal server error', 'detail': str(exception)},
                status=500,
            )
        return None  # let Django handle it normally


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Injects extra security headers into every response.
    Add this to MIDDLEWARE in settings.py if you want it active.
    """

    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options']        = 'DENY'
        response['Referrer-Policy']        = 'strict-origin-when-cross-origin'
        return response