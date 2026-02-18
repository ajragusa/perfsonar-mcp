"""
Tests for FastMCP wrapper
"""

import pytest


def test_fastmcp_import():
    """Test that FastMCP server module can be imported"""
    from perfsonar_mcp import fastmcp_server
    assert fastmcp_server.mcp is not None
    assert fastmcp_server.mcp.name == "perfsonar-mcp"


def test_fastmcp_server_object():
    """Test that FastMCP server object is properly configured"""
    from perfsonar_mcp.fastmcp_server import mcp
    assert mcp is not None
    assert mcp.name == "perfsonar-mcp"
    assert mcp.instructions is not None
    assert "perfSONAR" in mcp.instructions


@pytest.mark.asyncio
async def test_fastmcp_tools_registered():
    """Test that all tools are registered"""
    from perfsonar_mcp.fastmcp_server import mcp
    
    # Get tools dictionary
    tools_dict = await mcp.get_tools()
    tool_names = list(tools_dict.keys())
    
    # Check that all expected tools are registered
    expected_tools = [
        "query_measurements",
        "get_measurement_data",
        "get_throughput",
        "get_latency",
        "get_packet_loss",
        "get_available_event_types",
        "lookup_testpoints",
        "find_pscheduler_services",
        "schedule_throughput_test",
        "schedule_latency_test",
        "schedule_rtt_test",
        "get_test_status",
        "get_test_result",
    ]
    
    for tool in expected_tools:
        assert tool in tool_names, f"Tool {tool} not found in registered tools"
    
    # Verify tools have proper metadata
    for tool_name in expected_tools:
        tool = tools_dict[tool_name]
        assert hasattr(tool, 'fn'), f"Tool {tool_name} missing function"
        assert callable(tool.fn), f"Tool {tool_name} function not callable"


@pytest.mark.asyncio
async def test_fastmcp_resources_registered():
    """Test that resources are registered"""
    from perfsonar_mcp.fastmcp_server import mcp
    
    # Get resources dictionary
    resources_dict = await mcp.get_resources()
    resource_uris = list(resources_dict.keys())
    
    # Check that archive resource is registered
    assert any("perfsonar://archive" in uri for uri in resource_uris)
    
    # Verify resource has proper metadata
    for uri, resource in resources_dict.items():
        if "perfsonar://archive" in uri:
            assert hasattr(resource, 'fn'), f"Resource {uri} missing function"
            assert callable(resource.fn), f"Resource {uri} function not callable"


def test_fastmcp_main():
    """Test that main function exists"""
    from perfsonar_mcp.fastmcp_server import main
    assert main is not None
    assert callable(main)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
