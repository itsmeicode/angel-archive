from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

from app.config.settings import get_settings

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)


def is_rate_limit_disabled() -> bool:
    """Check if rate limiting should be disabled (dev mode)"""
    return settings.disable_rate_limit or settings.is_development


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests from this IP, please try again later.",
            "retryAfter": "15 minutes",
        },
    )


# Rate limit constants for different endpoint types
GENERAL_LIMIT = "100/15minutes"
AUTH_LIMIT = "5/15minutes"
MODIFICATION_LIMIT = "30/15minutes"
READ_LIMIT = "200/15minutes"
