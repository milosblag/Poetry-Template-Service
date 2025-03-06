# Kubernetes Deployment for Hello World API

This directory contains Kubernetes manifests for deploying the Hello World API to a Kubernetes cluster. This is provided as an **example service** that you can use as a starting point and customize for your own applications.

> **IMPORTANT**: This is a template service named `hello-world-api`. You **MUST** rename it to your actual service name before deploying to production.
> **REPLACE THE NAME IN ALL FILES, NOT JUST YAML FILES.**

## About This Example

The Hello World API is a simple RESTful service that demonstrates best practices for:
- Kubernetes deployment configuration
- Health check implementation
- Environment variable configuration
- Service exposure

## Structure

- `deployment.yaml`: Defines the Kubernetes Deployment resource
- `service.yaml`: Defines the Kubernetes Service to expose the API
- `configmap.yaml`: Contains configuration for the application
- `kustomization.yaml`: Kustomize configuration for organizing resources
- `validate-config.sh`: Validation script for checking your configuration
- `README.md`: This documentation file

## Prerequisites

- Kubernetes cluster (1.19+)
- `kubectl` command-line tool
- Docker registry with your application image

## Deployment Instructions

### 0. Rename This Service First! (Required)

⚠️ **Before proceeding, you MUST rename this example service** to match your actual application name. See the detailed steps in the [Renaming the Service](#renaming-the-service) section below.

### 1. Prepare Configuration

Edit `configmap.yaml` to set appropriate environment variables for your deployment.

### 2. Set Deployment Variables

Create a `.env` file with the following variables:
```
DOCKER_REGISTRY=your-registry.example.com
IMAGE_TAG=latest
```

### 3. Deploy with Kustomize

```bash
# Export variables for use in manifests
export $(cat .env | xargs)

# Apply using kustomize
kubectl apply -k .
```

### 4. Verify Deployment

```bash
# Replace YOUR-SERVICE-NAME with your actual service name in the commands below
# Check deployment status
kubectl get deployments

# Check pods
kubectl get pods -l app=YOUR-SERVICE-NAME

# Check service
kubectl get svc -l app=YOUR-SERVICE-NAME
```

### 5. Access the API

The API will be available at:
- Inside the cluster: `http://YOUR-SERVICE-NAME`
- For external access, you'll need to set up your own ingress controller or use a LoadBalancer service type

## Customizing This Example

### Renaming the Service

⚠️ **YOU MUST REPLACE `hello-world-api` WITH YOUR ACTUAL SERVICE NAME** ⚠️

This is a template service with the placeholder name `hello-world-api`. Before deploying, you must replace this name with your own service name in **ALL FILES**:

1. **Update ALL files in the directory**:
   ```bash
   # Find and replace all occurrences of hello-world-api with your actual service name
   # For example, if your service is called "payment-processor":
   find . -type f -exec sed -i 's/hello-world-api/payment-processor/g' {} \;
   ```

   This will update:
   - All YAML configuration files (deployment.yaml, service.yaml, etc.)
   - The validate-config.sh script
   - This README.md file
   
   > On macOS, use: `find . -type f -exec sed -i '' 's/hello-world-api/payment-processor/g' {} \;`

2. **Specifically check these locations**:

   a. **YAML configurations**:
      - Labels and selectors in all YAML files
      - Service and deployment names
      - ConfigMap names and references
      
   b. **The validation script**:
      - The `DEFAULT_SERVICE_NAME` variable in `validate-config.sh`
      - Any hardcoded service names in verification messages
      
   c. **Documentation**:
      - All occurrences in README.md
      - Any example commands that contain the service name
      
   d. **Shell commands**:
      - Any kubectl commands or examples
      - Health check URLs and endpoints

3. **Update the ConfigMap name**:
   
   Before:
   ```yaml
   # In kustomization.yaml
   configMapGenerator:
   - name: hello-world-api-config
   ```
   
   After:
   ```yaml
   # In kustomization.yaml
   configMapGenerator:
   - name: payment-processor-config
   ```
   
   Also update the reference in deployment.yaml:
   
   Before:
   ```yaml
   # In deployment.yaml
   envFrom:
   - configMapRef:
       name: hello-world-api-config
   ```
   
   After:
   ```yaml
   # In deployment.yaml
   envFrom:
   - configMapRef:
       name: payment-processor-config
   ```

4. **Update health check paths** in `deployment.yaml` if your health endpoint differs from `/api/v1/health`

5. **Update container ports** in `deployment.yaml` and service target ports in `service.yaml` if your application uses different ports

6. **Verify changes**:
   ```bash
   # Run the validation script to verify your changes
   ./validate-config.sh
   ```
   
   The validation script should now report your new service name and not show any warnings about using the default name.

### Adding New API Endpoints

To extend this example with additional endpoints:

1. **Implement new endpoints in your application code**:
   - Add new routes in your API framework
   - Ensure proper documentation for each endpoint
   - Add appropriate authentication if needed

2. **Update health checks** if necessary:
   - If you add critical endpoints, consider including them in health check monitoring
   - Update the readiness/liveness probe configuration in `deployment.yaml`

3. **Update ConfigMap** with any new environment variables needed for your endpoints:
   ```yaml
   # In configmap.yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: YOUR-SERVICE-NAME-config  # Use your actual service name here!
   data:
     # Add new environment variables here
     NEW_ENDPOINT_CONFIG: "value"
   ```

4. **Consider resource requirements**:
   - If new endpoints significantly change resource usage, update requests/limits in `deployment.yaml`

5. **Document your new endpoints** in your API documentation

## Configuration Options

### Scaling

To scale the deployment:

```bash
# Replace YOUR-SERVICE-NAME with your actual service name
kubectl scale deployment YOUR-SERVICE-NAME --replicas=5
```

### Resource Limits

Edit `deployment.yaml` to adjust CPU and memory requests/limits based on your workload.

### Environment-Specific Configuration

Use Kustomize overlays for different environments:

1. Create an overlay directory:
   ```
   kubernetes/
   ├── base/
   │   └── ... (move all files here)
   └── overlays/
       ├── development/
       │   └── kustomization.yaml
       └── production/
           └── kustomization.yaml
   ```

2. Configure environment-specific settings in each overlay's kustomization.yaml

## Troubleshooting

### Check Logs

```bash
# Get pod names
kubectl get pods -l app=YOUR-SERVICE-NAME

# View logs for a specific pod
kubectl logs <pod-name>
```

### Check Events

```bash
kubectl get events --sort-by='.lastTimestamp'
```

### Health Check

The API exposes a health endpoint at `/api/v1/health`. You can check it using:

```bash
# From inside the cluster (replace YOUR-SERVICE-NAME with your actual service name)
kubectl run -it --rm --restart=Never curl-test --image=curlimages/curl -- curl http://YOUR-SERVICE-NAME/api/v1/health
```

## Contributing

If you improve this example service, please consider contributing your changes back to the original repository. 