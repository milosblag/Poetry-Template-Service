"""
Health check API endpoints.
"""

import logging
from typing import cast

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.health import BasicHealth, get_basic_health

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

@router.get(f"{API_PREFIX}/health", response_model=BasicHealth)
@limiter.limit(settings.RATE_LIMIT_GENERAL)
async def health_check(request: Request) -> BasicHealth:
    """
    Basic health check endpoint to verify service status.

    Returns:
        BasicHealth: Simple status information for public access
    """
    logger.debug("Basic health check requested")
    return get_basic_health()

# Keep original route for backward compatibility
@router.get("/health", response_model=BasicHealth)
@limiter.limit(settings.RATE_LIMIT_GENERAL)
async def health_check_legacy(request: Request) -> BasicHealth:
    """Legacy health check endpoint for backward compatibility."""
    result = await health_check(request)
    return cast(BasicHealth, result)
