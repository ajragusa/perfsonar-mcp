# Deployment Guide

## Quick Start

### Local Development (stdio)

For local AI client integration:

```bash
# Install dependencies
pip install -e '.[dev]'

# Set configuration
export PERFSONAR_HOST=perfsonar.example.com

# Run the server
python -m perfsonar_mcp
```

### Local Web Server (SSE/HTTP)

For web-accessible MCP server:

```bash
# Install dependencies
pip install -e '.[dev]'

# Set configuration
export PERFSONAR_HOST=perfsonar.example.com

# Run with SSE transport (recommended)
fastmcp run src/perfsonar_mcp/fastmcp_server.py --transport sse --host 0.0.0.0 --port 8000

# Or use the convenience command
perfsonar-mcp-web

# Access at:
# - SSE endpoint: http://localhost:8000/sse
# - Health check: http://localhost:8000/health (if configured)
```

### Production Web Deployment

For production web deployment, use a process manager like systemd:

```bash
# /etc/systemd/system/perfsonar-mcp-web.service
[Unit]
Description=perfSONAR MCP Web Server
After=network.target

[Service]
Type=simple
User=perfsonar
WorkingDirectory=/opt/perfsonar-mcp
Environment="PERFSONAR_HOST=perfsonar.example.com"
Environment="LOOKUP_SERVICE_URL=https://lookup.perfsonar.net/lookup"
ExecStart=/usr/local/bin/fastmcp run /opt/perfsonar-mcp/src/perfsonar_mcp/fastmcp_server.py --transport sse --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable perfsonar-mcp-web
sudo systemctl start perfsonar-mcp-web
sudo systemctl status perfsonar-mcp-web
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

### Reverse Proxy (nginx)

For web deployment with SSL/TLS, use nginx as a reverse proxy:

```nginx
# /etc/nginx/sites-available/perfsonar-mcp
server {
    listen 443 ssl http2;
    server_name perfsonar-mcp.example.com;

    ssl_certificate /etc/ssl/certs/perfsonar-mcp.crt;
    ssl_certificate_key /etc/ssl/private/perfsonar-mcp.key;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # SSE endpoint
    location /sse {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE-specific settings
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
    }

    # Optional: Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name perfsonar-mcp.example.com;
    return 301 https://$server_name$request_uri;
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/perfsonar-mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
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
python -m perfsonar_mcp
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
