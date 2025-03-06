# Build arguments
ARG PYTHON_VERSION=3.11
# Using Alpine Linux to eliminate Debian-specific vulnerabilities:
# - Eliminates perl-base (CVE-2023-31484) HIGH vulnerability
# - Eliminates zlib1g (CVE-2023-45853) CRITICAL vulnerability
# - Provides a smaller attack surface and reduced image size
ARG BASE_IMAGE=python:${PYTHON_VERSION}-alpine3.19
ARG RUNTIME_BASE=python:${PYTHON_VERSION}-alpine3.19

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

# Install build dependencies
# Alpine uses apk instead of apt-get for package management
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
    build-base \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

# First update pip and install a safe version of setuptools to fix CVE-2024-6345
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --force-reinstall setuptools==70.0.0

# Install poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy only requirements files first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Export requirements and install dependencies directly without poetry virtualenv
RUN poetry export -f requirements.txt > requirements.txt && \
    # Ensure we have the secure versions explicitly listed
    echo "gunicorn==22.0.0" >> requirements.txt && \
    echo "python-multipart==0.0.18" >> requirements.txt && \
    echo "setuptools==70.0.0" >> requirements.txt && \
    # Install from the requirements file directly
    pip install --no-cache-dir -r requirements.txt && \
    # Force upgrade setuptools to fix CVE-2024-6345 after all dependencies
    pip install --no-cache-dir --force-reinstall setuptools==70.0.0 && \
    # Verify setuptools version
    pip show setuptools | grep "Version:"

# Runtime stage
FROM ${RUNTIME_BASE} AS runtime

# Set working directory for the runtime stage
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install runtime dependencies and force setuptools update (fix CVE-2024-6345)
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
    # Add runtime dependencies only
    libffi \
    openssl \
    # Add curl for healthchecks
    curl && \
    # Update pip and setuptools in the runtime stage too
    pip install --no-cache-dir --force-reinstall setuptools==70.0.0 && \
    # Create a non-root user to run the application
    addgroup -S appgroup && \
    adduser -S appuser -G appgroup && \
    # Create log directory with appropriate permissions
    mkdir -p /app/logs && \
    chown -R appuser:appgroup /app

# Copy the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Final check for setuptools version in runtime stage 
RUN pip show setuptools | grep "Version:"

# Copy application code
COPY --chown=appuser:appgroup ./app /app/app
COPY --chown=appuser:appgroup ./run.py /app/run.py
COPY --chown=appuser:appgroup ./gunicorn_conf.py /app/gunicorn_conf.py
COPY --chown=appuser:appgroup ./healthcheck.sh /app/healthcheck.sh

# Make the healthcheck script executable
RUN chmod +x /app/healthcheck.sh

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Set up a health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD /app/healthcheck.sh

# Run the application with Gunicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/app/gunicorn_conf.py", "app.main:app"]

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
      com.example.api.build-date="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
      com.example.api.security-notes="Switched to Alpine Linux to address perl-base (CVE-2023-31484) and zlib1g (CVE-2023-45853) vulnerabilities. Alpine uses musl libc and BusyBox instead of glibc and perl. Upgraded setuptools to 70.0.0 to fix CVE-2024-6345." \
      base_image="python:${PYTHON_VERSION}-alpine3.19" 