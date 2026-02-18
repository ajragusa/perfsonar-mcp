# Deployment Guide

## Quick Start

### Local Development

```bash
# Python
pip install -e '.[dev]'
export PERFSONAR_HOST=perfsonar.example.com
python -m perfsonar_mcp

# TypeScript
npm install && npm run dev
export PERFSONAR_HOST=perfsonar.example.com
npm start
```

### Docker

1. Create `.env` file:
```bash
PERFSONAR_HOST=perfsonar.example.com
LOOKUP_SERVICE_URL=https://lookup.perfsonar.net/lookup
PSCHEDULER_URL=https://perfsonar.example.com/pscheduler
```

2. Build and run:
```bash
docker build -t perfsonar-mcp:latest .
docker-compose up -d
```

3. Check logs:
```bash
docker-compose logs -f
```

### Kubernetes with Helm

#### Prerequisites
- Kubernetes cluster (1.19+)
- Helm 3.x
- kubectl configured

#### Installation

1. **Create namespace:**
```bash
kubectl create namespace perfsonar
```

2. **Install with default values:**
```bash
helm install perfsonar-mcp ./helm/perfsonar-mcp \
  --namespace perfsonar \
  --set config.perfsonarHost=perfsonar.example.com
```

3. **Install with custom values:**

Create `values-production.yaml`:
```yaml
replicaCount: 3

config:
  perfsonarHost: "perfsonar.example.com"
  lookupServiceUrl: "https://lookup.perfsonar.net/lookup"

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

nodeSelector:
  workload: monitoring

tolerations:
  - key: "monitoring"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
```

Install:
```bash
helm install perfsonar-mcp ./helm/perfsonar-mcp \
  --namespace perfsonar \
  -f values-production.yaml
```

4. **Verify deployment:**
```bash
kubectl get pods -n perfsonar
kubectl logs -n perfsonar deployment/perfsonar-mcp
```

5. **Upgrade:**
```bash
helm upgrade perfsonar-mcp ./helm/perfsonar-mcp \
  --namespace perfsonar \
  -f values-production.yaml
```

6. **Uninstall:**
```bash
helm uninstall perfsonar-mcp --namespace perfsonar
```

#### Accessing the Service

The MCP server uses stdio transport by default. For integration with AI agents:

1. **Port-forward for testing:**
```bash
kubectl port-forward -n perfsonar svc/perfsonar-mcp 8000:8000
```

2. **Expose via Ingress** (if using HTTP transport in future):
```yaml
# Add to values.yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: perfsonar-mcp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: perfsonar-mcp-tls
      hosts:
        - perfsonar-mcp.example.com
```

### DevContainer (VS Code)

1. **Install prerequisites:**
   - Docker Desktop
   - VS Code with Remote-Containers extension

2. **Open in container:**
   - Open project in VS Code
   - Click "Reopen in Container" when prompted
   - All dependencies auto-installed

3. **Start development:**
```bash
# Python
python -m perfsonar_mcp

# TypeScript
npm run dev
```

## Environment Variables

### Required
- `PERFSONAR_HOST` - Your perfSONAR host (e.g., perfsonar.example.com)

### Optional
- `LOOKUP_SERVICE_URL` - Lookup service endpoint (default: https://lookup.perfsonar.net/lookup)
- `PSCHEDULER_URL` - pScheduler endpoint (default: https://{PERFSONAR_HOST}/pscheduler)

## Configuration Examples

### Claude Desktop

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "perfsonar": {
      "command": "python",
      "args": ["-m", "perfsonar_mcp"],
      "env": {
        "PERFSONAR_HOST": "perfsonar.example.com"
      }
    }
  }
}
```

### Docker Compose

```yaml
version: '3.8'

services:
  perfsonar-mcp:
    image: perfsonar-mcp:latest
    container_name: perfsonar-mcp
    environment:
      - PERFSONAR_HOST=perfsonar.example.com
      - LOOKUP_SERVICE_URL=https://lookup.perfsonar.net/lookup
    restart: unless-stopped
    stdin_open: true
    tty: true
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: perfsonar-mcp-config
data:
  perfsonarHost: "perfsonar.example.com"
  lookupServiceUrl: "https://lookup.perfsonar.net/lookup"
  pschedulerUrl: "https://perfsonar.example.com/pscheduler"
```

## Troubleshooting

### Python

**Import errors:**
```bash
pip install -e .
# or
PYTHONPATH=/path/to/src:$PYTHONPATH python -m perfsonar_mcp
```

**Connection errors:**
```bash
# Check perfSONAR host is accessible
curl http://perfsonar.example.com/esmond/perfsonar/archive/

# Check environment variable
echo $PERFSONAR_HOST
```

### Docker

**Build errors:**
```bash
# Clean build
docker build --no-cache -t perfsonar-mcp:latest .
```

**Container not starting:**
```bash
docker logs perfsonar-mcp
```

### Kubernetes

**Pods not starting:**
```bash
kubectl describe pod -n perfsonar <pod-name>
kubectl logs -n perfsonar <pod-name>
```

**ConfigMap issues:**
```bash
kubectl get configmap -n perfsonar perfsonar-mcp-config -o yaml
```

**Resource limits:**
```bash
# Check node resources
kubectl top nodes
kubectl top pods -n perfsonar
```

## Monitoring

### Health Checks

Currently uses stdio transport, so health checks are based on process state.

### Logs

**Docker:**
```bash
docker-compose logs -f perfsonar-mcp
```

**Kubernetes:**
```bash
kubectl logs -f -n perfsonar deployment/perfsonar-mcp
kubectl logs -n perfsonar -l app.kubernetes.io/name=perfsonar-mcp --tail=100
```

### Metrics

Future enhancement: Add Prometheus metrics for:
- Request counts
- Response times
- Error rates
- Active connections

## Security

### Best Practices

1. **Network Security:**
   - Use TLS for all perfSONAR connections
   - Restrict network access with firewall rules
   - Use private networks in Kubernetes

2. **Secrets Management:**
   - Store credentials in Kubernetes Secrets
   - Use external secret managers (Vault, AWS Secrets Manager)
   - Rotate credentials regularly

3. **Container Security:**
   - Run as non-root user (UID 1000)
   - Use read-only root filesystem
   - Scan images for vulnerabilities

4. **RBAC:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: perfsonar-mcp-role
  namespace: perfsonar
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list"]
```

## Backup and Recovery

### Configuration Backup

```bash
# Helm values
helm get values perfsonar-mcp -n perfsonar > backup-values.yaml

# Kubernetes manifests
kubectl get all -n perfsonar -o yaml > backup-manifests.yaml
```

### Restore

```bash
helm install perfsonar-mcp ./helm/perfsonar-mcp \
  -n perfsonar \
  -f backup-values.yaml
```

## Performance Tuning

### Resource Allocation

Adjust based on workload:

```yaml
resources:
  limits:
    cpu: 2000m      # For high request volume
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

### Autoscaling

```yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### Connection Pooling

HTTP client uses connection pooling by default. Tune in code if needed.

## Upgrading

### Docker

```bash
# Build new version
docker build -t perfsonar-mcp:1.1.0 .

# Update compose
# Edit docker-compose.yml to use new tag

# Pull and restart
docker-compose pull
docker-compose up -d
```

### Kubernetes

```bash
# Update chart version
helm upgrade perfsonar-mcp ./helm/perfsonar-mcp \
  --namespace perfsonar \
  -f values-production.yaml

# Rollback if needed
helm rollback perfsonar-mcp -n perfsonar
```

## Support

- GitHub Issues: https://github.com/ajragusa/perfsonar-mcp/issues
- perfSONAR Docs: https://docs.perfsonar.net/
- MCP Protocol: https://modelcontextprotocol.io/
