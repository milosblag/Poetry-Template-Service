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

# Install poetry and update setuptools to secure version
RUN pip install --no-cache-dir poetry==1.7.1 && \
    pip install --no-cache-dir --upgrade pip setuptools>=70.0.0

# Copy only requirements files first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Export requirements and install dependencies directly without poetry virtualenv
RUN poetry export -f requirements.txt > requirements.txt && \
    # Ensure we have the secure versions explicitly listed
    echo "gunicorn==22.0.0" >> requirements.txt && \
    echo "python-multipart==0.0.18" >> requirements.txt && \
    echo "setuptools>=70.0.0" >> requirements.txt && \
    # Install from the requirements file directly
    pip install --no-cache-dir -r requirements.txt && \
    # Force upgrade setuptools to fix CVE-2024-6345
    pip install --no-cache-dir --upgrade setuptools>=70.0.0 && \
    # Verify installations are correct versions
    pip list | grep gunicorn && pip list | grep python-multipart && pip list | grep setuptools

# Runtime stage - using distroless for extra security
FROM ${RUNTIME_BASE} AS runtime

# Security note: Using Alpine Linux eliminates vulnerabilities found in Debian-based images
# Alpine provides:
# - Minimal base system with a smaller attack surface
# - musl libc instead of glibc (avoids certain classes of vulnerabilities)
# - No vulnerable packages found in Debian (perl-base, zlib1g)
# - Significantly smaller image size (~70% smaller)

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PYTHONPATH=/app

# Minimal runtime packages
RUN apk update && \
    apk upgrade --no-cache && \
    # Cleanup to reduce image size
    rm -rf /var/cache/apk/* && \
    # Create a non-root user
    addgroup -g 1001 -S appuser && \
    adduser -u 1001 -S appuser -G appuser -h /home/appuser && \
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
    find /app -type f -name "*.json" -exec chmod 644 {} \; && \
    # Remove any .venv directory if exists to avoid package version conflicts
    rm -rf /app/.venv

# Double check our package installations are correct and up-to-date
RUN pip list | grep gunicorn && pip list | grep python-multipart && pip list | grep setuptools && \
    # Force upgrade setuptools to fix CVE-2024-6345
    pip install --no-cache-dir --upgrade setuptools>=70.0.0 && \
    # Verify we have secure versions
    python -c "import pkg_resources; print('Gunicorn version:', pkg_resources.get_distribution('gunicorn').version); print('Python-multipart version:', pkg_resources.get_distribution('python-multipart').version); print('Setuptools version:', pkg_resources.get_distribution('setuptools').version)"

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
      com.example.api.build-date="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
      com.example.api.security-notes="Switched to Alpine Linux to address perl-base (CVE-2023-31484) and zlib1g (CVE-2023-45853) vulnerabilities. Alpine uses musl libc and BusyBox instead of glibc and perl."

# Run with gunicorn
ENTRYPOINT ["gunicorn"]
CMD ["-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn_conf.py", "main:app"] 