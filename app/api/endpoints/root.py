"""
Root API endpoints.
"""

import logging
from typing import cast

from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.models.basic import Message

# Get settings
settings = get_settings()

# Configure logger
logger = logging.getLogger(__name__)

# Set up rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter()

# API version prefix
API_PREFIX = f"/api/{settings.API_VERSION}"


@router.get(
    f"{API_PREFIX}/",
    response_model=Message,
    status_code=status.HTTP_200_OK
)
@limiter.limit(settings.RATE_LIMIT_GENERAL)
async def read_root(request: Request) -> dict[str, str]:
    """
    Root endpoint that returns a Hello World message.

    Returns:
        Message: Pydantic model. A dictionary containing
        the message
    """
    try:
        logger.info("Processing request to root endpoint")
        return {"message": "Hello world!"}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
