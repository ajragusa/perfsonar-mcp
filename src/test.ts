#!/usr/bin/env node
/**
 * Simple test script to verify the MCP server can start
 * This doesn't test actual perfSONAR integration (would need a real perfSONAR instance)
 * but verifies the server structure is correct
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { PerfSONARClient } from "./client.js";

// Test that we can import the required modules
console.log("✓ Successfully imported Server from @modelcontextprotocol/sdk");
console.log("✓ Successfully imported PerfSONARClient");

// Test that we can create a PerfSONARClient
const testHost = "test.perfsonar.net";
const client = new PerfSONARClient({ host: testHost });
console.log(`✓ Successfully created PerfSONARClient for host: ${testHost}`);

// Test that we can create a Server
const server = new Server(
  {
    name: "perfsonar-mcp-test",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);
console.log("✓ Successfully created MCP Server instance");

console.log("\n✅ All basic tests passed!");
console.log("\nNote: Full integration tests require a running perfSONAR instance.");
console.log("Set PERFSONAR_HOST environment variable and run: npm start");
