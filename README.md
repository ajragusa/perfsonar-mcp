# perfsonar-mcp

An MCP (Model Context Protocol) server for perfSONAR network measurement toolkit. This server allows AI agents to interact with perfSONAR measurement archives to query network performance metrics like throughput, latency, and packet loss.

## Features

- **Query Measurements**: Search for measurements with various filters (source, destination, event type, tool name)
- **Get Throughput Data**: Retrieve bandwidth/throughput measurements between hosts
- **Get Latency Data**: Retrieve delay/round-trip time measurements between hosts
- **Get Packet Loss Data**: Retrieve packet loss rate measurements between hosts
- **Get Raw Time Series Data**: Access raw measurement data with optional time-based summaries
- **Discover Event Types**: List all available measurement types in the archive

## Installation

```bash
npm install
npm run build
```

## Configuration

The server requires the `PERFSONAR_HOST` environment variable to be set:

```bash
export PERFSONAR_HOST=your-perfsonar-host.example.com
```

## Usage

### Running the Server

```bash
npm start
```

Or for development with auto-reload:

```bash
npm run dev
```

### Using with Claude Desktop

Add the following to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "perfsonar": {
      "command": "node",
      "args": ["/path/to/perfsonar-mcp/build/index.js"],
      "env": {
        "PERFSONAR_HOST": "your-perfsonar-host.example.com"
      }
    }
  }
}
```

### Using with Other MCP Clients

The server communicates via stdio and follows the Model Context Protocol specification. Any MCP-compatible client can use it.

## Available Tools

### query_measurements

Query perfSONAR measurements with optional filters.

**Parameters:**
- `source` (optional): Source host/IP address
- `destination` (optional): Destination host/IP address
- `eventType` (optional): Event type to filter (e.g., throughput, packet-loss-rate)
- `toolName` (optional): Tool name to filter (e.g., bwctl/iperf3, powstream)
- `timeRange` (optional): Time range in seconds from now

**Example:**
```json
{
  "source": "host1.example.com",
  "destination": "host2.example.com",
  "eventType": "throughput"
}
```

### get_measurement_data

Get raw time-series data for a specific measurement.

**Parameters:**
- `metadataKey` (required): Metadata key from query_measurements
- `eventType` (required): Event type (e.g., throughput, packet-loss-rate)
- `summaryType` (optional): Summary type (e.g., averages, statistics)
- `summaryWindow` (optional): Summary window in seconds (e.g., 3600 for hourly)
- `timeRange` (optional): Time range in seconds from now

### get_throughput

Get throughput measurements between two hosts.

**Parameters:**
- `source` (required): Source host/IP address
- `destination` (required): Destination host/IP address
- `timeRange` (optional): Time range in seconds (default: 86400 - 1 day)
- `summaryWindow` (optional): Summary window in seconds (e.g., 3600 for hourly)

### get_latency

Get latency/delay measurements between two hosts.

**Parameters:**
- `source` (required): Source host/IP address
- `destination` (required): Destination host/IP address
- `timeRange` (optional): Time range in seconds (default: 86400 - 1 day)
- `summaryWindow` (optional): Summary window in seconds (e.g., 3600 for hourly)

### get_packet_loss

Get packet loss measurements between two hosts.

**Parameters:**
- `source` (required): Source host/IP address
- `destination` (required): Destination host/IP address
- `timeRange` (optional): Time range in seconds (default: 86400 - 1 day)
- `summaryWindow` (optional): Summary window in seconds (e.g., 3600 for hourly)

### get_available_event_types

Get all available event types (measurement types) in the archive.

**Parameters:**
- `source` (optional): Filter by source host/IP address
- `destination` (optional): Filter by destination host/IP address

## Resources

The server provides a resource endpoint for the perfSONAR archive:

- `perfsonar://{PERFSONAR_HOST}/archive` - Main measurement archive

## perfSONAR API

This server uses the perfSONAR esmond measurement archive API. For more information:
- [perfSONAR Documentation](https://docs.perfsonar.net/)
- [esmond API Reference](https://docs.perfsonar.net/esmond_api_rest.html)

## Development

### Project Structure

```
src/
├── index.ts    # Main MCP server implementation
├── client.ts   # perfSONAR API client
└── types.ts    # TypeScript type definitions
```

### Building

```bash
npm run build
```

### Type Checking

```bash
npx tsc --noEmit
```

## License

MIT

