#!/bin/bash
set -e

echo "Validating Kubernetes configuration..."
echo

# Default service name to detect if user has renamed it
DEFAULT_SERVICE_NAME="hello-world-api"

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
echo "Checking if the service has been renamed from the default example..."
service_name=$(grep -o 'app: .*' deployment.yaml | head -1 | cut -d' ' -f2)
if [ "$service_name" = "$DEFAULT_SERVICE_NAME" ]; then
    echo "⚠️  WARNING: You are still using the default service name '$DEFAULT_SERVICE_NAME'"
    echo "    This is an example template service. You MUST rename it to your actual service name."
    echo "    Rename the service in ALL files, not just YAML files!"
    echo "    Don't forget to update:"
    echo "     - YAML configuration files (deployment.yaml, service.yaml, etc.)"
    echo "     - This validation script (validate-config.sh)"
    echo "     - The README.md file"
    echo "     - Any commands or examples"
    echo "    See the 'Renaming the Service' section in README.md for complete instructions."
else
    echo "✓ Service has been renamed to: $service_name"
fi

echo
echo "Checking for any remaining API_KEY references in configuration files..."
if grep -q "API_KEY" *.yaml 2>/dev/null; then
    echo "Error: Found references to API_KEY in configuration files"
    grep "API_KEY" *.yaml
    exit 1
else
    echo "✓ No API_KEY references found in configuration files"
fi

echo
echo "Checking for any remaining secret.yaml references in configuration files..."
if grep -q "secret.yaml" *.yaml 2>/dev/null; then
    echo "Error: Found references to secret.yaml in configuration files"
    grep "secret.yaml" *.yaml
    exit 1
else
    echo "✓ No secret.yaml references found in configuration files"
fi

echo
echo "Checking for any ingress.yaml references in configuration files..."
if grep -q "ingress.yaml" *.yaml 2>/dev/null; then
    echo "Warning: Found references to ingress.yaml in configuration files, but ingress has been removed"
    grep "ingress.yaml" *.yaml
else
    echo "✓ No ingress.yaml references found in configuration files"
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
echo "Checking documentation completeness..."
if [ -f "README.md" ]; then
    echo "✓ README.md exists"
    # Check if the README still contains the default service name
    if [ "$service_name" != "$DEFAULT_SERVICE_NAME" ] && grep -q "$DEFAULT_SERVICE_NAME" README.md; then
        echo "⚠️  WARNING: You've renamed the service to '$service_name' but README.md still contains references to '$DEFAULT_SERVICE_NAME'"
        echo "    Update the README.md to match your service name."
        echo "    Tip: Use this command to update all files:"
        echo "      find . -type f -exec sed -i 's/$DEFAULT_SERVICE_NAME/$service_name/g' {} \;"
        echo "    (On macOS, use: find . -type f -exec sed -i '' 's/$DEFAULT_SERVICE_NAME/$service_name/g' {} \;)"
    fi
else
    echo "Warning: README.md not found, documentation is missing"
fi

# Also check if this script itself still has hardcoded default values
if [ "$service_name" != "$DEFAULT_SERVICE_NAME" ] && grep -q "DEFAULT_SERVICE_NAME=\"$DEFAULT_SERVICE_NAME\"" "$0"; then
    echo "⚠️  WARNING: You've renamed the service to '$service_name' but this validation script still has"
    echo "    the default service name hardcoded. Update the DEFAULT_SERVICE_NAME variable in this script."
fi

echo
echo "Validation completed successfully!"
echo
echo "Summary of resources:"
echo "-------------------"
if [ "$service_name" = "$DEFAULT_SERVICE_NAME" ]; then
    echo "⚠️  USING DEFAULT EXAMPLE SERVICE NAME: $DEFAULT_SERVICE_NAME"
    echo "    You MUST rename this service before deploying to production!"
    echo "    See README.md for instructions on how to rename ALL files, not just YAML files."
else
    echo "Service: $service_name"
fi
echo "Deployment: 3 replicas"
echo "Service type: ClusterIP"
echo "ConfigMap: ${service_name}-config"
echo

echo "Health check endpoint: /api/v1/health"

echo
if [ "$service_name" = "$DEFAULT_SERVICE_NAME" ]; then
    echo "⚠️  FINAL REMINDER: This is an example service with the default name '$DEFAULT_SERVICE_NAME'."
    echo "   You MUST rename it to your actual service name before deploying to production."
    echo "   Use 'find . -type f -exec sed -i 's/$DEFAULT_SERVICE_NAME/your-service-name/g' {} \;'"
    echo "   to rename the service in ALL files, not just YAML files."
    echo "   See the 'Renaming the Service' section in README.md for complete instructions."
else
    echo "Note: Service has been successfully renamed from the default template."
fi 