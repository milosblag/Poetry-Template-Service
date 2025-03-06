# Docker Security and Vulnerability Scanning

This document outlines the security measures and vulnerability scanning procedures for Docker images in this project.

## Table of Contents

- [Introduction](#introduction)
- [Security Best Practices](#security-best-practices)
- [Vulnerability Scanning](#vulnerability-scanning)
  - [Prerequisites](#prerequisites)
  - [Diagnostic Tool](#diagnostic-tool)
  - [Environment Variables](#environment-variables)
  - [Scanning Options](#scanning-options)
  - [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)
- [Handling Vulnerabilities](#handling-vulnerabilities)
- [Cleaning Up](#cleaning-up)
- [Resources](#resources)

## Introduction

Docker containers are a core part of our deployment strategy. While they provide isolation and reproducibility, they also introduce security considerations that must be addressed. This document outlines our approach to Docker security and vulnerability management.

## Security Best Practices

Our Docker setup follows these security best practices:

1. **Minimal Base Images**: We use Alpine Linux as our base image to reduce the attack surface.
2. **Multi-stage Builds**: We separate build dependencies from runtime dependencies.
3. **Non-root Users**: Our applications run as non-root users.
4. **Read-only Filesystem**: Where possible, containers run with read-only filesystems.
5. **Resource Limits**: We apply resource constraints to prevent resource exhaustion attacks.
6. **Up-to-date Dependencies**: We regularly update dependencies to address known vulnerabilities.
7. **Secrets Management**: Sensitive information is not stored in Docker images.

## Vulnerability Scanning

We use [Trivy](https://github.com/aquasecurity/trivy) for vulnerability scanning of Docker images. Trivy is a comprehensive, easy-to-use scanner that can detect vulnerabilities in container images.

### Prerequisites

Before running vulnerability scans, ensure:

1. **Docker is running** - Docker daemon must be active on your system
2. **Trivy is installed** - The script will attempt to use a containerized version if Trivy is not installed locally
3. **Docker image exists** - The target image must be built or available

### Diagnostic Tool

If you encounter Docker connectivity issues, use our diagnostic tool:

```bash
# Run diagnostic check
./docker_connectivity_check.sh

# Or use the make command
make docker-check
```

This tool will:
- Check Docker daemon status
- Verify Docker socket permissions
- Test Docker API access
- Diagnose common connectivity issues
- Provide tailored solutions for your environment

### Environment Variables

The vulnerability scanning script supports several environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| DOCKER_HOST | Docker daemon socket location | `unix:///home/user/.docker/run/docker.sock` |
| TRIVY_DEBUG | Enable verbose Trivy output | `true` |
| DOCKER_BUILDKIT | Use BuildKit for building images | `1` |
| TRIVY_IGNORE_UNFIXED | Ignore unfixed vulnerabilities | `true` |

### Scanning Options

Our Docker vulnerability scanner provides comprehensive options for different scanning needs:

```bash
# Basic usage
./docker_vulnerability_scanner.sh

# Show help with all options
./docker_vulnerability_scanner.sh --help

# Scan a specific image 
./docker_vulnerability_scanner.sh --image custom-image:tag

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

You can also use the make command for quick access:

```bash
make docker-scan
```

The scanner provides these benefits:

1. **Automatic Socket Detection**: Automatically detects Docker socket location on macOS, WSL, and standard Linux systems
2. **Containerized Scanning**: Runs Trivy in a container if not installed locally
3. **Local or Remote Images**: Offers to build or pull missing images
4. **Multiple Output Formats**: Supports table, JSON, SARIF, CycloneDX and GitHub formats
5. **Report Generation**: Can create detailed Markdown security reports
6. **Customizable Timeouts**: Allows setting scan timeouts for large images

### CI/CD Integration

For CI/CD pipelines, you can use the scanner with appropriate options:

```bash
# Basic usage with report generation for CI
./docker_vulnerability_scanner.sh --report

# More complete CI configuration
./docker_vulnerability_scanner.sh --image hello-world-api:latest --severity HIGH,CRITICAL --format json --output ./security-reports/scan-results.json --report
```

You can configure exit codes in your CI pipeline based on the scanner's exit code:
- Exit code 0: No vulnerabilities found (or below threshold)
- Non-zero exit code: Vulnerabilities found above threshold

## Troubleshooting

Common issues that may occur during vulnerability scanning:

### Docker Daemon Not Running

**Error:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

**Solution:**
1. Start Docker:
   - **macOS**: Start Docker Desktop application
   - **Linux**: `sudo systemctl start docker`
   - **Windows**: Start Docker Desktop application
2. Verify Docker is running: `docker info`

### Docker Socket Not Accessible

**Error:**
```
Docker socket is not accessible
```

**Solution:**
1. Check if the Docker socket exists:
   - Linux/macOS: `ls -la /var/run/docker.sock`
   - Windows: Check if Docker Desktop is fully initialized
2. Check permissions on the socket (Linux/macOS):
   - `ls -la /var/run/docker.sock`
   - Should show something like: `srw-rw---- 1 root docker`
3. Make sure your user is in the docker group:
   - `groups $USER`
   - If not in docker group: `sudo usermod -aG docker $USER` (logout and login again)
4. For CI environments:
   - GitHub Actions: Use privileged container or docker action
   - GitLab CI: Use docker:dind service
   - Jenkins: Add user to docker group

### Docker API Access Issues

**Error:**
```
Cannot access Docker API
```

**Solution:**
1. Verify your user has permission to use Docker:
   - Run a simple Docker command: `docker ps`
   - If you get permission errors, add your user to the docker group
2. Check if Docker is accessible via TCP:
   - Some environments use TCP instead of socket: `DOCKER_HOST=tcp://localhost:2375`
3. For CI environments:
   - Make sure the CI runner has proper Docker access
   - Check if you need to bind mount the Docker socket from host

### Permission Issues

**Error:**
```
Cannot list Docker images (permission issue)
```

**Solution:**
1. Run the command with sudo if appropriate
2. Add your user to the docker group: `sudo usermod -aG docker $USER` (logout/login required)
3. Check that the Docker socket has the correct group permissions
4. Use our diagnostic tool: `./docker_connectivity_check.sh`

### Trivy Cannot Connect to Docker

**Error:**
```
scan error: unable to initialize a scanner: unable to initialize an image scanner: unable to find the specified image
```

**Solution:**
1. Run our diagnostic tool first: `./docker_connectivity_check.sh`
2. Try setting the DOCKER_HOST environment variable: `DOCKER_HOST=unix:///var/run/docker.sock ./docker_vulnerability_scanner.sh`
3. For macOS users: `DOCKER_HOST=unix://$HOME/.docker/run/docker.sock ./docker_vulnerability_scanner.sh`
4. Use the socket parameter: `./docker_vulnerability_scanner.sh --socket /path/to/docker.sock`

### HTML Template Not Found

**Error:**
```
template not found: @contrib/html.tpl
```

**Solution:**
This is usually encountered in CI environments. The script will attempt to use alternative formats or create a basic output file.

## Handling Vulnerabilities

When vulnerabilities are detected:

1. **Assess Impact**: Determine if the vulnerability affects your application.
2. **Update Dependencies**: Update to patched versions of affected packages.
3. **Consider Mitigations**: If updates are not available, implement mitigations.
4. **Document Exceptions**: For accepted vulnerabilities, document the decision.

Our general approach follows this priority:

1. CRITICAL and HIGH vulnerabilities should be addressed immediately.
2. MEDIUM vulnerabilities should be scheduled for remediation.
3. LOW vulnerabilities should be documented and addressed during regular maintenance.

## Cleaning Up

The vulnerability scanner generates various files that should be cleaned up after use, especially in CI/CD environments.

### Generated Files

- **security-report-{date}.md**: Markdown reports with scan results
- **scan-results.json**: Raw JSON output from Trivy
- **security-reports/**: Directory containing various report formats
- **trivy-*.json**: Additional JSON output files
- **trivy-*.sarif**: SARIF format reports

### Cleaning Up Reports

You can clean up these files using:

```bash
# Using the Makefile
make security-clean  # Clean only security reports
make clean           # Clean all temporary files including security reports

# Manual cleanup
rm -f security-report-*.md security-report-*.html scan-results.json trivy-*.json trivy-*.sarif
rm -rf security-reports/
```

### GitIgnore Configuration

The project's `.gitignore` file is configured to exclude these security reports from being committed to the repository.

## Resources

- [Trivy Documentation](https://aquasecurity.github.io/trivy/latest/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker) 