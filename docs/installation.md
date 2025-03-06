# Installation and Deployment Guide

This guide provides detailed instructions for installing, configuring, and deploying the Hello World API in different environments.

## Table of Contents
- [Local Development Setup](#local-development-setup)
- [Docker Development Setup](#docker-development-setup)
- [Production Deployment](#production-deployment)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## Local Development Setup

### Prerequisites
- Python 3.11 or higher
- Poetry (for dependency management)
- Git

### Step-by-Step Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hello-world-api.git
   cd hello-world-api
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

4. Create and configure a `.env` file:
   ```bash
   cp .env.example .env
   # Edit the .env file with your preferred settings
   ```

5. Run the application:
   ```bash
   python run.py
   ```

6. Access the API at http://localhost:8000
   - API documentation is available at http://localhost:8000/docs
   - ReDoc alternative UI is available at http://localhost:8000/redoc

### Running Tests

Run the tests using pytest:
```bash
pytest
```

Or use the provided script for a comprehensive test run:
```bash
python run_tests.py
```

## Docker Development Setup

### Prerequisites
- Docker
- Docker Compose

### Step-by-Step Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hello-world-api.git
   cd hello-world-api
   ```

2. Build and start the Docker container:
   ```bash
   docker-compose up --build
   ```

3. Access the API at http://localhost:8000

### Testing in Docker

Run tests inside the Docker container:
```bash
docker-compose exec api pytest
```

## Production Deployment

### Option 1: Docker Deployment

1. Configure production environment variables:
   ```bash
   # Create a production .env file
   cp .env.example .env.production
   # Edit the .env.production file with production settings
   ```

2. Build the production Docker image:
   ```bash
   docker build -t hello-world-api:production .
   ```

3. Run the production container:
   ```bash
   docker run -d --name hello-world-api \
     --env-file .env.production \
     -p 8000:8000 \
     hello-world-api:production
   ```

### Option 2: Kubernetes Deployment

1. Create Kubernetes deployment files (examples provided in `k8s/` directory)
2. Apply the Kubernetes manifests:
   ```bash
   kubectl apply -f k8s/
   ```

### Option 3: Cloud Platform Deployment

#### AWS Elastic Beanstalk

1. Install the EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize EB configuration:
   ```bash
   eb init -p docker
   ```

3. Deploy to Elastic Beanstalk:
   ```bash
   eb create production-environment
   ```

#### Google Cloud Run

1. Build and push Docker image to Google Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/your-project/hello-world-api
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy hello-world-api \
     --image gcr.io/your-project/hello-world-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Environment Variables

The application can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| HOST | Host to bind the server | 0.0.0.0 |
| PORT | Port to bind the server | 8000 |
| RELOAD | Enable/disable auto-reload for development | False |
| WORKERS | Number of worker processes | 4 |
| ENVIRONMENT | Deployment environment (development, staging, production) | development |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| LOG_FILE | Log file path | app.log |
| ALLOWED_ORIGINS | Comma-separated list of allowed CORS origins | * |
| API_VERSION | API version for endpoint routing | v1 |
| RATE_LIMIT_GENERAL | General rate limit (requests/time) | 100/minute |

## Troubleshooting

### Common Issues

#### Application fails to start

1. Check the logs:
   ```bash
   cat app.log
   ```

2. Verify that all required environment variables are set

3. Ensure the port is not in use by another application:
   ```bash
   lsof -i :8000
   ```

#### Docker-related issues

1. Check Docker logs:
   ```bash
   docker logs hello-world-api
   ```

2. Ensure Docker daemon is running:
   ```bash
   docker info
   ```

3. Verify Docker Compose configuration:
   ```bash
   docker-compose config
   ```

### Getting Help

If you encounter issues not covered in this guide:

1. Check the issue tracker on GitHub
2. Create a new issue with detailed information about your problem
3. Contact the development team 