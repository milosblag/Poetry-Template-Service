#!/bin/bash
set -e

# Default values
IMAGE_NAME="hello-world-api:alpine-secure"
SEVERITY="HIGH,CRITICAL"
OUTPUT_FORMAT="table"
OUTPUT_FILE=""
TIMEOUT="10m"
SCAN_PYTHON=true
SCAN_OS=true
GENERATE_REPORT=false

# Display help message
function show_help {
    echo "Docker Image Security Scanner"
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --image NAME[:TAG]    Docker image to scan (default: $IMAGE_NAME)"
    echo "  --severity LEVEL      Comma-separated list of severity levels to scan for (default: $SEVERITY)"
    echo "                        Possible values: UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL"
    echo "  --format FORMAT       Output format (default: $OUTPUT_FORMAT)"
    echo "                        Possible values: table, json, sarif, cyclonedx, github"
    echo "  --output FILE         Write results to file instead of stdout"
    echo "  --timeout DURATION    Timeout duration (default: $TIMEOUT)"
    echo "  --skip-python         Skip scanning Python packages"
    echo "  --skip-os             Skip scanning OS packages"
    echo "  --report              Generate a security report in Markdown format"
    echo "  --help                Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --image myapp:1.0.0 --severity HIGH,CRITICAL --format json --output scan-results.json"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        --severity)
            SEVERITY="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --skip-python)
            SCAN_PYTHON=false
            shift
            ;;
        --skip-os)
            SCAN_OS=false
            shift
            ;;
        --report)
            GENERATE_REPORT=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Prepare scan command
SCAN_CMD="docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image"

# Add options
if [ "$SCAN_PYTHON" = false ]; then
    SCAN_CMD="$SCAN_CMD --skip-files-with-python"
fi

if [ "$SCAN_OS" = false ]; then
    SCAN_CMD="$SCAN_CMD --skip-os-packages"
fi

SCAN_CMD="$SCAN_CMD --severity $SEVERITY --timeout $TIMEOUT"

if [ -n "$OUTPUT_FILE" ]; then
    SCAN_CMD="$SCAN_CMD --format $OUTPUT_FORMAT --output $OUTPUT_FILE"
else
    SCAN_CMD="$SCAN_CMD --format $OUTPUT_FORMAT"
fi

# Add image name
SCAN_CMD="$SCAN_CMD $IMAGE_NAME"

# Print scan information
echo "==============================================="
echo "🔍 Docker Image Security Scanner"
echo "==============================================="
echo "Image: $IMAGE_NAME"
echo "Scanning for: $SEVERITY vulnerabilities"
echo "Timeout: $TIMEOUT"
echo "==============================================="
echo "Starting vulnerability scan..."

# Run the scan
if [ -n "$OUTPUT_FILE" ]; then
    eval "$SCAN_CMD"
    echo "Scan results saved to $OUTPUT_FILE"
else
    eval "$SCAN_CMD"
fi

# Generate security report if requested
if [ "$GENERATE_REPORT" = true ]; then
    REPORT_FILE="security-report-$(date +%Y%m%d).md"
    
    echo "# Security Report for $IMAGE_NAME" > "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "## Scan Information" >> "$REPORT_FILE"
    echo "- **Date**: $(date)" >> "$REPORT_FILE"
    echo "- **Image**: $IMAGE_NAME" >> "$REPORT_FILE"
    echo "- **Severity Levels**: $SEVERITY" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    echo "## Vulnerability Summary" >> "$REPORT_FILE"
    
    if [ -n "$OUTPUT_FILE" ] && [ "$OUTPUT_FORMAT" = "json" ]; then
        # Extract summary from JSON output
        VULN_COUNT=$(jq '.Results | map(.Vulnerabilities | length) | add' "$OUTPUT_FILE")
        CRITICAL_COUNT=$(jq '.Results | map(.Vulnerabilities | map(select(.Severity == "CRITICAL")) | length) | add' "$OUTPUT_FILE")
        HIGH_COUNT=$(jq '.Results | map(.Vulnerabilities | map(select(.Severity == "HIGH")) | length) | add' "$OUTPUT_FILE")
        
        echo "- **Total vulnerabilities**: $VULN_COUNT" >> "$REPORT_FILE"
        echo "- **Critical**: $CRITICAL_COUNT" >> "$REPORT_FILE"
        echo "- **High**: $HIGH_COUNT" >> "$REPORT_FILE"
    else
        echo "For detailed vulnerability information, please run the scan with JSON output format." >> "$REPORT_FILE"
    fi
    
    echo "" >> "$REPORT_FILE"
    echo "## Recommendations" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "1. Update vulnerable packages to their latest versions" >> "$REPORT_FILE"
    echo "2. Consider using a more secure base image" >> "$REPORT_FILE"
    echo "3. Implement least privilege principles" >> "$REPORT_FILE"
    echo "4. Use multi-stage builds to reduce attack surface" >> "$REPORT_FILE"
    echo "5. Run containers as non-root users" >> "$REPORT_FILE"
    echo "6. Regularly scan images for vulnerabilities" >> "$REPORT_FILE"
    
    echo "Security report generated: $REPORT_FILE"
fi

# Check if there are vulnerabilities and exit with appropriate code
if [ -n "$OUTPUT_FILE" ] && [ "$OUTPUT_FORMAT" = "json" ]; then
    VULN_COUNT=$(jq '.Results | map(.Vulnerabilities | length) | add' "$OUTPUT_FILE")
    if [ "$VULN_COUNT" -gt 0 ]; then
        echo "⚠️ Vulnerability Summary:"
        echo "   - HIGH: $(jq '.Results | map(.Vulnerabilities | map(select(.Severity == "HIGH")) | length) | add' "$OUTPUT_FILE")"
        echo "   - CRITICAL: $(jq '.Results | map(.Vulnerabilities | map(select(.Severity == "CRITICAL")) | length) | add' "$OUTPUT_FILE")"
        echo ""
        echo "❌ $VULN_COUNT vulnerabilities found! Pipeline will fail."
        echo "   These vulnerabilities must be addressed before proceeding."
        exit 1
    else
        echo "✅ No vulnerabilities found!"
        exit 0
    fi
fi

# If we can't determine the exact count (not using JSON output), exit with code 1 if the scan found vulnerabilities
if [ $? -ne 0 ]; then
    exit 1
else
    echo "✅ No vulnerabilities found!"
    exit 0
fi 