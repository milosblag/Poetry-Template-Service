"""
Exception handling utilities.
"""
import time
import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings

# Get settings and logger
settings = get_settings()
logger = logging.getLogger(__name__)


class UnicornException(Exception):
    """Custom exception type."""
    def __init__(self, message: str):
        self.message = message


async def unicorn_exception_handler(request: Request, exc: UnicornException):
    """Custom exception handler for UnicornException."""
    logger.error(f"UnicornException: {exc.message}")
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.message}"},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Generic exception handler for unhandled exceptions."""
    error_id = f"error-{time.time()}"
    logger.error(f"Unhandled exception {error_id}: {str(exc)}")
    logger.error(traceback.format_exc())
    
    # In production, don't expose details
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error_id": error_id}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "error_id": error_id,
                "detail": str(exc),
                "traceback": traceback.format_exc()
            }
        ) 