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
npm install
```

3. Build the project:
```bash
npm run build
```

4. Run tests:
```bash
npm test
```

## Project Structure

```
perfsonar-mcp/
├── src/
│   ├── index.ts      # Main MCP server implementation
│   ├── client.ts     # perfSONAR API client
│   ├── types.ts      # TypeScript type definitions
│   └── test.ts       # Basic tests
├── build/            # Compiled JavaScript output
├── README.md         # Main documentation
├── EXAMPLES.md       # Usage examples
└── package.json      # Project metadata and dependencies
```

## Development Workflow

### Making Changes

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes in the `src/` directory

3. Build and test:
```bash
npm run build
npm test
```

4. Commit your changes with clear messages:
```bash
git commit -m "Add feature: description"
```

### Code Style

- Use TypeScript for all code
- Follow existing code formatting patterns
- Add JSDoc comments for public APIs
- Use descriptive variable and function names
- Keep functions focused and single-purpose

### Type Safety

- All code must pass TypeScript strict mode checks
- Avoid using `any` type
- Use Zod schemas for runtime validation
- Export types from `types.ts`

## Testing

Currently, the project has basic import tests. To add more comprehensive tests:

1. Integration tests require a running perfSONAR instance
2. Unit tests can mock the axios client
3. Add test files in `src/` with `.test.ts` extension

### Manual Testing

To test against a real perfSONAR instance:

```bash
export PERFSONAR_HOST=your-perfsonar-host.example.com
npm start
```

Then use an MCP client (like Claude Desktop) to interact with the server.

## Adding New Tools

To add a new tool to the MCP server:

1. Define the Zod schema for input parameters in `src/index.ts`
2. Add the tool definition to the `ListToolsRequestSchema` handler
3. Implement the tool logic in the `CallToolRequestSchema` handler
4. If needed, add supporting methods to `PerfSONARClient` in `src/client.ts`
5. Update the README with the new tool documentation

Example:
```typescript
// 1. Define schema
const MyNewToolArgsSchema = z.object({
  param1: z.string().describe("Description of param1"),
  param2: z.number().optional().describe("Description of param2"),
});

// 2. Add to tool list
{
  name: "my_new_tool",
  description: "What this tool does",
  inputSchema: {
    type: "object",
    properties: {
      param1: { type: "string", description: "..." },
      param2: { type: "number", description: "..." }
    },
    required: ["param1"]
  }
}

// 3. Implement handler
case "my_new_tool": {
  const parsed = MyNewToolArgsSchema.parse(args);
  // Implementation here
  return { content: [{ type: "text", text: result }] };
}
```

## Adding New Resources

To add a new resource:

1. Add the resource to the `ListResourcesRequestSchema` handler
2. Implement the read logic in the `ReadResourceRequestSchema` handler

## perfSONAR API Coverage

The perfSONAR esmond API has many endpoints. Currently supported:
- ✅ Query measurements
- ✅ Get time-series data
- ✅ Throughput measurements
- ✅ Latency measurements
- ✅ Packet loss measurements
- ✅ Event type discovery

Not yet implemented (contributions welcome):
- ⬜ Traceroute data
- ⬜ Path MTU data
- ⬜ Scheduling new tests
- ⬜ Historical data with custom time ranges
- ⬜ Multiple archive support

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update EXAMPLES.md if adding new functionality
3. The PR should pass all tests
4. Request review from maintainers

## Questions or Issues?

- Open an issue on GitHub for bugs or feature requests
- Tag issues appropriately (bug, enhancement, question, etc.)
- Provide clear reproduction steps for bugs
- Include perfSONAR version and environment details

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
