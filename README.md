# perfsonar-mcp

MCP (Model Context Protocol) server for perfSONAR - Query measurements, discover testpoints, and schedule network tests.

## 🚀 Features

### Measurement Archive Queries
- Query historical measurements with filters
- Get throughput, latency, and packet loss data
- Access raw time-series data with summaries
- Discover available measurement types

### Lookup Service Integration  
- Find perfSONAR testpoints globally
- Search by location (city, country)
- Locate pScheduler services for testing

### Test Scheduling (pScheduler)
- Schedule throughput tests (iperf3)
- Schedule latency tests (owping)
- Schedule RTT tests (ping)
- Monitor test status and retrieve results

## 📦 Installation

```bash
pip install -e .
```

For development with additional tools:

```bash
pip install -e '.[dev]'
```

## ⚙️ Configuration

Required environment variable:

```bash
export PERFSONAR_HOST=perfsonar.example.com
```

Optional:

```bash
export LOOKUP_SERVICE_URL=https://lookup.perfsonar.net/lookup
export PSCHEDULER_URL=https://perfsonar.example.com/pscheduler
```

## 🏃 Usage

### Local (stdio transport)

Standard MCP stdio transport for local AI clients:

```bash
python -m perfsonar_mcp
# or
perfsonar-mcp
```

### Web Access (SSE/HTTP transport)

FastMCP enables web-accessible MCP server via SSE (Server-Sent Events) or HTTP:

```bash
# SSE transport (recommended for web)
export PERFSONAR_HOST=perfsonar.example.com
fastmcp run src/perfsonar_mcp/fastmcp_server.py --transport sse --host 0.0.0.0 --port 8000

# HTTP transport (alternative)
fastmcp run src/perfsonar_mcp/fastmcp_server.py --transport http --host 0.0.0.0 --port 8000

# Or use the convenience command
perfsonar-mcp-web
```

The server will be accessible at:
- SSE: `http://your-host:8000/sse`
- HTTP: `http://your-host:8000/mcp/`

### Docker

```bash
docker-compose up -d
```

### Kubernetes

```bash
helm install perfsonar-mcp ./helm/perfsonar-mcp \
  --set config.perfsonarHost=perfsonar.example.com
```

## 🤖 Claude Desktop Integration

Add to your `claude_desktop_config.json`:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "perfsonar": {
      "command": "python",
      "args": ["-m", "perfsonar_mcp"],
      "env": {
        "PERFSONAR_HOST": "your-perfsonar-host.example.com"
      }
    }
  }
}
```

For web-based access, use the SSE endpoint:

```json
{
  "mcpServers": {
    "perfsonar-web": {
      "url": "http://your-server:8000/sse",
      "transport": "sse"
    }
  }
}
```

## 🔧 Available Tools (13)

### Measurement Archive (6)
- `query_measurements` - Search measurements
- `get_throughput` - Throughput data
- `get_latency` - Latency data
- `get_packet_loss` - Packet loss data
- `get_measurement_data` - Raw time-series
- `get_available_event_types` - List types

### Lookup Service (2)
- `lookup_testpoints` - Find testpoints
- `find_pscheduler_services` - Find pScheduler

### pScheduler (5)
- `schedule_throughput_test` - Run throughput test
- `schedule_latency_test` - Run latency test
- `schedule_rtt_test` - Run RTT test
- `get_test_status` - Check status
- `get_test_result` - Get results

## 💡 Example Queries

Ask Claude:

> "Find perfSONAR testpoints in Europe"

> "Schedule a 30-second throughput test to host.example.com"

> "Get hourly throughput averages between host1 and host2 for the last week"

## 🏗️ Architecture

### Standard MCP (stdio)
```
AI Agent (Claude)
    ↓ MCP Protocol (stdio)
perfSONAR MCP Server (Python)
    ├── Measurement Archive Client
    ├── Lookup Service Client  
    └── pScheduler Client
        ↓
    perfSONAR Services
```

### Web-Accessible MCP (SSE/HTTP)
```
Web Clients / AI Agents
    ↓ HTTP/SSE
FastMCP Web Server (uvicorn)
    ↓ MCP Protocol
perfSONAR MCP Server (Python)
    ├── Measurement Archive Client
    ├── Lookup Service Client  
    └── pScheduler Client
        ↓
    perfSONAR Services
```

Both transports expose the same tools and capabilities. The web transport enables:
- Remote access from any HTTP client
- Multiple concurrent connections
- Integration with web-based AI applications
- RESTful API-like access patterns

## 🛠️ Development

### Logging

The server includes comprehensive logging for development and debugging. By default, logs are written to stderr at INFO level.

To enable DEBUG logging for more detailed output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set the log level via environment variable:

```bash
export PYTHONLOGLEVEL=DEBUG
python -m perfsonar_mcp
```

Log output includes:
- Server initialization and configuration
- API requests and responses
- Tool invocations with arguments
- Error details with stack traces

### DevContainer

Open in VS Code → Reopen in Container

### Local Development

```bash
# Install with dev dependencies
pip install -e '.[dev]'

# Format code
black src/perfsonar_mcp/

# Lint code
ruff check src/perfsonar_mcp/

# Type check
mypy src/perfsonar_mcp/

# Run tests
pytest tests/
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md)
- [Examples](EXAMPLES.md)
- [Contributing](CONTRIBUTING.md)

## 🌐 Resources

- [perfSONAR Docs](https://docs.perfsonar.net/)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 📄 License

MIT
