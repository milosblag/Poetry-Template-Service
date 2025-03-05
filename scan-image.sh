#!/bin/bash
set -e

# Configuration
IMAGE_NAME="hello-world-api:latest"
SEVERITY="HIGH,CRITICAL"
OUTPUT_FORMAT="table"
TIMEOUT="10m"
EXIT_ON_SEVERITY="CRITICAL"

# Print banner
echo "==============================================="
echo "🔍 Docker Image Security Scanner"
echo "==============================================="
echo "Image: $IMAGE_NAME"
echo "Scanning for: $SEVERITY vulnerabilities"
echo "Timeout: $TIMEOUT"
echo "==============================================="

# Check if Trivy is installed
if ! command -v trivy &> /dev/null; then
    echo "Error: Trivy is not installed. Please install it first."
    echo "See https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
    exit 1
fi

# Run scan for vulnerabilities
echo "Starting vulnerability scan..."
if trivy image --exit-code 1 --severity "$SEVERITY" --timeout "$TIMEOUT" --format "$OUTPUT_FORMAT" "$IMAGE_NAME"; then
    echo "✅ Success: No $SEVERITY vulnerabilities found!"
    exit 0
else
    scan_exit_code=$?
    echo "⚠️ Warning: Vulnerabilities detected with severity $SEVERITY"
    
    # Check specifically for critical vulnerabilities
    if trivy image --exit-code 1 --severity "$EXIT_ON_SEVERITY" --timeout "$TIMEOUT" --format "$OUTPUT_FORMAT" "$IMAGE_NAME" > /dev/null 2>&1; then
        echo "❌ Found vulnerabilities, but none at the '$EXIT_ON_SEVERITY' level. Continuing..."
        exit 0
    else
        echo "❌ CRITICAL vulnerabilities found! Pipeline will fail."
        exit $scan_exit_code
    fi
fi 