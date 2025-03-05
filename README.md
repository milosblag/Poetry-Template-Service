# Hello World API

A production-ready FastAPI Hello World API with proper configuration and best practices.

## Features

- ✅ API versioning with backward compatibility
- ✅ Comprehensive health checks with system metrics (CPU, memory, disk)
- ✅ Rate limiting to prevent abuse
- ✅ Enhanced security headers with CSP and permissions policies
- ✅ Proper configuration management with environment variables
- ✅ Production-ready logging with rotation
- ✅ Graceful error handling and detailed debugging (dev only)
- ✅ Docker and Docker Compose support
- ✅ Gunicorn for production deployment
- ✅ Response compression for better performance
- ✅ Structured error reporting with error IDs

## Project Structure

```
.
├── config.py            # Configuration management
├── Dockerfile           # Container definition
├── docker-compose.yml   # Container orchestration
├── gunicorn_conf.py     # Production server config
├── health.py            # Enhanced health checks
├── main.py              # Application entry point
├── poetry.lock          # Dependency lock file
├── pyproject.toml       # Poetry package definition
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.11+
- Poetry for dependency management

```bash
# Install poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

## Running the Application

### For Development:

```bash
# Run with auto-reload
poetry run python main.py
```

### For Production:

```bash
# Using Poetry and Gunicorn
poetry run gunicorn -k uvicorn.workers.UvicornWorker -c gunicorn_conf.py main:app

# Using Docker
docker-compose up -d
```

## Environment Variables

Create a `.env` file with the following variables:

```
# Server settings
HOST=0.0.0.0           # Host to bind to
PORT=8000              # Port to bind to
RELOAD=False           # Auto-reload on code changes (development only)
WORKERS=4              # Number of worker processes

# Environment settings
ENVIRONMENT=production        # 'development' or 'production'
LOG_LEVEL=info               # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_FILE=app.log             # Log file path
LOG_MAX_SIZE=10485760        # Max log file size in bytes (10MB)
LOG_BACKUP_COUNT=5           # Number of log files to keep

# CORS settings
ALLOWED_ORIGINS=https://yourdomain.com  # Comma-separated list of allowed origins

# API settings
API_VERSION=v1               # API version prefix

# Rate limiting
RATE_LIMIT_GENERAL=100/minute # Rate limit for general endpoints
```

## API Documentation

In development mode, you can access:
- API documentation at: http://localhost:8000/docs
- Alternative documentation at: http://localhost:8000/redoc

In production mode, these endpoints are disabled for security.

## API Endpoints

- Hello World: 
  - New: http://localhost:8000/api/v1/
  - Legacy: http://localhost:8000/
  
- Health Check: 
  - New: http://localhost:8000/api/v1/health
  - Legacy: http://localhost:8000/health

## Health Check Response

The health check endpoint returns detailed information about the service:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "uptime_human": "1h",
  "system": {
    "process_id": 1234,
    "hostname": "server1",
    "cpu_usage": 12.5,
    "memory_usage": 35.2,
    "disk_usage": 42.7
  }
}
```

## Docker Deployment

The application includes Docker support for easy deployment:

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

## Security Features

- **Rate Limiting**: Prevents abuse by limiting request frequency
- **Security Headers**:
  - Content-Security-Policy: Prevents XSS and data injection attacks
  - X-Content-Type-Options: Prevents MIME type sniffing
  - X-Frame-Options: Prevents clickjacking
  - X-XSS-Protection: Additional XSS protection
  - Referrer-Policy: Controls referrer information
  - Permissions-Policy: Controls browser features
  - Strict-Transport-Security: Enforces HTTPS (production only)
- **Trusted Hosts**: Prevents host header attacks in production
- **Response Compression**: Improves performance and reduces bandwidth

## Error Handling

The application includes comprehensive error handling:

- Custom exception types with dedicated handlers
- Automatic error ID generation for traceability
- Detailed error information in development mode
- Production-safe error responses without sensitive details
- Error logging with full tracebacks for debugging 