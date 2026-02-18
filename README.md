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

### Python (Recommended)

```bash
pip install -e .
```

### TypeScript

```bash
npm install && npm run build
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

### Python

```bash
python -m perfsonar_mcp
# or
perfsonar-mcp
```

### TypeScript

```bash
npm start
```

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

```
AI Agent (Claude)
    ↓ MCP Protocol
perfSONAR MCP Server
    ├── Measurement Archive Client
    ├── Lookup Service Client  
    └── pScheduler Client
```

## 🛠️ Development

### DevContainer

Open in VS Code → Reopen in Container

### Local

```bash
# Python
pip install -e '.[dev]'
black src/perfsonar_mcp/
ruff check src/perfsonar_mcp/

# TypeScript
npm run dev
```

## 📚 Documentation

- [TypeScript README](README-typescript.md)
- [Examples](EXAMPLES.md)
- [Contributing](CONTRIBUTING.md)

## 🌐 Resources

- [perfSONAR Docs](https://docs.perfsonar.net/)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 📄 License

MIT
