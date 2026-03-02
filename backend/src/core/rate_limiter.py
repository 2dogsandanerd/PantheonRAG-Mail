from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please wait before making more requests.",
            "retry_after": exc.detail,
        },
    )


RATE_LIMITS = {
    "ingest": "10/minute",
    "chat": "60/minute",
    "email": "30/minute",
    "default": "100/minute",
}
