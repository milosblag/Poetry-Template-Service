from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import uvicorn
import logging
import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import socket

load_dotenv()

# --- Configuration ---
# Use environment variables for configuration, with defaults for development
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))  # Use single PORT variable
RELOAD = os.getenv("RELOAD", "False").lower() == "true" 
WORKERS = int(os.getenv("WORKERS", "4"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Configure logging
def configure_logging():
    """Configures the root logger."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log"),
        ]
    )
configure_logging()
logger = logging.getLogger(__name__)

# Port finding only happens in main process execution, not during imports
def find_available_port(start_port: int, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, port))
                return port
        except OSError:
            continue
    return start_port  # Fallback to original port if nothing available

# --- Pydantic Models ---
class Message(BaseModel):
    """Response model for the root endpoint."""
    message: str = Field(..., example="Hello world!")  # "..." makes it required, example for docs


# --- Initialize FastAPI app ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    logger.info("Application starting up...")
    # Example: Connect to a database, load a machine learning model, etc.
    yield
    logger.info("Application shutting down...")
    # Example: Close database connections

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Hello World API",
    description="A simple API that returns Hello World",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "root", "description": "Operations related to the root endpoint."}
    ]  # Add tags for better organization in documentation
)

# --- Middleware ---
# Configure CORS (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Use the configured list of origins
    allow_credentials=True,
    allow_methods=["GET"],  # Only allow specific methods, * is dangerous
    allow_headers=["*"],   # Be specific with headers in production
)

# --- Exception Handling ---
class UnicornException(Exception):
    """Custom exception type."""
    def __init__(self, message: str):
        self.message = message

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request, exc: UnicornException):
    """Custom exception handler for UnicornException."""
    logger.error(f"UnicornException: {exc.message}")  # Log the error
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.message}"},
    )

# --- Routes ---
@app.get("/", response_model=Message, tags=["root"], status_code=status.HTTP_200_OK)
async def read_root():
    """
    Root endpoint that returns a Hello World message.

    Returns:
        Message:  Pydantic model. A dictionary containing the message
    """
    try:
        logger.info("Processing request to root endpoint")
        
        return {"message": "Hello world!"}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)  # Log with traceback
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# --- Main Entry Point ---
if __name__ == "__main__":
    # Only find available port when running the script directly
    run_port = find_available_port(PORT)
    if run_port != PORT:
        logger.info(f"Port {PORT} is in use, using port {run_port} instead")
    else:
        logger.info(f"Using port: {run_port}")
        
    uvicorn.run(
        "main:app",
        host=HOST,
        port=run_port,  # Use the port we found
        reload=RELOAD,
        workers=WORKERS if not RELOAD else 1,  # Workers are ignored in reload mode
        log_level=LOG_LEVEL.lower()
    )