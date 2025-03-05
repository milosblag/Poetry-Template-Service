# Hello World API

A production-ready FastAPI Hello World API with proper configuration and best practices.

## Installation

```bash
# Install poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

## Running the Application

For development:
```bash
poetry run dev
```

For production:
```bash
poetry run start
```

## API Documentation

Once running, you can access:
- API documentation at: http://localhost:8000/docs
- Alternative documentation at: http://localhost:8000/redoc
- The Hello World endpoint at: http://localhost:8000/ 