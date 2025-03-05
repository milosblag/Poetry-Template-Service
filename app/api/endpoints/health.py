"""
Health check API endpoints.
"""
import logging
from fastapi import APIRouter, Request
from app.core.health import get_service_health, ServiceHealth
from app.core.config import get_settings
from slowapi import Limiter
from slowapi.util import get_remote_address

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
    f"{API_PREFIX}/health", 
    response_model=ServiceHealth
)
@limiter.limit(settings.RATE_LIMIT_GENERAL)
async def health_check(request: Request):
    """
    Enhanced health check endpoint to verify service status.
    
    Returns:
        ServiceHealth: Comprehensive information about service health and uptime
    """
    logger.debug("Health check requested")
    return get_service_health(version=settings.VERSION)


# Keep original route for backward compatibility
@router.get(
    "/health", 
    response_model=ServiceHealth
)
@limiter.limit(settings.RATE_LIMIT_GENERAL)
async def health_check_legacy(request: Request):
    """Legacy health check endpoint for backward compatibility."""
    return await health_check(request) 