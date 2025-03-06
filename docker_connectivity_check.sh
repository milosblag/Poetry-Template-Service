#!/bin/bash
# docker_connectivity_check.sh
# A diagnostic tool to check Docker connectivity and fix common issues
# This script helps diagnose Docker daemon issues before running vulnerability scans

set -e

echo "🔍 Docker Connectivity Diagnostic Tool 🔍"
echo "==========================================="

# Check if Docker CLI is installed
echo "Checking for Docker CLI..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker CLI not found! Please install Docker first."
    exit 1
fi
echo "✅ Docker CLI is installed"

# Try basic Docker info command
echo "Attempting to connect to Docker daemon..."
if docker info &> /dev/null; then
    echo "✅ Basic connection to Docker daemon successful"
else
    echo "❌ Cannot connect to Docker daemon"
    echo "Checking for common issues..."
    
    # Check if Docker daemon is running
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - check with launchctl
        if pgrep -f "Docker.app" &> /dev/null; then
            echo "🔍 Docker app is running but daemon may not be fully initialized"
            echo "   Try waiting a moment or restart Docker Desktop"
        else
            echo "❌ Docker app is not running on macOS"
            echo "   Please start Docker Desktop application"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - check with systemctl
        if command -v systemctl &> /dev/null; then
            if systemctl is-active --quiet docker; then
                echo "🔍 Docker service is running but socket may have permission issues"
            else
                echo "❌ Docker service is not running"
                echo "   Start it with: sudo systemctl start docker"
            fi
        else
            echo "🔍 Unable to check Docker service status (systemctl not found)"
        fi
    elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
        # Windows
        echo "🔍 On Windows, make sure Docker Desktop is running"
        echo "   Check Docker Desktop tray icon or start the application"
    fi
    
    # Check socket existence and permissions
    echo "Checking Docker socket..."
    if [ -S /var/run/docker.sock ]; then
        echo "✅ Docker socket exists at /var/run/docker.sock"
        
        # Check permissions
        SOCKET_PERMS=$(ls -la /var/run/docker.sock | awk '{print $1}')
        SOCKET_OWNER=$(ls -la /var/run/docker.sock | awk '{print $3}')
        SOCKET_GROUP=$(ls -la /var/run/docker.sock | awk '{print $4}')
        
        echo "🔍 Socket permissions: $SOCKET_PERMS, Owner: $SOCKET_OWNER, Group: $SOCKET_GROUP"
        
        # Check if current user is in the socket group
        if groups | grep -q "$SOCKET_GROUP"; then
            echo "✅ Current user is in the $SOCKET_GROUP group"
        else
            echo "❌ Current user is NOT in the $SOCKET_GROUP group"
            echo "   Run: sudo usermod -aG $SOCKET_GROUP $USER"
            echo "   Then log out and log back in"
        fi
    else
        echo "❌ Docker socket not found at /var/run/docker.sock"
        
        # Check alternative socket location for macOS
        if [ -S $HOME/.docker/run/docker.sock ]; then
            echo "✅ Found Docker socket at $HOME/.docker/run/docker.sock"
            echo "🔍 You may need to set DOCKER_HOST environment variable:"
            echo "   export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock"
        else
            echo "❌ No Docker socket found at standard locations"
        fi
    fi
    
    # Check if Docker is configured for TCP
    echo "Checking for TCP connectivity..."
    if curl -s http://localhost:2375/_ping &> /dev/null; then
        echo "✅ Docker daemon is accessible via TCP on port 2375"
        echo "🔍 You can set: export DOCKER_HOST=tcp://localhost:2375"
    elif curl -s http://localhost:2376/_ping &> /dev/null; then
        echo "✅ Docker daemon is accessible via secure TCP on port 2376"
        echo "🔍 You can set: export DOCKER_HOST=tcp://localhost:2376"
    else
        echo "❌ Docker daemon is not accessible via TCP"
    fi
    
    echo "==========================================="
    echo "Recommended actions:"
    echo "1. Make sure Docker is running"
    echo "2. If using Docker Desktop, restart it and wait for it to fully initialize"
    echo "3. Check socket permissions and group membership"
    echo "4. For Trivy specifically, try running with sudo: sudo ./scan_docker_vulnerabilities.sh"
    
    exit 1
fi

# If we get here, basic Docker connectivity is working
# Now check if we can list images
echo "Checking image listing..."
if docker images &> /dev/null; then
    echo "✅ Can list Docker images"
else
    echo "❌ Cannot list Docker images (permission issue)"
    echo "   Try running Docker commands with sudo or add your user to the docker group"
    exit 1
fi

# Try a basic container operation
echo "Testing basic container operations..."
if docker run --rm hello-world &> /dev/null; then
    echo "✅ Can run containers"
else
    echo "❌ Cannot run containers (possible permission or configuration issue)"
    exit 1
fi

# Set up environment for Trivy
echo "Setting up environment for Trivy..."

# Try to detect if we need to set DOCKER_HOST
if [ ! -S /var/run/docker.sock ] && [ -S $HOME/.docker/run/docker.sock ]; then
    echo "🔍 Using alternative Docker socket location"
    export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock
    echo "✅ Set DOCKER_HOST to $DOCKER_HOST"
fi

echo "==========================================="
echo "✅ Docker connectivity check PASSED"
echo "You should now be able to run:"
echo "   ./scan_docker_vulnerabilities.sh"
echo "==========================================="

# Ask if user wants to build hello-world-api image
echo "Would you like to build the hello-world-api image now? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    if [ -f "Dockerfile" ]; then
        echo "Building hello-world-api image..."
        docker build -t hello-world-api .
        echo "✅ Image built successfully"
    else
        echo "❌ Dockerfile not found in current directory"
    fi
fi 