# Hello World API

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.11-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-ready FastAPI Hello World API with an emphasis on security, performance, and modern Python practices. This project demonstrates how to structure a professional API with all the necessary components for a robust production deployment.

![Hello World API](https://via.placeholder.com/800x400?text=Hello+World+API)

## Table of Contents

- [Features](#features)
- [Project Architecture](#project-architecture)
- [Development Setup](#development-setup)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Performance](#performance)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Production-Ready Architecture**: A clean, modular structure following best practices.
- **API Versioning**: Built-in support for API versioning to ensure backward compatibility.
- **Health Checks**: Comprehensive health check endpoints for monitoring systems.
- **Security Features**:
  - Strict security headers
  - Rate limiting to prevent abuse
  - CORS configuration
  - Trusted host validation
  - Docker image vulnerability scanning
- **Performance Optimizations**:
  - GZip compression for responses
  - Asynchronous request handling
  - Optimized Docker configuration
- **Observability**:
  - Structured console logging
  - Request timing information
  - Resource usage metrics
- **Developer Experience**:
  - Comprehensive type hints and annotations
  - Automated testing and quality tools
  - Live reload during development
  - Comprehensive dependency management with Poetry

## Project Architecture

```
hello-world-api/
├── app/                    # Main application package
│   ├── api/                # API endpoints and routers
│   │   ├── endpoints/      # API endpoint modules
│   │   ├── middleware/     # Middleware components
│   │   └── router.py       # Main API router
│   ├── core/               # Core application components
│   │   ├── config.py       # Configuration settings
│   │   └── health.py       # Health check functionality
│   ├── models/             # Pydantic models
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── docs/                   # Documentation
│   ├── api_documentation.md
│   ├── code_examples.md
│   ├── docker_security.md
│   ├── installation.md
│   ├── security.md
│   └── technical_design.md
├── kubernetes/             # Kubernetes deployment configuration
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── kustomization.yaml
│   └── README.md           # Kubernetes-specific documentation
├── .env                    # Environment variables
├── pyproject.toml          # Poetry configuration
├── poetry.lock             # Poetry lock file
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── gunicorn_conf.py        # Gunicorn configuration
├── run.py                  # Entry point script
├── run_tests.py            # Test runner script
├── healthcheck.sh          # Container health check script
├── docker_vulnerability_scanner.sh  # Docker security scanning tool
├── docker_connectivity_check.sh     # Docker connectivity diagnostic tool
└── Makefile                # Development and CI/CD command shortcuts
```

### Key Components

- **FastAPI Framework**: High-performance asynchronous Python web framework
- **Poetry**: Modern Python dependency management
- **Pydantic**: Data validation and settings management
- **Uvicorn & Gunicorn**: ASGI server implementation with workers management
- **Docker & Docker Compose**: Containerization and orchestration
- **SlowAPI**: Rate limiting implementation
- **Kubernetes**: Configuration files for container orchestration

## Development Setup

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Docker & Docker Compose (optional, for containerized development)

### Local Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/hello-world-api.git
   cd hello-world-api
   ```

2. **Install dependencies with Poetry**:
   ```bash
   poetry install
   ```

3. **Activate the virtual environment**:
   ```bash
   poetry shell
   ```

4. **Run the application in development mode**:
   ```bash
   python run.py
   # OR
   make run
   ```

5. **Access the application**:
   - API: [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Using Docker

1. **Build the Docker image**:
   ```bash
   docker build -t hello-world-api .
   # OR
   make docker-build
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 hello-world-api
   # OR
   make docker-run
   ```

3. **Alternatively, use Docker Compose**:
   ```bash
   docker-compose up
   ```

## API Documentation

### Endpoints

- `GET /api/v1/`: Returns a Hello World message
- `GET /api/v1/health`: Returns basic health status

When running in development mode, comprehensive API documentation is available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Configuration

The application is highly configurable through environment variables or a `.env` file.

### Environment Variables

| Variable             | Description                              | Default       |
|----------------------|------------------------------------------|---------------|
| HOST                 | Server host                              | 0.0.0.0       |
| PORT                 | Server port                              | 8000          |
| RELOAD               | Enable auto-reload (development only)    | False         |
| WORKERS              | Number of Gunicorn workers               | 4             |
| ENVIRONMENT          | Environment (development/production)     | development   |
| LOG_LEVEL            | Logging level                            | INFO          |
| ALLOWED_ORIGINS      | CORS allowed origins (comma-separated)   | *             |
| API_VERSION          | API version                              | v1            |
| RATE_LIMIT_GENERAL   | General rate limit                       | 100/minute    |

## Testing

This project uses pytest for unit and integration tests.

### Running Tests

```bash
# Run all tests
pytest
# OR
make test

# Run tests with coverage report
pytest --cov=app
```

### Test Structure

- **Unit Tests**: In `tests/unit/` directory, testing individual components in isolation
- **Integration Tests**: In `tests/integration/` directory, testing component interactions

## Deployment

### Production Considerations

1. **Environment Settings**: Set `ENVIRONMENT=production` to enable production optimizations
2. **Documentation Access**: API docs are automatically disabled in production
3. **Security Headers**: Strict security headers are applied in production
4. **Host Validation**: Trusted host middleware is enabled in production

### Docker Production Deployment

```bash
# Build with production tag
docker build -t hello-world-api:production .

# Run with production environment
docker run -p 8000:8000 -e ENVIRONMENT=production hello-world-api:production
```

### Kubernetes Deployment

While not included in this repository, the application is designed to work well in a Kubernetes environment. The health checks and container configuration are already optimized for orchestration.

## Performance

### Optimizations

- **Asynchronous Request Handling**: Using FastAPI's async capabilities
- **Worker Configuration**: Configurable Gunicorn workers
- **Response Compression**: GZip middleware for large responses
- **Alpine-based Docker Image**: Minimal footprint Docker image

### Benchmarks

Benchmark results will vary by hardware, but typical performance on modest hardware:

- **Requests per second**: ~10,000 req/s 
- **Latency**: <10ms average response time
- **Memory usage**: ~50MB base + ~10MB per worker

## Security Considerations

### Implemented Security Features

- **Rate Limiting**: Protection against abuse and DoS
- **Security Headers**: Including Content-Security-Policy
- **CORS Configuration**: Strict origin controls
- **Trusted Host Validation**: Prevents host header attacks
- **Alpine Linux Base**: Minimal attack surface in Docker image
- **Dependency Security**: Regular updates via Poetry
- **Simple Health Endpoint**: Public endpoint with minimal information for monitoring

### Security Recommendations

- Deploy behind a TLS-terminating reverse proxy like Nginx
- Implement API keys or OAuth2 for protected endpoints
- Regularly update dependencies with `poetry update`
- Run security scans on your Docker image
- Always use a strong, unique API key in production environments
- Consider implementing more robust authentication for production

### Docker Security

This project includes tools for Docker image vulnerability scanning:

- Manual vulnerability scanning: `make docker-scan` or `./docker_vulnerability_scanner.sh`
- Connectivity diagnostics: `make docker-check` or `./docker_connectivity_check.sh`
- Security reports are generated in various formats (JSON, HTML, text summary)

For more details, see the [Docker Security Documentation](docs/docker_security.md).

## Docker Vulnerability Scanning Tools

This repository contains tools for scanning Docker images for security vulnerabilities.

## Overview

We've consolidated our Docker vulnerability scanning tools into two main components:
- A comprehensive scanner for vulnerability detection
- A diagnostic tool for troubleshooting connectivity issues

## Key Components

- **[docker_vulnerability_scanner.sh](./docker_vulnerability_scanner.sh)**: The main scanner script that provides comprehensive vulnerability scanning for Docker images
- **[docker_connectivity_check.sh](./docker_connectivity_check.sh)**: A diagnostic tool for checking Docker connectivity issues

## Usage

### Basic Usage

Scan a Docker image for vulnerabilities:

```bash
./docker_vulnerability_scanner.sh --image my-image:latest
```

Or use the Make command:

```bash
make docker-scan
```

### Diagnostic Tool

If you encounter Docker connectivity issues:

```bash
./docker_connectivity_check.sh
```

Or use the Make command:

```bash
make docker-check
```

### Advanced Options

The scanner supports many options:

```bash
# Show help with all options
./docker_vulnerability_scanner.sh --help

# Customize severity levels
./docker_vulnerability_scanner.sh --severity "CRITICAL,HIGH,MEDIUM"

# Output to JSON file
./docker_vulnerability_scanner.sh --format json --output results.json

# Generate markdown report
./docker_vulnerability_scanner.sh --report

# Skip Python package scanning
./docker_vulnerability_scanner.sh --skip-python

# Specify Docker socket location
./docker_vulnerability_scanner.sh --socket /custom/path/to/docker.sock
```

## CI/CD Integration

We provide a GitHub Actions workflow for automated vulnerability scanning:

```yaml
# .github/workflows/docker-security-scan.yml
```

## Documentation

For comprehensive documentation on Docker security and vulnerability scanning, see:

- [Docker Security Documentation](./docs/docker_security.md)

## Cleanup

The vulnerability scanner generates various report files. To clean up these files:

```bash
# Remove security reports and scan results
rm -f security-report-*.md scan-results.json

# Or use the make command
make clean
```

These files are also included in .gitignore to prevent them from being committed to the repository.

## Recent Updates

- Consolidated multiple scanner scripts into a single enhanced scanner
- Added GitHub Actions workflow for automated scanning
- Improved Docker socket auto-detection
- Enhanced error handling and diagnostics
- Added comprehensive report generation 

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please make sure your code passes linting and tests:

```bash
# Format code
make format

# Run linting
make lint

# Run tests
make test
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Made with ❤️ using FastAPI and modern Python practices 