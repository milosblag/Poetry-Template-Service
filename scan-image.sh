#!/bin/bash
set -e

# Default configuration
IMAGE_NAME="hello-world-api:latest"
SEVERITY="HIGH,CRITICAL"
OUTPUT_FORMAT="table"
TIMEOUT="10m"
EXIT_ON_SEVERITY="CRITICAL"

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --image=*)
      IMAGE_NAME="${1#*=}"
      shift
      ;;
    --severity=*)
      SEVERITY="${1#*=}"
      shift
      ;;
    --exit-on=*)
      EXIT_ON_SEVERITY="${1#*=}"
      shift
      ;;
    --timeout=*)
      TIMEOUT="${1#*=}"
      shift
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo "Options:"
      echo "  --image=NAME      Docker image name to scan (default: hello-world-api:latest)"
      echo "  --severity=LEVEL  Severity levels to scan for (default: HIGH,CRITICAL)"
      echo "  --exit-on=LEVEL   Exit with error if vulnerabilities at this level are found (default: CRITICAL)"
      echo "  --timeout=TIME    Timeout for scan (default: 10m)"
      echo "  --help            Display this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# On macOS, set Docker socket location if default is not found
if [ ! -S /var/run/docker.sock ] && [ -S $HOME/.docker/run/docker.sock ]; then
    export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock
    echo "Using Docker socket at $DOCKER_HOST"
fi

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

# Check if Docker is accessible
if ! docker info &> /dev/null; then
    echo "Error: Cannot connect to the Docker daemon. Make sure Docker is running and you have the proper permissions."
    echo "Try running with 'sudo' or add your user to the docker group."
    exit 2
fi

# Run scan for vulnerabilities
echo "Starting vulnerability scan..."
trivy_result=$(trivy image --exit-code 1 --severity "$SEVERITY" --timeout "$TIMEOUT" --format "$OUTPUT_FORMAT" "$IMAGE_NAME" 2>&1) || scan_exit_code=$?

# Check if the scan was successful
if echo "$trivy_result" | grep -q "unable to initialize a scanner\|unable to find the specified image"; then
    echo "❌ Error during scanning:"
    echo "$trivy_result"
    echo "Please make sure the image exists and you have permissions to access it."
    exit 3
fi

# Display the scan results
echo "$trivy_result"

# Count vulnerabilities by severity
high_count=$(echo "$trivy_result" | grep -c "HIGH" || true)
critical_count=$(echo "$trivy_result" | grep -c "CRITICAL" || true)

# Check if vulnerabilities were found
if [ -z "$scan_exit_code" ]; then
    echo "✅ Success: No $SEVERITY vulnerabilities found!"
    exit 0
else
    echo ""
    echo "⚠️ Vulnerability Summary:"
    echo "   - HIGH: $high_count"
    echo "   - CRITICAL: $critical_count"
    echo ""
    
    # Check specifically for critical vulnerabilities
    if [[ "$EXIT_ON_SEVERITY" == "NONE" ]]; then
        echo "📝 Vulnerabilities found, but exit-on-severity is set to NONE. Continuing..."
        exit 0
    elif [[ "$EXIT_ON_SEVERITY" == "CRITICAL" ]] && [ "$critical_count" -eq 0 ]; then
        echo "📝 Found HIGH vulnerabilities, but none at the '$EXIT_ON_SEVERITY' level."
        echo "   Consider addressing these issues in future updates."
        exit 0
    else
        if [[ "$EXIT_ON_SEVERITY" == "CRITICAL" ]]; then
            echo "❌ $critical_count CRITICAL vulnerabilities found! Pipeline will fail."
        else
            echo "❌ Vulnerabilities found at '$EXIT_ON_SEVERITY' level! Pipeline will fail."
        fi
        echo "   These vulnerabilities must be addressed before proceeding."
        exit $scan_exit_code
    fi
fi 