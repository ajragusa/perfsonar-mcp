"""
MCP Server for perfSONAR
"""

import asyncio
import json
import os
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    Resource,
    ReadResourceResult,
)

from .client import PerfSONARClient
from .lookup import LookupServiceClient
from .pscheduler import PSchedulerClient
from .types import (
    PerfSONARConfig,
    MeasurementQueryParams,
    MeasurementDataParams,
    LookupQueryParams,
)


class PerfSONARMCPServer:
    """MCP Server for perfSONAR"""

    def __init__(self):
        self.server = Server("perfsonar-mcp")
        self.perfsonar_host = os.getenv("PERFSONAR_HOST")
        self.lookup_service_url = os.getenv(
            "LOOKUP_SERVICE_URL", "https://lookup.perfsonar.net/lookup"
        )
        
        if not self.perfsonar_host:
            raise ValueError("PERFSONAR_HOST environment variable is required")
        
        self.client = PerfSONARClient(PerfSONARConfig(host=self.perfsonar_host))
        self.lookup_client = LookupServiceClient(self.lookup_service_url)
        self.pscheduler_url = os.getenv(
            "PSCHEDULER_URL", f"https://{self.perfsonar_host}/pscheduler"
        )
        self.pscheduler_client = PSchedulerClient(self.pscheduler_url)
        
        self.setup_handlers()

    def setup_handlers(self):
        """Setup MCP request handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="query_measurements",
                    description="Query perfSONAR measurements with optional filters. Returns metadata about available measurements.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {"type": "string", "description": "Source host/IP address"},
                            "destination": {"type": "string", "description": "Destination host/IP address"},
                            "eventType": {"type": "string", "description": "Event type to filter"},
                            "toolName": {"type": "string", "description": "Tool name to filter"},
                            "timeRange": {"type": "number", "description": "Time range in seconds"},
                        },
                    },
                ),
                Tool(
                    name="get_measurement_data",
                    description="Get raw time-series data for a specific measurement.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "metadataKey": {"type": "string", "description": "Metadata key from query"},
                            "eventType": {"type": "string", "description": "Event type"},
                            "summaryType": {"type": "string", "description": "Summary type"},
                            "summaryWindow": {"type": "number", "description": "Summary window in seconds"},
                            "timeRange": {"type": "number", "description": "Time range in seconds"},
                        },
                        "required": ["metadataKey", "eventType"],
                    },
                ),
                Tool(
                    name="get_throughput",
                    description="Get throughput measurements between source and destination.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {"type": "string", "description": "Source host/IP address"},
                            "destination": {"type": "string", "description": "Destination host/IP address"},
                            "timeRange": {"type": "number", "description": "Time range in seconds"},
                            "summaryWindow": {"type": "number", "description": "Summary window in seconds"},
                        },
                        "required": ["source", "destination"],
                    },
                ),
                Tool(
                    name="get_latency",
                    description="Get latency/delay measurements between source and destination.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {"type": "string", "description": "Source host/IP address"},
                            "destination": {"type": "string", "description": "Destination host/IP address"},
                            "timeRange": {"type": "number", "description": "Time range in seconds"},
                            "summaryWindow": {"type": "number", "description": "Summary window in seconds"},
                        },
                        "required": ["source", "destination"],
                    },
                ),
                Tool(
                    name="get_packet_loss",
                    description="Get packet loss measurements between source and destination.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {"type": "string", "description": "Source host/IP address"},
                            "destination": {"type": "string", "description": "Destination host/IP address"},
                            "timeRange": {"type": "number", "description": "Time range in seconds"},
                            "summaryWindow": {"type": "number", "description": "Summary window in seconds"},
                        },
                        "required": ["source", "destination"],
                    },
                ),
                Tool(
                    name="get_available_event_types",
                    description="Get all available event types in the archive.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {"type": "string", "description": "Source filter"},
                            "destination": {"type": "string", "description": "Destination filter"},
                        },
                    },
                ),
                Tool(
                    name="lookup_testpoints",
                    description="Find perfSONAR testpoints using the lookup service.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "serviceType": {"type": "string", "description": "Service type filter"},
                            "locationCity": {"type": "string", "description": "City filter"},
                            "locationCountry": {"type": "string", "description": "Country filter"},
                        },
                    },
                ),
                Tool(
                    name="find_pscheduler_services",
                    description="Find pScheduler services for running tests.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "locationCity": {"type": "string", "description": "City filter"},
                            "locationCountry": {"type": "string", "description": "Country filter"},
                        },
                    },
                ),
                Tool(
                    name="schedule_throughput_test",
                    description="Schedule a throughput test using pScheduler.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {"type": "string", "description": "Source host (optional)"},
                            "dest": {"type": "string", "description": "Destination host"},
                            "duration": {"type": "string", "description": "Test duration (e.g., PT30S)"},
                        },
                        "required": ["dest"],
                    },
                ),
                Tool(
                    name="schedule_latency_test",
                    description="Schedule a latency test using pScheduler.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {"type": "string", "description": "Source host (optional)"},
                            "dest": {"type": "string", "description": "Destination host"},
                            "packetCount": {"type": "number", "description": "Number of packets"},
                            "packetInterval": {"type": "number", "description": "Interval between packets"},
                        },
                        "required": ["dest"],
                    },
                ),
                Tool(
                    name="schedule_rtt_test",
                    description="Schedule an RTT (ping) test using pScheduler.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dest": {"type": "string", "description": "Destination host"},
                            "count": {"type": "number", "description": "Number of pings"},
                        },
                        "required": ["dest"],
                    },
                ),
                Tool(
                    name="get_test_status",
                    description="Get status of a pScheduler test run.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "runUrl": {"type": "string", "description": "Run URL from test scheduling"},
                        },
                        "required": ["runUrl"],
                    },
                ),
                Tool(
                    name="get_test_result",
                    description="Get result of a completed pScheduler test.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "runUrl": {"type": "string", "description": "Run URL from test scheduling"},
                        },
                        "required": ["runUrl"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> CallToolResult:
            try:
                if name == "query_measurements":
                    params = MeasurementQueryParams(
                        source=arguments.get("source"),
                        destination=arguments.get("destination"),
                        event_type=arguments.get("eventType"),
                        tool_name=arguments.get("toolName"),
                        time_range=arguments.get("timeRange"),
                    )
                    results = await self.client.query_measurements(params)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps([r.model_dump(by_alias=True) for r in results], indent=2),
                            )
                        ]
                    )

                elif name == "get_measurement_data":
                    params = MeasurementDataParams(
                        metadata_key=arguments["metadataKey"],
                        event_type=arguments["eventType"],
                        summary_type=arguments.get("summaryType"),
                        summary_window=arguments.get("summaryWindow"),
                        time_range=arguments.get("timeRange"),
                    )
                    results = await self.client.get_measurement_data(params)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps([r.model_dump() for r in results], indent=2),
                            )
                        ]
                    )

                elif name == "get_throughput":
                    results = await self.client.get_throughput(
                        arguments["source"],
                        arguments["destination"],
                        arguments.get("timeRange", 86400),
                        arguments.get("summaryWindow"),
                    )
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps([r.model_dump(by_alias=True) for r in results], indent=2),
                            )
                        ]
                    )

                elif name == "get_latency":
                    results = await self.client.get_latency(
                        arguments["source"],
                        arguments["destination"],
                        arguments.get("timeRange", 86400),
                        arguments.get("summaryWindow"),
                    )
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps([r.model_dump(by_alias=True) for r in results], indent=2),
                            )
                        ]
                    )

                elif name == "get_packet_loss":
                    results = await self.client.get_packet_loss(
                        arguments["source"],
                        arguments["destination"],
                        arguments.get("timeRange", 86400),
                        arguments.get("summaryWindow"),
                    )
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps([r.model_dump(by_alias=True) for r in results], indent=2),
                            )
                        ]
                    )

                elif name == "get_available_event_types":
                    results = await self.client.get_available_event_types(
                        arguments.get("source"), arguments.get("destination")
                    )
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps(results, indent=2))]
                    )

                elif name == "lookup_testpoints":
                    results = await self.lookup_client.find_testpoints(
                        arguments.get("serviceType"),
                        arguments.get("locationCity"),
                        arguments.get("locationCountry"),
                    )
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps([r.model_dump(by_alias=True) for r in results], indent=2),
                            )
                        ]
                    )

                elif name == "find_pscheduler_services":
                    results = await self.lookup_client.find_pscheduler_services(
                        arguments.get("locationCity"), arguments.get("locationCountry")
                    )
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps([r.model_dump(by_alias=True) for r in results], indent=2),
                            )
                        ]
                    )

                elif name == "schedule_throughput_test":
                    result = await self.pscheduler_client.schedule_throughput_test(
                        arguments.get("source"),
                        arguments["dest"],
                        arguments.get("duration", "PT30S"),
                    )
                    return CallToolResult(
                        content=[
                            TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))
                        ]
                    )

                elif name == "schedule_latency_test":
                    result = await self.pscheduler_client.schedule_latency_test(
                        arguments.get("source"),
                        arguments["dest"],
                        arguments.get("packetCount", 600),
                        arguments.get("packetInterval", 0.1),
                    )
                    return CallToolResult(
                        content=[
                            TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))
                        ]
                    )

                elif name == "schedule_rtt_test":
                    result = await self.pscheduler_client.schedule_rtt_test(
                        arguments["dest"], arguments.get("count", 10)
                    )
                    return CallToolResult(
                        content=[
                            TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))
                        ]
                    )

                elif name == "get_test_status":
                    result = await self.pscheduler_client.get_run_status(arguments["runUrl"])
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text", text=json.dumps(result.model_dump(by_alias=True), indent=2)
                            )
                        ]
                    )

                elif name == "get_test_result":
                    result = await self.pscheduler_client.get_result(arguments["runUrl"])
                    if result:
                        return CallToolResult(
                            content=[
                                TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))
                            ]
                        )
                    else:
                        return CallToolResult(
                            content=[TextContent(type="text", text="Test not completed yet")]
                        )

                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")], isError=True
                )

        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            return [
                Resource(
                    uri=f"perfsonar://{self.perfsonar_host}/archive",
                    name="perfSONAR Archive",
                    description="Main perfSONAR measurement archive",
                    mimeType="application/json",
                )
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> ReadResourceResult:
            if uri == f"perfsonar://{self.perfsonar_host}/archive":
                measurements = await self.client.query_measurements()
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=json.dumps([m.model_dump(by_alias=True) for m in measurements], indent=2),
                        )
                    ]
                )
            raise ValueError(f"Unknown resource: {uri}")

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )

    async def cleanup(self):
        """Cleanup resources"""
        await self.client.close()
        await self.lookup_client.close()
        await self.pscheduler_client.close()
