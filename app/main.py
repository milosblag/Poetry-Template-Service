"""
Main FastAPI application module.
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, cast
from typing import Callable

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import Response
from starlette.requests import Request

from app.api.middleware.security import add_process_time_header
from app.api.router import api_router

# Local imports
from app.core.config import get_settings
from app.utils.exceptions import (
    UnicornException,
    generic_exception_handler,
    unicorn_exception_handler,
)
from app.utils.logging import configure_logging

# Configure logging
logger = configure_logging()

# Load settings
settings = get_settings()

# Application state
startup_time = time.time()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifecycle manager for the FastAPI application."""
    logger.info(
        f"Application starting up in {settings.ENVIRONMENT} environment..."
    )
    # Here you would initialize resources like database connections
    try:
        # Example: initialize resources
        yield
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        raise
    finally:
        logger.info("Application shutting down...")
        # Example: close database connections, cleanup resources


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Hello World API",
    description="A simple API that returns Hello World",
    version=settings.VERSION,
    docs_url=(
        "/docs" if settings.ENVIRONMENT != "production" else None
    ),  # Disable in production
    redoc_url=(
        "/redoc" if settings.ENVIRONMENT != "production" else None
    ),  # Disable in production
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "root",
            "description": "Operations related to the root endpoint."
        },
        {
            "name": "health",
            "description": "Health check endpoints."
        },
    ],
)

# Add rate limiting exception handler
app.state.limiter = limiter

# Cast to the expected callable type for FastAPI exception handlers
app.add_exception_handler(
    RateLimitExceeded,
    cast(
        'Callable[[Request, Exception], Response]',
        _rate_limit_exceeded_handler
    )
)

# Add custom exception handlers
app.add_exception_handler(
    UnicornException,
    cast(
        'Callable[[Request, Exception], Response]',
        unicorn_exception_handler
    )
)

app.add_exception_handler(
    Exception,
    cast(
        'Callable[[Request, Exception], Response]',
        generic_exception_handler
    )
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add trusted host middleware in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "api.yourdomain.com",
            "yourdomain.com",
            "localhost",
            "127.0.0.1",
        ],
    )

# Add security headers middleware
app.middleware("http")(add_process_time_header)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET"],  # Restrict to necessary methods
    allow_headers=["Content-Type", "Authorization"],  # Be specific
)

# Include all routes
app.include_router(api_router)


def start() -> None:
    """Start the application server."""
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    start()
