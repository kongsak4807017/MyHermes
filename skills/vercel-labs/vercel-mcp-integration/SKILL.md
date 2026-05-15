---
name: vercel-mcp-integration
description: "MCP (Model Context Protocol) integration with Next.js/Vercel: servers, clients, transport patterns, and tool definitions."
version: 1.0.0
author: Hermes Agent (derived from vercel-labs repos)
license: MIT
dependencies: [nextjs, typescript, mcp]
metadata:
  hermes:
    tags: [MCP, Model Context Protocol, Next.js, Vercel, AI SDK, Tools]
---

# Vercel MCP Integration

Patterns for building and connecting MCP (Model Context Protocol) servers with Next.js, Vercel AI SDK, and various transports.

## When to use

**Use when:**
- Building MCP servers that expose tools to AI models
- Connecting Next.js apps to MCP servers
- Integrating external APIs via MCP (Stripe, Contentful, etc.)
- Creating stdio or HTTP MCP transports
- Building AI agents that use MCP tools

## Core Concepts

### MCP Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Host (Next.js App)                    │
│              ┌─────────────────────────────┐                │
│              │      MCP Client              │                │
│              │   (AI SDK integration)       │                │
│              └─────────────┬───────────────┘                │
└────────────────────────────┼────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼──────┐ ┌───▼────┐ ┌──────▼──────┐
       │  stdio      │ │ HTTP   │ │  Server-Sent│
       │  transport  │ │transport│ │  Events     │
       └──────┬──────┘ └───┬────┘ └──────┬──────┘
              │            │             │
       ┌──────▼──────┐ ┌───▼────┐ ┌──────▼──────┐
       │ MCP Server  │ │MCP Server│ │ MCP Server  │
       │ (local)     │ │(remote)  │ │ (edge)      │
       └─────────────┘ └────────┘ └─────────────┘
```

## Quick Start

### Installation

```bash
npm install @modelcontextprotocol/sdk ai @ai-sdk/openai
```

### Pattern 1: MCP Server with stdio Transport

From `mcp-on-vercel`:

```typescript
// server.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

const server = new Server({
  name: 'example-server',
  version: '1.0.0',
}, {
  capabilities: { tools: {} },
});

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'search',
        description: 'Search the knowledge base',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string' },
          },
          required: ['query'],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'search') {
    const { query } = request.params.arguments;
    const results = await performSearch(query);
    return { content: [{ type: 'text', text: JSON.stringify(results) }] };
  }
  throw new Error(`Unknown tool: ${request.params.name}`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Pattern 2: MCP Server with HTTP/SSE Transport

From `mcp-for-next.js`:

```typescript
// app/api/mcp/route.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';

const server = new Server({
  name: 'nextjs-mcp',
  version: '1.0.0',
}, {
  capabilities: { tools: {} },
});

// Tool definitions...

export async function GET(req: Request) {
  const transport = new SSEServerTransport('/api/mcp', res);
  await server.connect(transport);
  return new Response(transport.sessionId);
}

export async function POST(req: Request) {
  const body = await req.json();
  // Handle tool calls via HTTP
  return Response.json({ result: await handleToolCall(body) });
}
```

### Pattern 3: MCP to AI SDK Bridge

From `mcp-to-ai-sdk`:

```typescript
import { createMCPClient } from 'ai';
import { openai } from '@ai-sdk/openai';

// Create MCP client
const mcpClient = await createMCPClient({
  transport: {
    type: 'stdio',
    command: 'node',
    args: ['server.js'],
  },
});

// Get tools from MCP server
const tools = await mcpClient.tools();

// Use with AI SDK
const result = await generateText({
  model: openai('gpt-4o'),
  tools,
  prompt: 'Search for information about Next.js',
});

// Cleanup
await mcpClient.close();
```

### Pattern 4: Express MCP Server

From `express-mcp`:

```typescript
import express from 'express';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';

const app = express();
const server = new Server({ name: 'express-mcp', version: '1.0.0' });

let transport: SSEServerTransport;

app.get('/sse', async (req, res) => {
  transport = new SSEServerTransport('/messages', res);
  await server.connect(transport);
});

app.post('/messages', async (req, res) => {
  if (transport) {
    await transport.handlePostMessage(req, res);
  }
});

app.listen(3000);
```

### Pattern 5: Stripe MCP Integration

From `mcp-for-next.js-with-stripe`:

```typescript
// tools/stripe.ts
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export const stripeTools = [
  {
    name: 'create_payment_intent',
    description: 'Create a Stripe PaymentIntent',
    parameters: {
      amount: { type: 'number' },
      currency: { type: 'string' },
    },
    execute: async ({ amount, currency }) => {
      const intent = await stripe.paymentIntents.create({ amount, currency });
      return { client_secret: intent.client_secret };
    },
  },
  {
    name: 'list_products',
    description: 'List Stripe products',
    execute: async () => {
      const products = await stripe.products.list();
      return { products: products.data };
    },
  },
];
```

### Pattern 6: Contentful MCP Server

From `contentful-mcp-server`:

```typescript
import { createClient } from 'contentful-management';

const client = createClient({
  accessToken: process.env.CONTENTFUL_MANAGEMENT_TOKEN!,
});

export const contentfulTools = [
  {
    name: 'get_entries',
    description: 'Get Contentful entries',
    parameters: { content_type: { type: 'string' }, limit: { type: 'number' } },
    execute: async ({ content_type, limit }) => {
      const space = await client.getSpace(process.env.CONTENTFUL_SPACE_ID!);
      const env = await space.getEnvironment('master');
      const entries = await env.getEntries({ content_type, limit });
      return { entries: entries.items.map(e => e.fields) };
    },
  },
  {
    name: 'create_entry',
    description: 'Create a Contentful entry',
    parameters: {
      content_type: { type: 'string' },
      fields: { type: 'object' },
    },
    execute: async ({ content_type, fields }) => {
      const space = await client.getSpace(process.env.CONTENTFUL_SPACE_ID!);
      const env = await space.getEnvironment('master');
      const entry = await env.createEntry(content_type, { fields });
      return { entryId: entry.sys.id };
    },
  },
];
```

### Pattern 7: AI SDK 5 Migration MCP Server

From `ai-sdk-5-migration-mcp-server`:

```typescript
// MCP server that helps migrate AI SDK 4.x to 5.0
import { Server } from '@modelcontextprotocol/sdk/server/index.js';

const migrationTools = [
  {
    name: 'analyze_codebase',
    description: 'Analyze codebase for AI SDK 4.x patterns',
    parameters: { path: { type: 'string' } },
    execute: async ({ path }) => {
      // Scan for deprecated imports
      // Report: openai.chat.completions.create -> streamText
      // Report: streamData -> toDataStreamResponse
      return { report: generateMigrationReport(path) };
    },
  },
  {
    name: 'apply_migration',
    description: 'Apply AI SDK 5.0 migration fixes',
    parameters: { file: { type: 'string' } },
    execute: async ({ file }) => {
      // Auto-apply transformations
      return { modified: true, changes: [...] };
    },
  },
];
```

### Pattern 8: Next.js + MCP + AI SDK Full Integration

```typescript
// app/api/chat/route.ts
import { createMCPClient } from 'ai';
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  // Connect to MCP server
  const mcpClient = await createMCPClient({
    transport: {
      type: 'stdio',
      command: 'node',
      args: ['mcp-server.js'],
    },
  });

  // Get dynamic tools
  const tools = await mcpClient.tools();

  // Stream with MCP tools
  const result = streamText({
    model: openai('gpt-4o'),
    messages,
    tools,
    maxSteps: 5,
  });

  // Cleanup on completion
  result.toDataStreamResponse({
    onFinish: () => mcpClient.close(),
  });
}
```

## Transport Patterns

### stdio Transport
- Best for: Local MCP servers, CLI tools
- Pros: Simple, no network overhead
- Cons: Single process, no concurrency

### HTTP/SSE Transport
- Best for: Remote MCP servers, web apps
- Pros: HTTP-compatible, scalable
- Cons: More complex setup

### WebSocket Transport
- Best for: Real-time bidirectional
- Pros: Full-duplex
- Cons: Not in MCP spec yet

## Tool Definition Schema

```typescript
interface MCPTool {
  name: string;
  description: string;
  parameters: {
    type: 'object';
    properties: Record<string, {
      type: 'string' | 'number' | 'boolean' | 'array' | 'object';
      description?: string;
      enum?: string[];
    }>;
    required?: string[];
  };
  execute: (args: any) => Promise<any>;
}
```

## Deployment

### Vercel Edge MCP
```typescript
// vercel.json
{
  "functions": {
    "api/mcp/*": {
      "maxDuration": 30
    }
  }
}
```

### Environment Variables
```
MCP_SERVER_COMMAND=node
MCP_SERVER_ARGS=server.js
STRIPE_SECRET_KEY=sk_...
CONTENTFUL_MANAGEMENT_TOKEN=...
```

## References

- https://modelcontextprotocol.io
- https://github.com/vercel-labs/mcp-* repos
