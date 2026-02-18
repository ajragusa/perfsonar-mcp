"""
Basic tests for perfSONAR MCP server
"""

import pytest
from perfsonar_mcp.types import (
    PerfSONARConfig,
    MeasurementQueryParams,
    LookupQueryParams,
    ThroughputTestSpec,
)
from perfsonar_mcp.client import PerfSONARClient
from perfsonar_mcp.lookup import LookupServiceClient
from perfsonar_mcp.pscheduler import PSchedulerClient


def test_imports():
    """Test that all modules can be imported"""
    from perfsonar_mcp import (
        PerfSONARMCPServer,
        PerfSONARClient,
        LookupServiceClient,
        PSchedulerClient,
    )
    assert PerfSONARMCPServer is not None
    assert PerfSONARClient is not None
    assert LookupServiceClient is not None
    assert PSchedulerClient is not None


def test_types():
    """Test that type models work correctly"""
    config = PerfSONARConfig(host="test.perfsonar.net")
    assert config.host == "test.perfsonar.net"
    assert config.base_url is None
    
    params = MeasurementQueryParams(source="host1", destination="host2")
    assert params.source == "host1"
    assert params.destination == "host2"
    
    lookup_params = LookupQueryParams(type="service", location_city="Chicago")
    assert lookup_params.type == "service"
    assert lookup_params.location_city == "Chicago"
    
    test_spec = ThroughputTestSpec(dest="host.example.com", duration="PT30S")
    assert test_spec.dest == "host.example.com"
    assert test_spec.duration == "PT30S"


def test_client_creation():
    """Test that clients can be created"""
    config = PerfSONARConfig(host="test.perfsonar.net")
    client = PerfSONARClient(config)
    assert client.base_url == "http://test.perfsonar.net/esmond/perfsonar/archive"
    
    lookup_client = LookupServiceClient()
    assert lookup_client.base_url == "https://lookup.perfsonar.net/lookup"
    
    pscheduler_client = PSchedulerClient("https://test.perfsonar.net/pscheduler")
    assert pscheduler_client.base_url == "https://test.perfsonar.net/pscheduler"


@pytest.mark.asyncio
async def test_client_cleanup():
    """Test that clients can be cleaned up"""
    config = PerfSONARConfig(host="test.perfsonar.net")
    client = PerfSONARClient(config)
    await client.close()
    
    lookup_client = LookupServiceClient()
    await lookup_client.close()
    
    pscheduler_client = PSchedulerClient("https://test.perfsonar.net/pscheduler")
    await pscheduler_client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
