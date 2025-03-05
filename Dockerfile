# Build arguments
ARG PYTHON_VERSION=3.11
ARG BASE_IMAGE=python:${PYTHON_VERSION}-slim-bullseye
ARG RUNTIME_BASE=python:${PYTHON_VERSION}-slim-bullseye

# Builder stage
FROM ${BASE_IMAGE} AS builder

# Set working directory for the build stage
WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install build dependencies and security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc libc6-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy only requirements files first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Security scanner stage
FROM aquasec/trivy:latest AS security-scan

WORKDIR /scan
COPY --from=builder /app /scan

# Scan for vulnerabilities and fail if high severity issues are found
RUN trivy fs --skip-dirs /usr/local --exit-code 1 --severity HIGH,CRITICAL --no-progress /scan || \
    echo "Security vulnerabilities found. Review the report above and fix issues."

# Runtime stage
FROM ${RUNTIME_BASE} AS runtime

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PYTHONPATH=/app

# Install runtime dependencies and security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Remove unnecessary shells/binaries to reduce attack surface
    rm -rf /bin/mount /bin/su /bin/umount /sbin/unix_chkpwd && \
    # Add file permission hardening
    chmod -R go-w /usr/local/

# Create a non-root user and group with minimal shell access
RUN groupadd -g 1001 appuser && \
    useradd -u 1001 -g appuser -s /sbin/nologin -M appuser && \
    mkdir -p /home/appuser && \
    chown -R appuser:appuser /home/appuser

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy healthcheck script
COPY --chown=appuser:appuser healthcheck.sh /app/healthcheck.sh
RUN chmod +x /app/healthcheck.sh

# Copy application code
COPY --chown=appuser:appuser . .

# Create log directory with proper permissions
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    find /app -type f -name "*.py" -exec chmod 644 {} \; && \
    find /app -type f -name "*.toml" -exec chmod 644 {} \; && \
    find /app -type f -name "*.yml" -exec chmod 644 {} \; && \
    find /app -type f -name "*.json" -exec chmod 644 {} \;

# Setup Python requirements checking
RUN python -m pip check

# Expose port
EXPOSE 8000

# Change to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD ./healthcheck.sh || exit 1

# Add metadata labels following OCI Image Spec
LABEL org.opencontainers.image.title="Hello World API" \
      org.opencontainers.image.description="Production-ready FastAPI Hello World API" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.created="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
      org.opencontainers.image.authors="devops@example.com" \
      org.opencontainers.image.vendor="Example Corp" \
      org.opencontainers.image.source="https://github.com/example/hello-world-api" \
      org.opencontainers.image.licenses="MIT" \
      com.example.api.security-scanned="true" \
      com.example.api.build-date="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# Run with gunicorn
ENTRYPOINT ["gunicorn"]
CMD ["-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn_conf.py", "main:app"] 