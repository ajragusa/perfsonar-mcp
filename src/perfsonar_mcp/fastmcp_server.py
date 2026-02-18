"""
FastMCP wrapper for perfSONAR MCP Server
Enables web access via SSE and HTTP transports
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from perfsonar_mcp.client import PerfSONARClient
from perfsonar_mcp.lookup import LookupServiceClient
from perfsonar_mcp.pscheduler import PSchedulerClient
from perfsonar_mcp.types import (
    PerfSONARConfig,
    MeasurementQueryParams,
    MeasurementDataParams,
)

logger = logging.getLogger(__name__)

# Initialize clients - will be set during lifespan
perfsonar_client: Optional[PerfSONARClient] = None
lookup_client: Optional[LookupServiceClient] = None
pscheduler_client: Optional[PSchedulerClient] = None


@asynccontextmanager
async def lifespan(app):
    """Initialize and cleanup resources"""
    global perfsonar_client, lookup_client, pscheduler_client
    
    perfsonar_host = os.getenv("PERFSONAR_HOST")
    if not perfsonar_host:
        raise ValueError("PERFSONAR_HOST environment variable is required")
    
    lookup_service_url = os.getenv(
        "LOOKUP_SERVICE_URL", "https://lookup.perfsonar.net/lookup"
    )
    pscheduler_url = os.getenv(
        "PSCHEDULER_URL", f"https://{perfsonar_host}/pscheduler"
    )
    
    logger.info(f"Initializing perfSONAR MCP Server")
    logger.info(f"perfSONAR host: {perfsonar_host}")
    logger.info(f"Lookup service: {lookup_service_url}")
    logger.info(f"pScheduler URL: {pscheduler_url}")
    
    # Initialize clients
    perfsonar_client = PerfSONARClient(PerfSONARConfig(host=perfsonar_host))
    lookup_client = LookupServiceClient(lookup_service_url)
    pscheduler_client = PSchedulerClient(pscheduler_url)
    
    yield
    
    # Cleanup
    logger.info("Cleaning up resources")
    if perfsonar_client:
        await perfsonar_client.close()
    if lookup_client:
        await lookup_client.close()
    if pscheduler_client:
        await pscheduler_client.close()


# Initialize FastMCP server with lifespan
mcp = FastMCP(
    name="perfsonar-mcp",
    instructions="""MCP Server for perfSONAR - Query network measurements, discover testpoints, and schedule tests.
    
Available capabilities:
- Query historical measurements with filters
- Get throughput, latency, and packet loss data
- Discover perfSONAR testpoints globally
- Schedule and monitor network tests via pScheduler
""",
    lifespan=lifespan,
)


# Measurement Archive Tools

@mcp.tool()
async def query_measurements(
    source: Optional[str] = None,
    destination: Optional[str] = None,
    eventType: Optional[str] = None,
    toolName: Optional[str] = None,
    timeRange: Optional[int] = None,
) -> str:
    """Query perfSONAR measurements with optional filters. Returns metadata about available measurements.
    
    Args:
        source: Source host/IP address
        destination: Destination host/IP address
        eventType: Event type to filter (e.g., 'throughput', 'histogram-owdelay')
        toolName: Tool name to filter (e.g., 'bwctl/iperf3', 'powstream')
        timeRange: Time range in seconds from now
        
    Returns:
        JSON string with measurement metadata
    """
    params = MeasurementQueryParams(
        source=source,
        destination=destination,
        event_type=eventType,
        tool_name=toolName,
        time_range=timeRange,
    )
    results = await perfsonar_client.query_measurements(params)
    return json.dumps([r.model_dump(by_alias=True) for r in results], indent=2)


@mcp.tool()
async def get_measurement_data(
    metadataKey: str,
    eventType: str,
    summaryType: Optional[str] = None,
    summaryWindow: Optional[int] = None,
    timeRange: Optional[int] = None,
) -> str:
    """Get raw time-series data for a specific measurement.
    
    Args:
        metadataKey: Metadata key from query results
        eventType: Event type (e.g., 'throughput', 'histogram-owdelay')
        summaryType: Summary type (e.g., 'average', 'aggregation')
        summaryWindow: Summary window in seconds
        timeRange: Time range in seconds from now
        
    Returns:
        JSON string with time-series measurement data
    """
    params = MeasurementDataParams(
        metadata_key=metadataKey,
        event_type=eventType,
        summary_type=summaryType,
        summary_window=summaryWindow,
        time_range=timeRange,
    )
    results = await perfsonar_client.get_measurement_data(params)
    return json.dumps([r.model_dump() for r in results], indent=2)


@mcp.tool()
async def get_throughput(
    source: str,
    destination: str,
    timeRange: int = 86400,
    summaryWindow: Optional[int] = None,
) -> str:
    """Get throughput measurements between source and destination.
    
    Args:
        source: Source host/IP address
        destination: Destination host/IP address
        timeRange: Time range in seconds (default: 86400 = 24 hours)
        summaryWindow: Summary window in seconds for aggregation
        
    Returns:
        JSON string with throughput measurement data
    """
    results = await perfsonar_client.get_throughput(
        source, destination, timeRange, summaryWindow
    )
    return json.dumps([r.model_dump(by_alias=True) for r in results], indent=2)


@mcp.tool()
async def get_latency(
    source: str,
    destination: str,
    timeRange: int = 86400,
    summaryWindow: Optional[int] = None,
) -> str:
    """Get latency/delay measurements between source and destination.
    
    Args:
        source: Source host/IP address
        destination: Destination host/IP address
        timeRange: Time range in seconds (default: 86400 = 24 hours)
        summaryWindow: Summary window in seconds for aggregation
        
    Returns:
        JSON string with latency measurement data
    """
    results = await perfsonar_client.get_latency(
        source, destination, timeRange, summaryWindow
    )
    return json.dumps([r.model_dump(by_alias=True) for r in results], indent=2)


@mcp.tool()
async def get_packet_loss(
    source: str,
    destination: str,
    timeRange: int = 86400,
    summaryWindow: Optional[int] = None,
) -> str:
    """Get packet loss measurements between source and destination.
    
    Args:
        source: Source host/IP address
        destination: Destination host/IP address
        timeRange: Time range in seconds (default: 86400 = 24 hours)
        summaryWindow: Summary window in seconds for aggregation
        
    Returns:
        JSON string with packet loss measurement data
    """
    results = await perfsonar_client.get_packet_loss(
        source, destination, timeRange, summaryWindow
    )
    return json.dumps([r.model_dump(by_alias=True) for r in results], indent=2)


@mcp.tool()
async def get_available_event_types(
    source: Optional[str] = None,
    destination: Optional[str] = None,
) -> str:
    """Get all available event types in the measurement archive.
    
    Args:
        source: Optional source filter
        destination: Optional destination filter
        
    Returns:
        JSON string with list of available event types
    """
    results = await perfsonar_client.get_available_event_types(source, destination)
    return json.dumps(results, indent=2)


# Lookup Service Tools

@mcp.tool()
async def lookup_testpoints(
    serviceType: Optional[str] = None,
    locationCity: Optional[str] = None,
    locationCountry: Optional[str] = None,
) -> str:
    """Find perfSONAR testpoints using the lookup service.
    
    Args:
        serviceType: Service type filter (e.g., 'bwctl', 'owamp')
        locationCity: City filter (e.g., 'Chicago', 'London')
        locationCountry: Country filter (e.g., 'US', 'GB')
        
    Returns:
        JSON string with list of matching testpoints
    """
    results = await lookup_client.find_testpoints(
        serviceType, locationCity, locationCountry
    )
    return json.dumps([r.model_dump(by_alias=True) for r in results], indent=2)


@mcp.tool()
async def find_pscheduler_services(
    locationCity: Optional[str] = None,
    locationCountry: Optional[str] = None,
) -> str:
    """Find pScheduler services for running tests.
    
    Args:
        locationCity: City filter (e.g., 'Chicago', 'London')
        locationCountry: Country filter (e.g., 'US', 'GB')
        
    Returns:
        JSON string with list of pScheduler services
    """
    results = await lookup_client.find_pscheduler_services(
        locationCity, locationCountry
    )
    return json.dumps([r.model_dump(by_alias=True) for r in results], indent=2)


# pScheduler Tools

@mcp.tool()
async def schedule_throughput_test(
    dest: str,
    source: Optional[str] = None,
    duration: str = "PT30S",
) -> str:
    """Schedule a throughput test using pScheduler.
    
    Args:
        dest: Destination host for the test
        source: Optional source host (if not specified, uses pScheduler host)
        duration: Test duration in ISO 8601 format (e.g., 'PT30S' for 30 seconds)
        
    Returns:
        JSON string with test details including run URL for status checks
    """
    result = await pscheduler_client.schedule_throughput_test(
        source, dest, duration
    )
    return json.dumps(result.model_dump(), indent=2)


@mcp.tool()
async def schedule_latency_test(
    dest: str,
    source: Optional[str] = None,
    packetCount: int = 600,
    packetInterval: float = 0.1,
) -> str:
    """Schedule a latency test using pScheduler.
    
    Args:
        dest: Destination host for the test
        source: Optional source host (if not specified, uses pScheduler host)
        packetCount: Number of packets to send (default: 600)
        packetInterval: Interval between packets in seconds (default: 0.1)
        
    Returns:
        JSON string with test details including run URL for status checks
    """
    result = await pscheduler_client.schedule_latency_test(
        source, dest, packetCount, packetInterval
    )
    return json.dumps(result.model_dump(), indent=2)


@mcp.tool()
async def schedule_rtt_test(
    dest: str,
    count: int = 10,
) -> str:
    """Schedule an RTT (ping) test using pScheduler.
    
    Args:
        dest: Destination host for the test
        count: Number of pings (default: 10)
        
    Returns:
        JSON string with test details including run URL for status checks
    """
    result = await pscheduler_client.schedule_rtt_test(dest, count)
    return json.dumps(result.model_dump(), indent=2)


@mcp.tool()
async def get_test_status(runUrl: str) -> str:
    """Get status of a pScheduler test run.
    
    Args:
        runUrl: Run URL from test scheduling response
        
    Returns:
        JSON string with test status information
    """
    result = await pscheduler_client.get_run_status(runUrl)
    return json.dumps(result.model_dump(by_alias=True), indent=2)


@mcp.tool()
async def get_test_result(runUrl: str) -> str:
    """Get result of a completed pScheduler test.
    
    Args:
        runUrl: Run URL from test scheduling response
        
    Returns:
        JSON string with test results, or message if test not completed yet
    """
    result = await pscheduler_client.get_result(runUrl)
    if result:
        return json.dumps(result.model_dump(), indent=2)
    else:
        return json.dumps({"message": "Test not completed yet"})


# Resources

@mcp.resource("perfsonar://archive")
async def get_archive() -> str:
    """Get overview of the perfSONAR measurement archive"""
    measurements = await perfsonar_client.query_measurements()
    return json.dumps([m.model_dump(by_alias=True) for m in measurements], indent=2)


def main():
    """Main entry point for web server"""
    mcp.run()


if __name__ == "__main__":
    main()
