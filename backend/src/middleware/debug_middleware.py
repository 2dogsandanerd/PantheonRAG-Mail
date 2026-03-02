"""
Lean Debug Middleware
Tracks requests and detects problems (warnings/errors only).
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.crash_detector import crash_detector
import time
from loguru import logger


class DebugMiddleware(BaseHTTPMiddleware):
    """Minimal debug middleware - tracks requests and performance."""

    async def dispatch(self, request: Request, call_next):
        # Track request
        crash_detector.track_request(
            method=request.method,
            path=request.url.path,
            params=dict(request.query_params)
        )

        # Measure request duration
        start_time = time.time()

        try:
            response = await call_next(request)

            # Warn if slow
            duration = time.time() - start_time
            if duration > 5.0:  # 5 seconds threshold
                logger.warning(
                    f"SLOW REQUEST: {request.method} {request.url.path} took {duration:.2f}s"
                )

            return response

        except Exception as e:
            # Log error
            logger.error(
                f"REQUEST FAILED: {request.method} {request.url.path} - {type(e).__name__}: {e}"
            )

            # Log crash
            crash_detector.log_crash(e, {
                "request_method": request.method,
                "request_path": str(request.url.path),
                "request_params": dict(request.query_params)
            })

            raise
