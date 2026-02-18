# Contributing to perfSONAR MCP

Thank you for your interest in contributing to the perfSONAR MCP server!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/ajragusa/perfsonar-mcp.git
cd perfsonar-mcp
```

2. Install dependencies:
```bash
pip install -e '.[dev]'
```

3. Run tests:
```bash
pytest tests/
```

## Project Structure

```
perfsonar-mcp/
├── src/
│   └── perfsonar_mcp/        # Python implementation
│       ├── __init__.py       # Package initialization
│       ├── __main__.py       # Entry point
│       ├── server.py         # Main MCP server
│       ├── client.py         # Measurement archive client
│       ├── lookup.py         # Lookup service client
│       ├── pscheduler.py     # pScheduler client
│       └── types.py          # Type definitions
├── tests/
│   └── test_basic.py         # Basic tests
├── helm/                     # Kubernetes Helm chart
├── .devcontainer/            # VS Code DevContainer
├── Dockerfile                # Production Docker image
├── docker-compose.yml        # Local deployment
├── pyproject.toml           # Python package config
├── README.md                # Main documentation
├── DEPLOYMENT.md            # Deployment guide
├── EXAMPLES.md              # Usage examples
└── CONTRIBUTING.md          # This file
```

## Development Workflow

### Making Changes

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes in the `src/perfsonar_mcp/` directory

3. Format and test:
```bash
black src/perfsonar_mcp/
ruff check src/perfsonar_mcp/
mypy src/perfsonar_mcp/
pytest tests/
```

4. Commit your changes with clear messages:
```bash
git commit -m "Add feature: description"
```

### Code Style

- Use Python 3.10+ features
- Follow PEP 8 style guidelines
- Use Black for code formatting (line length: 100)
- Add docstrings for public APIs
- Use descriptive variable and function names
- Keep functions focused and single-purpose
- Use async/await for all I/O operations

### Type Safety

- All code must pass mypy strict type checking
- Use Pydantic models for data validation
- Add type hints to all function signatures
- Use Optional[] for nullable types
- Export types from `types.py`

## Testing

Currently, the project has basic tests in `tests/test_basic.py`:

1. Integration tests require a running perfSONAR instance
2. Unit tests can mock the httpx client
3. Add new test files in `tests/` directory

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=perfsonar_mcp --cov-report=html

# Run specific test
pytest tests/test_basic.py::test_imports -v
```

### Manual Testing

To test against a real perfSONAR instance:

```bash
export PERFSONAR_HOST=your-perfsonar-host.example.com
python -m perfsonar_mcp
```

Then use an MCP client (like Claude Desktop) to interact with the server.

## Adding New Tools

To add a new tool to the MCP server:

1. Add method to appropriate client (`client.py`, `lookup.py`, or `pscheduler.py`)
2. Add tool definition in `server.py` `list_tools()` method
3. Implement handler in `server.py` `call_tool()` method
4. Add Pydantic model to `types.py` if needed
5. Update the README with the new tool documentation
6. Add tests for the new functionality

Example:
```python
# 1. Add to types.py
class MyNewToolParams(BaseModel):
    param1: str = Field(description="Description of param1")
    param2: Optional[int] = Field(default=None, description="Description of param2")

# 2. Add to server.py list_tools()
Tool(
    name="my_new_tool",
    description="What this tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."},
            "param2": {"type": "number", "description": "..."}
        },
        "required": ["param1"]
    }
)

# 3. Implement handler in call_tool()
elif name == "my_new_tool":
    params = MyNewToolParams(**arguments)
    result = await self.client.my_new_method(params.param1, params.param2)
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(result))]
    )
```

## Adding New Resources

To add a new resource:

1. Add the resource to the `list_resources()` method
2. Implement the read logic in the `read_resource()` method

## perfSONAR API Coverage

The perfSONAR API has many endpoints. Currently supported:
- ✅ Query measurements (esmond archive)
- ✅ Get time-series data
- ✅ Throughput measurements
- ✅ Latency measurements
- ✅ Packet loss measurements
- ✅ Event type discovery
- ✅ Lookup service (testpoint discovery)
- ✅ pScheduler (test scheduling)

Not yet implemented (contributions welcome):
- ⬜ Traceroute data
- ⬜ Path MTU data
- ⬜ Historical data export
- ⬜ Custom time range queries
- ⬜ Multiple archive support

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update EXAMPLES.md if adding new functionality
3. Ensure all tests pass
4. Run linters and formatters
5. Request review from maintainers

## Questions or Issues?

- Open an issue on GitHub for bugs or feature requests
- Tag issues appropriately (bug, enhancement, question, etc.)
- Provide clear reproduction steps for bugs
- Include perfSONAR version and environment details

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
