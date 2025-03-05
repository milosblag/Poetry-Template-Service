"""
Security and processing time middleware.
"""
import time
from fastapi import Request, Response
from app.core.config import get_settings

# Get settings
settings = get_settings()


async def add_process_time_header(request: Request, call_next):
    """Add processing time and security headers to response."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Enhanced security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Only use relaxed CSP in development mode for Swagger UI to work
    if settings.ENVIRONMENT == "development":
        # Allow resources needed for Swagger UI and ReDoc
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net blob:; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "img-src 'self' https://fastapi.tiangolo.com data:; "
            "connect-src 'self'; "
            "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com; "
            "worker-src blob:; "
            "frame-ancestors 'none';"
        )
    else:
        # Strict CSP for production
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
    
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    return response 