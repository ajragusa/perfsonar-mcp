# perfSONAR MCP Server Examples

This document provides example queries you can use with the perfSONAR MCP server.

## Basic Examples

### 1. Query All Measurements

Ask the AI agent:
```
Show me all measurements available in the perfSONAR archive
```

The agent will use the `query_measurements` tool to list all available measurements.

### 2. Get Throughput Between Two Hosts

Ask the AI agent:
```
Get the throughput measurements between host1.example.com and host2.example.com for the last day
```

The agent will use the `get_throughput` tool to retrieve bandwidth data.

### 3. Get Latency Data

Ask the AI agent:
```
What is the latency between source.example.com and destination.example.com?
```

The agent will use the `get_latency` tool to retrieve delay measurements.

### 4. Get Packet Loss

Ask the AI agent:
```
Show me packet loss data between 10.0.0.1 and 10.0.0.2
```

The agent will use the `get_packet_loss` tool to retrieve packet loss statistics.

### 5. Discover Available Measurements

Ask the AI agent:
```
What types of measurements are available in the perfSONAR archive?
```

The agent will use the `get_available_event_types` tool to list all event types.

## Advanced Examples

### 6. Get Hourly Throughput Averages

Ask the AI agent:
```
Get hourly average throughput between host1.example.com and host2.example.com for the last week
```

The agent will use the `get_throughput` tool with:
- `timeRange`: 604800 (7 days in seconds)
- `summaryWindow`: 3600 (1 hour in seconds)

### 7. Filter Measurements by Tool

Ask the AI agent:
```
Show me all iperf3 measurements between host1.example.com and host2.example.com
```

The agent will use the `query_measurements` tool with:
- `source`: host1.example.com
- `destination`: host2.example.com
- `toolName`: bwctl/iperf3

### 8. Get Specific Time Range Data

Ask the AI agent:
```
Get throughput data for the last 6 hours between source.example.com and destination.example.com
```

The agent will use the `get_throughput` tool with:
- `timeRange`: 21600 (6 hours in seconds)

### 9. Analyze Network Performance

Ask the AI agent:
```
Analyze the network performance between host1.example.com and host2.example.com. 
Show me throughput, latency, and packet loss for the last 24 hours.
```

The agent will use multiple tools:
- `get_throughput`
- `get_latency`
- `get_packet_loss`

### 10. Compare Multiple Routes

Ask the AI agent:
```
Compare network performance between:
- host1.example.com to host2.example.com
- host1.example.com to host3.example.com
Show throughput and latency for both paths.
```

The agent will make multiple calls to retrieve and compare data from different routes.

## Understanding the Data

### Timestamps
All timestamps in the data are Unix epoch timestamps (seconds since January 1, 1970 UTC).

### Throughput Values
Throughput values are typically in bits per second (bps).

### Latency Values
Latency values are in milliseconds (ms) or microseconds (μs) depending on the measurement type.

### Packet Loss Values
Packet loss rates are expressed as a decimal (e.g., 0.01 = 1% loss).

## Common Event Types

- `throughput`: Bandwidth/throughput measurements
- `packet-loss-rate`: Packet loss measurements
- `histogram-owdelay`: One-way delay histogram
- `histogram-rtt`: Round-trip time histogram
- `packet-count-sent`: Number of packets sent
- `packet-count-lost`: Number of packets lost
- `packet-retransmits`: TCP retransmission counts
- `failures`: Test failures

## Summary Windows

Common summary windows (in seconds):
- `300`: 5 minutes
- `3600`: 1 hour
- `86400`: 1 day

## Tips for Best Results

1. **Be Specific**: Provide exact hostnames or IP addresses when querying
2. **Use Time Ranges**: Specify time ranges to avoid large data sets
3. **Request Summaries**: Use summary windows for aggregated data over longer periods
4. **Check Event Types First**: Use `get_available_event_types` to see what's available
5. **Combine Queries**: Ask for multiple metrics in one question for comprehensive analysis
