from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from fastapi import Request
from fastapi.responses import JSONResponse
from app.schema.response import ApiResponse

limiter = Limiter(key_func=get_remote_address)

async def rate_limit_custom_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content=ApiResponse(
            success=False,
            message="Too Many Requests , Limit Exceeded",
            error=str(exc)).model_dump(exclude={"data"})
    )


def _rate_limit_exceeded_handle(app):
    global limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_custom_handler)
    app.add_middleware(SlowAPIMiddleware)