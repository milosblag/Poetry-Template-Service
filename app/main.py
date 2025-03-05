"""
Main FastAPI application module.
"""
import time
import socket
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Local imports
from app.core.config import get_settings
from app.utils.logging import configure_logging
from app.utils.exceptions import UnicornException, unicorn_exception_handler, generic_exception_handler
from app.api.middleware.security import add_process_time_header
from app.api.router import api_router

# Configure logging
logger = configure_logging()

# Load settings
settings = get_settings()

# Application state
startup_time = time.time()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def find_available_port(start_port: int, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((settings.HOST, port))
                return port
        except OSError:
            continue
    return start_port  # Fallback to original port if nothing available


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    logger.info(f"Application starting up in {settings.ENVIRONMENT} environment...")
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
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,  # Disable in production
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,  # Disable in production
    lifespan=lifespan,
    openapi_tags=[
        {"name": "root", "description": "Operations related to the root endpoint."},
        {"name": "health", "description": "Health check endpoints."}
    ]
)

# Add rate limiting exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add custom exception handlers
app.add_exception_handler(UnicornException, unicorn_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add trusted host middleware in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["api.yourdomain.com", "yourdomain.com", "localhost", "127.0.0.1"]
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


def start():
    """Start the application server."""
    port = find_available_port(settings.PORT)
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=port,
        reload=settings.RELOAD,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    start() 