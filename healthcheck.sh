#!/bin/sh
set -e

# Configuration
HEALTH_ENDPOINT="http://localhost:8000/api/v1/health"
TIMEOUT=5
MAX_RETRIES=3

# Helper function for logging
log() {
  echo "[healthcheck] $1"
}

# Function to check if the service is responding
check_endpoint() {
  log "Checking endpoint: $HEALTH_ENDPOINT"
  
  # Try to connect with timeout and check for 200 status code
  response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT $HEALTH_ENDPOINT)
  
  if [ "$response" = "200" ]; then
    log "Health check successful: HTTP $response"
    return 0
  else
    log "Health check failed: HTTP $response"
    return 1
  fi
}

# Check if curl is available
if ! command -v curl >/dev/null 2>&1; then
  log "Error: curl is required but not installed"
  exit 1
fi

# Try multiple times before giving up
retry=0
while [ $retry -lt $MAX_RETRIES ]; do
  if check_endpoint; then
    exit 0
  fi
  
  retry=$((retry+1))
  
  if [ $retry -lt $MAX_RETRIES ]; then
    log "Retrying in 1 second... (Attempt $retry/$MAX_RETRIES)"
    sleep 1
  fi
done

log "Health check failed after $MAX_RETRIES attempts"
exit 1 