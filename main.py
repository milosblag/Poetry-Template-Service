from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import uvicorn
import logging
import socket
import time
from logging.handlers import RotatingFileHandler
import traceback
from contextlib import asynccontextmanager
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field

# Local imports
from config import get_settings
import health

# Load settings
settings = get_settings()

# --- Configure logging ---
def configure_logging():
    """Configure application logging with rotation."""
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.LOG_LEVEL)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_SIZE,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(settings.LOG_LEVEL)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(process)d] - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

logger = configure_logging()

# --- Port finding logic ---
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

# --- Pydantic Models ---
class Message(BaseModel):
    """Response model for the root endpoint."""
    message: str = Field(..., example="Hello world!")

# --- Application state ---
startup_time = time.time()

# --- Initialize rate limiter ---
limiter = Limiter(key_func=get_remote_address)

# --- Initialize FastAPI app ---
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
    version="1.0.0",
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

# --- Middleware ---
# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add trusted host middleware in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["api.yourdomain.com", "yourdomain.com"]
    )

# Process time and security headers middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add processing time to response headers."""
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
        # Allow resources needed for Swagger UI
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' https://fastapi.tiangolo.com data:; "
            "connect-src 'self'; "
            "font-src 'self' https://cdn.jsdelivr.net; "
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET"],  # Restrict to necessary methods
    allow_headers=["Content-Type", "Authorization"],  # Be specific
)

# --- Exception Handling ---
class UnicornException(Exception):
    """Custom exception type."""
    def __init__(self, message: str):
        self.message = message

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request, exc: UnicornException):
    """Custom exception handler for UnicornException."""
    logger.error(f"UnicornException: {exc.message}")
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.message}"},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
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

# --- Routes ---
# Define API version prefix
API_PREFIX = f"/api/{settings.API_VERSION}"

@app.get(f"{API_PREFIX}/", response_model=Message, tags=["root"], status_code=status.HTTP_200_OK)
@limiter.limit(settings.RATE_LIMIT_GENERAL)
async def read_root(request: Request):
    """
    Root endpoint that returns a Hello World message.

    Returns:
        Message: Pydantic model. A dictionary containing the message
    """
    try:
        logger.info("Processing request to root endpoint")
        return {"message": "Hello world!"}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# Keep original route for backward compatibility
@app.get("/", response_model=Message, tags=["root"], status_code=status.HTTP_200_OK)
@limiter.limit(settings.RATE_LIMIT_GENERAL)
async def read_root_legacy(request: Request):
    return await read_root(request)

@app.get(f"{API_PREFIX}/health", response_model=health.ServiceHealth, tags=["health"])
@limiter.limit(settings.RATE_LIMIT_GENERAL)
async def health_check(request: Request):
    """
    Enhanced health check endpoint to verify service status.
    
    Returns:
        ServiceHealth: Comprehensive information about service health and uptime
    """
    return health.get_service_health(version="1.0.0")

# Keep original health route for backward compatibility
@app.get("/health", response_model=health.ServiceHealth, tags=["health"])
@limiter.limit(settings.RATE_LIMIT_GENERAL)
async def health_check_legacy(request: Request):
    return await health_check(request)

# --- Main Entry Point ---
if __name__ == "__main__":
    # Only find available port when running the script directly
    run_port = find_available_port(settings.PORT)
    if run_port != settings.PORT:
        logger.info(f"Port {settings.PORT} is in use, using port {run_port} instead")
    else:
        logger.info(f"Using port: {run_port}")
        
    uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
    uvicorn_log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(name)s - %(levelname)s - [%(process)d] - %(client_addr)s - %(request_line)s - %(status_code)s"
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=run_port,
        reload=settings.RELOAD,
        workers=settings.WORKERS if not settings.RELOAD else 1,
        log_level=settings.LOG_LEVEL.lower(),
        log_config=uvicorn_log_config
    )