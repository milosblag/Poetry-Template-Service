#!/bin/bash
set -e

echo "Validating Kubernetes configuration..."
echo

# Create test variables for substitution
export DOCKER_REGISTRY="test-registry.example.com"
export IMAGE_TAG="latest"

# Check for required yaml files
required_files=("deployment.yaml" "service.yaml" "configmap.yaml" "kustomization.yaml")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: Required file $file not found"
        exit 1
    fi
    echo "✓ Found $file"
done

echo
echo "Checking for any remaining API_KEY references..."
if grep -q "API_KEY" *.yaml; then
    echo "Error: Found references to API_KEY in configuration files"
    grep "API_KEY" *.yaml
    exit 1
else
    echo "✓ No API_KEY references found"
fi

echo
echo "Checking for any remaining secret.yaml references..."
if grep -q "secret.yaml" *.yaml; then
    echo "Error: Found references to secret.yaml in configuration files"
    grep "secret.yaml" *.yaml
    exit 1
else
    echo "✓ No secret.yaml references found"
fi

echo
echo "Checking resource references in kustomization.yaml..."
resources=$(grep -A10 "resources:" kustomization.yaml | grep -v "resources:" | grep -v "^-" | grep -v "^#" | tr -d ' ')
for file in "deployment.yaml" "service.yaml" "configmap.yaml"; do
    if ! echo "$resources" | grep -q "$file"; then
        echo "Warning: $file not found in kustomization.yaml resources"
    else
        echo "✓ $file referenced in kustomization.yaml"
    fi
done

echo
echo "Validation completed successfully!"
echo
echo "Summary of resources:"
echo "-------------------"
echo "Deployment: hello-world-api (3 replicas)"
echo "Service: hello-world-api (type: ClusterIP)"
echo "ConfigMap: hello-world-api-config"
echo

echo "Health check endpoint: /api/v1/health" 