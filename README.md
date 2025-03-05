# Hello World API with Docker Security Scanner

A production-ready FastAPI Hello World API with integrated security scanning for Docker images.

## Project Overview

This project consists of:

1. A production-ready FastAPI application with health checks, rate limiting, and proper logging
2. A secure Dockerfile with multi-stage builds and security best practices
3. A Docker Compose configuration for easy local deployment
4. A powerful security scanning script (`scan-image.sh`) to find vulnerabilities in Docker images

## Features

### FastAPI Application

- **FastAPI Framework**: Modern, high-performance web framework based on Python type hints
- **Health Check Endpoint**: Built-in monitoring endpoint with comprehensive service health information
- **Rate Limiting**: Protection against abuse with configurable rate limits
- **Proper Logging**: Structured logging with rotation support
- **CORS Configuration**: Configurable Cross-Origin Resource Sharing
- **Error Handling**: Comprehensive exception handling with proper error responses

### Docker Setup

- **Multi-Stage Build**: Optimized Docker image size and improved security
- **Security Hardening**: Non-root user, read-only filesystem where possible, removed unnecessary binaries
- **Resource Limiting**: CPU and memory constraints to prevent resource exhaustion
- **Health Checking**: Containerized health checking with retries and proper reporting

### Security Scanner

- **Automated Vulnerability Scanning**: Using Trivy to detect security issues
- **Configurable Severity Levels**: Focus on specific vulnerability severities (LOW, MEDIUM, HIGH, CRITICAL)
- **CI/CD Integration**: Flexible exit code handling for pipeline integration
- **macOS Support**: Special handling for Docker Desktop on macOS

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop)
- [Trivy](https://aquasecurity.github.io/trivy/latest/getting-started/installation/) (for security scanning)
- Bash shell

## Getting Started

### Building the API

Build the Docker image using Docker Compose:

```bash
docker-compose build
```

Or build directly with Docker:

```bash
docker build -t hello-world-api:latest .
```

### Running the API

Start the API with Docker Compose:

```bash
docker-compose up -d
```

Check if the API is running:

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2023-08-15T12:30:45Z"
}
```

### Accessing the API

The main endpoint is available at:

```
http://localhost:8000/
```

The health check endpoint is available at:

```
http://localhost:8000/health
```

## Security Scanning

The project includes a powerful security scanning script for Docker images.

### Running the Security Scanner

Make the script executable:

```bash
chmod +x scan-image.sh
```

Scan the default API image:

```bash
./scan-image.sh
```

### Security Scanner Options

- `--image=NAME`: Docker image name to scan (default: hello-world-api:latest)
- `--severity=LEVEL`: Severity levels to scan for (default: HIGH,CRITICAL)
- `--exit-on=LEVEL`: Exit with error if vulnerabilities at this level are found (default: CRITICAL)
- `--timeout=TIME`: Timeout for scan (default: 10m)
- `--help`: Display help message

### Security Scanner Examples

Scan the default image:
```bash
./scan-image.sh
```

Scan a specific image:
```bash
./scan-image.sh --image=myapp:1.0
```

Scan for all vulnerability levels:
```bash
./scan-image.sh --severity=LOW,MEDIUM,HIGH,CRITICAL
```

Report vulnerabilities but don't fail the pipeline:
```bash
./scan-image.sh --exit-on=NONE
```

### Security Scanner Exit Codes

- `0`: No vulnerabilities found or vulnerabilities below exit-on level
- `1`: Vulnerabilities found at or above exit-on level
- `2`: Docker daemon connection error
- `3`: Image not found or scanning error

## CI/CD Integration

The security scanner can be integrated into CI/CD pipelines to enforce security requirements:

```yaml
# Example GitHub Actions job
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t hello-world-api:latest .
      
    - name: Install Trivy
      run: |
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
        
    - name: Run security scan
      run: ./scan-image.sh --image=hello-world-api:latest
```

## Development

### Local Python Setup

If you want to run the API locally without Docker:

1. Install Poetry:
```bash
pip install poetry
```

2. Install dependencies:
```bash
poetry install
```

3. Run the API:
```bash
poetry run uvicorn main:app --reload
```

### Configuration

The application is configured through environment variables, which can be set in the `.env` file:

- `ENVIRONMENT`: Set to `development`, `staging`, or `production`
- `HOST`: Host to bind the API server to
- `PORT`: Port to expose the API
- `LOG_LEVEL`: Logging level (info, debug, warning, error)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
- `RATE_LIMIT_GENERAL`: Rate limit for API endpoints

## Troubleshooting

### Docker Issues

If you encounter permission issues with Docker, ensure your user has the necessary permissions to access the Docker daemon:

```bash
# Add your user to the docker group (Linux)
sudo usermod -aG docker $USER
```

On macOS, ensure Docker Desktop is running and properly authenticated.

### macOS Docker Socket

The security scanner automatically detects if it's running on macOS and sets the correct Docker socket location, which is typically at `~/.docker/run/docker.sock` instead of the default `/var/run/docker.sock`.

If you still encounter issues, you can manually set the Docker host:

```bash
export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock
```

### Trivy Installation

If Trivy is not installed, you can install it following the [official installation guide](https://aquasecurity.github.io/trivy/latest/getting-started/installation/).

Quick installation commands:

```bash
# macOS
brew install trivy

# Debian/Ubuntu
apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list
apt-get update
apt-get install trivy
```

## License

MIT 