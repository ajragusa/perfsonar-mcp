#!/usr/bin/env python3
"""
Main entry point for perfSONAR MCP server
"""

import asyncio
import sys
from perfsonar_mcp.server import PerfSONARMCPServer


def main():
    """Main entry point"""
    try:
        server = PerfSONARMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        sys.stderr.write("\nShutting down...\n")
        sys.exit(0)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
