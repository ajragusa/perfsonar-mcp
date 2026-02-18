#!/usr/bin/env python3
"""
Main entry point for perfSONAR MCP server
"""

import asyncio
import logging
import sys
from perfsonar_mcp.server import PerfSONARMCPServer


def main():
    """Main entry point"""
    # Configure logging to stderr for MCP compatibility
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting perfSONAR MCP server")
        server = PerfSONARMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down")
        sys.stderr.write("\nShutting down...\n")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
