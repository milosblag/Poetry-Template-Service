# Kubernetes Deployment for Hello World API

This directory contains Kubernetes manifests for deploying the Hello World API to a Kubernetes cluster.

## Structure

- `deployment.yaml`: Defines the Kubernetes Deployment resource
- `service.yaml`: Defines the Kubernetes Service to expose the API
- `configmap.yaml`: Contains configuration for the application
- `kustomization.yaml`: Kustomize configuration for organizing resources

## Prerequisites

- Kubernetes cluster (1.19+)
- `kubectl` command-line tool
- Docker registry with the Hello World API image

## Deployment Instructions

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
# Check deployment status
kubectl get deployments

# Check pods
kubectl get pods -l app=hello-world-api

# Check service
kubectl get svc -l app=hello-world-api

```

### 5. Access the API

The API will be available at:
- Inside the cluster: `http://hello-world-api`
- Outside the cluster: `https://api.example.com` (replace with your domain)

## Configuration Options

### Scaling

To scale the deployment:

```bash
kubectl scale deployment hello-world-api --replicas=5
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
kubectl get pods -l app=hello-world-api

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
# From outside the cluster
curl https://api.example.com/api/v1/health

# From inside the cluster
kubectl run -it --rm --restart=Never curl-test --image=curlimages/curl -- curl http://hello-world-api/api/v1/health
``` 