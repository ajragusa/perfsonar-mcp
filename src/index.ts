#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { PerfSONARClient } from "./client.js";

// Configuration from environment variables
const PERFSONAR_HOST = process.env.PERFSONAR_HOST;

if (!PERFSONAR_HOST) {
  console.error("Error: PERFSONAR_HOST environment variable is required");
  process.exit(1);
}

// Initialize perfSONAR client
const client = new PerfSONARClient({ host: PERFSONAR_HOST });

// Define tool input schemas
const QueryMeasurementsArgsSchema = z.object({
  source: z.string().optional().describe("Source host/IP address"),
  destination: z.string().optional().describe("Destination host/IP address"),
  eventType: z
    .string()
    .optional()
    .describe(
      "Event type to filter (e.g., throughput, packet-loss-rate, histogram-owdelay)"
    ),
  toolName: z
    .string()
    .optional()
    .describe("Tool name to filter (e.g., bwctl/iperf3, powstream)"),
  timeRange: z
    .number()
    .optional()
    .describe("Time range in seconds from now to query"),
});

const GetMeasurementDataArgsSchema = z.object({
  metadataKey: z.string().describe("Metadata key from measurement query"),
  eventType: z.string().describe("Event type (e.g., throughput, packet-loss-rate)"),
  summaryType: z
    .string()
    .optional()
    .describe("Summary type (e.g., averages, statistics, aggregations)"),
  summaryWindow: z
    .number()
    .optional()
    .describe("Summary window in seconds (e.g., 3600 for hourly)"),
  timeRange: z
    .number()
    .optional()
    .describe("Time range in seconds from now to query"),
});

const GetThroughputArgsSchema = z.object({
  source: z.string().describe("Source host/IP address"),
  destination: z.string().describe("Destination host/IP address"),
  timeRange: z
    .number()
    .optional()
    .describe("Time range in seconds from now to query (default: 86400 - 1 day)"),
  summaryWindow: z
    .number()
    .optional()
    .describe("Summary window in seconds (e.g., 3600 for hourly averages)"),
});

const GetLatencyArgsSchema = z.object({
  source: z.string().describe("Source host/IP address"),
  destination: z.string().describe("Destination host/IP address"),
  timeRange: z
    .number()
    .optional()
    .describe("Time range in seconds from now to query (default: 86400 - 1 day)"),
  summaryWindow: z
    .number()
    .optional()
    .describe("Summary window in seconds (e.g., 3600 for hourly statistics)"),
});

const GetPacketLossArgsSchema = z.object({
  source: z.string().describe("Source host/IP address"),
  destination: z.string().describe("Destination host/IP address"),
  timeRange: z
    .number()
    .optional()
    .describe("Time range in seconds from now to query (default: 86400 - 1 day)"),
  summaryWindow: z
    .number()
    .optional()
    .describe("Summary window in seconds (e.g., 3600 for hourly aggregations)"),
});

const GetEventTypesArgsSchema = z.object({
  source: z.string().optional().describe("Source host/IP address to filter by"),
  destination: z
    .string()
    .optional()
    .describe("Destination host/IP address to filter by"),
});

// Create MCP server
const server = new Server(
  {
    name: "perfsonar-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "query_measurements",
        description:
          "Query perfSONAR measurements with optional filters. Returns metadata about available measurements including sources, destinations, event types, and tool names.",
        inputSchema: {
          type: "object",
          properties: {
            source: {
              type: "string",
              description: "Source host/IP address",
            },
            destination: {
              type: "string",
              description: "Destination host/IP address",
            },
            eventType: {
              type: "string",
              description:
                "Event type to filter (e.g., throughput, packet-loss-rate, histogram-owdelay)",
            },
            toolName: {
              type: "string",
              description: "Tool name to filter (e.g., bwctl/iperf3, powstream)",
            },
            timeRange: {
              type: "number",
              description: "Time range in seconds from now to query",
            },
          },
        },
      },
      {
        name: "get_measurement_data",
        description:
          "Get raw time-series data for a specific measurement. Requires a metadata key from query_measurements.",
        inputSchema: {
          type: "object",
          properties: {
            metadataKey: {
              type: "string",
              description: "Metadata key from measurement query",
            },
            eventType: {
              type: "string",
              description: "Event type (e.g., throughput, packet-loss-rate)",
            },
            summaryType: {
              type: "string",
              description:
                "Summary type (e.g., averages, statistics, aggregations)",
            },
            summaryWindow: {
              type: "number",
              description: "Summary window in seconds (e.g., 3600 for hourly)",
            },
            timeRange: {
              type: "number",
              description: "Time range in seconds from now to query",
            },
          },
          required: ["metadataKey", "eventType"],
        },
      },
      {
        name: "get_throughput",
        description:
          "Get throughput measurements between source and destination. Returns bandwidth/throughput data points over time.",
        inputSchema: {
          type: "object",
          properties: {
            source: {
              type: "string",
              description: "Source host/IP address",
            },
            destination: {
              type: "string",
              description: "Destination host/IP address",
            },
            timeRange: {
              type: "number",
              description:
                "Time range in seconds from now to query (default: 86400 - 1 day)",
            },
            summaryWindow: {
              type: "number",
              description:
                "Summary window in seconds (e.g., 3600 for hourly averages)",
            },
          },
          required: ["source", "destination"],
        },
      },
      {
        name: "get_latency",
        description:
          "Get latency/delay measurements between source and destination. Returns delay or round-trip time data points over time.",
        inputSchema: {
          type: "object",
          properties: {
            source: {
              type: "string",
              description: "Source host/IP address",
            },
            destination: {
              type: "string",
              description: "Destination host/IP address",
            },
            timeRange: {
              type: "number",
              description:
                "Time range in seconds from now to query (default: 86400 - 1 day)",
            },
            summaryWindow: {
              type: "number",
              description:
                "Summary window in seconds (e.g., 3600 for hourly statistics)",
            },
          },
          required: ["source", "destination"],
        },
      },
      {
        name: "get_packet_loss",
        description:
          "Get packet loss measurements between source and destination. Returns packet loss rate data points over time.",
        inputSchema: {
          type: "object",
          properties: {
            source: {
              type: "string",
              description: "Source host/IP address",
            },
            destination: {
              type: "string",
              description: "Destination host/IP address",
            },
            timeRange: {
              type: "number",
              description:
                "Time range in seconds from now to query (default: 86400 - 1 day)",
            },
            summaryWindow: {
              type: "number",
              description:
                "Summary window in seconds (e.g., 3600 for hourly aggregations)",
            },
          },
          required: ["source", "destination"],
        },
      },
      {
        name: "get_available_event_types",
        description:
          "Get all available event types (measurement types) from the perfSONAR archive. Can be filtered by source and/or destination.",
        inputSchema: {
          type: "object",
          properties: {
            source: {
              type: "string",
              description: "Source host/IP address to filter by",
            },
            destination: {
              type: "string",
              description: "Destination host/IP address to filter by",
            },
          },
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args } = request.params;

    switch (name) {
      case "query_measurements": {
        const parsed = QueryMeasurementsArgsSchema.parse(args);
        const params: any = {};
        if (parsed.source) params.source = parsed.source;
        if (parsed.destination) params.destination = parsed.destination;
        if (parsed.eventType) params["event-type"] = parsed.eventType;
        if (parsed.toolName) params["tool-name"] = parsed.toolName;
        if (parsed.timeRange) params["time-range"] = parsed.timeRange;

        const measurements = await client.queryMeasurements(params);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(measurements, null, 2),
            },
          ],
        };
      }

      case "get_measurement_data": {
        const parsed = GetMeasurementDataArgsSchema.parse(args);
        const data = await client.getMeasurementData({
          metadataKey: parsed.metadataKey,
          eventType: parsed.eventType,
          summaryType: parsed.summaryType,
          summaryWindow: parsed.summaryWindow,
          timeRange: parsed.timeRange,
        });
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(data, null, 2),
            },
          ],
        };
      }

      case "get_throughput": {
        const parsed = GetThroughputArgsSchema.parse(args);
        const results = await client.getThroughput(
          parsed.source,
          parsed.destination,
          {
            timeRange: parsed.timeRange || 86400,
            summaryWindow: parsed.summaryWindow,
          }
        );
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(results, null, 2),
            },
          ],
        };
      }

      case "get_latency": {
        const parsed = GetLatencyArgsSchema.parse(args);
        const results = await client.getLatency(parsed.source, parsed.destination, {
          timeRange: parsed.timeRange || 86400,
          summaryWindow: parsed.summaryWindow,
        });
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(results, null, 2),
            },
          ],
        };
      }

      case "get_packet_loss": {
        const parsed = GetPacketLossArgsSchema.parse(args);
        const results = await client.getPacketLoss(
          parsed.source,
          parsed.destination,
          {
            timeRange: parsed.timeRange || 86400,
            summaryWindow: parsed.summaryWindow,
          }
        );
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(results, null, 2),
            },
          ],
        };
      }

      case "get_available_event_types": {
        const parsed = GetEventTypesArgsSchema.parse(args);
        const eventTypes = await client.getAvailableEventTypes(
          parsed.source,
          parsed.destination
        );
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(eventTypes, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new Error(
        `Invalid arguments: ${error.issues.map((e) => `${e.path.join(".")}: ${e.message}`).join(", ")}`
      );
    }
    throw error;
  }
});

// List resources
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: `perfsonar://${PERFSONAR_HOST}/archive`,
        name: "perfSONAR Archive",
        description: "Main perfSONAR measurement archive",
        mimeType: "application/json",
      },
    ],
  };
});

// Read resource
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === `perfsonar://${PERFSONAR_HOST}/archive`) {
    const measurements = await client.queryMeasurements({});
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify(measurements, null, 2),
        },
      ],
    };
  }

  throw new Error(`Unknown resource: ${uri}`);
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("perfSONAR MCP server running on stdio");
  console.error(`Connected to perfSONAR host: ${PERFSONAR_HOST}`);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
