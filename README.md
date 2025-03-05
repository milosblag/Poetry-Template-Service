# Hello World API

A production-ready FastAPI Hello World API with a clean, modular structure.

## Project Structure

```
hello-world-api/
├── app/                    # Main application package
│   ├── api/                # API endpoints and routers
│   │   ├── endpoints/      # API endpoint modules
│   │   ├── middleware/     # Middleware components
│   │   └── dependencies/   # Endpoint dependencies
│   ├── core/               # Core application components
│   │   └── security/       # Security utilities
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic services
│   ├── database/           # Database models and utilities
│   └── utils/              # Utility functions
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── docs/                   # Documentation
├── .env                    # Environment variables
├── pyproject.toml          # Poetry configuration
├── poetry.lock             # Poetry lock file
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── gunicorn_conf.py        # Gunicorn configuration
└── run.py                  # Entry point script
```

## Features

- **Modular Structure**: Clean separation of concerns
- **API Versioning**: Support for API versioning
- **Health Checks**: Comprehensive health check endpoint
- **Security**: Security headers, rate limiting, and CORS configuration
- **Logging**: Structured logging with rotation
- **Configuration**: Environment-based configuration with validation
- **Docker Support**: Production-ready Docker configuration
- **Testing**: Unit and integration test structure

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hello-world-api.git
   cd hello-world-api
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Run the application:
   ```bash
   poetry run python run.py
   ```

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t hello-world-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 hello-world-api
   ```

Or use Docker Compose:
```bash
docker-compose up
```

## API Documentation

When running in development mode, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Configure the application using environment variables or a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| HOST | Server host | 0.0.0.0 |
| PORT | Server port | 8000 |
| RELOAD | Enable auto-reload | False |
| WORKERS | Number of workers | 4 |
| ENVIRONMENT | Environment (development/production) | development |
| LOG_LEVEL | Logging level | INFO |
| ALLOWED_ORIGINS | CORS allowed origins (comma-separated) | * |
| API_VERSION | API version | v1 |
| RATE_LIMIT_GENERAL | General rate limit | 100/minute |

## Testing

Run tests with pytest:
```bash
poetry run pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov=app
```

## Development

### Code Formatting

Format code with Black:
```bash
poetry run black .
```

Sort imports with isort:
```bash
poetry run isort .
```

### Type Checking

Run type checking with mypy:
```bash
poetry run mypy app
```

### Linting

Run linting with flake8:
```bash
poetry run flake8 app
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 