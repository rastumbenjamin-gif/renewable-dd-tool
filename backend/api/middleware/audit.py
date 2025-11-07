"""
Audit logging middleware
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import structlog
import time

logger = structlog.get_logger()


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for audit purposes"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        response = await call_next(request)

        # Log response
        duration = time.time() - start_time
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )

        return response
