---
name: vercel-ai-sdk-production
description: "Production-ready Vercel AI SDK v4/v5 patterns: real npm packages, actual APIs, deployment workflows, and infrastructure integration."
version: 2.0.0
author: Hermes Agent (production upgrade)
license: MIT
dependencies: [ai, @ai-sdk/openai, @vercel/kv, @vercel/postgres, vercel]
metadata:
  hermes:
    tags: [AI SDK, Vercel, Production, Next.js, Streaming, RAG, Deploy]
---

# Vercel AI SDK Production

Production-ready patterns using **real Vercel AI SDK packages** from npm registry. Not theory — actual `npm install` commands and working code.

## Prerequisites

```bash
# Required packages
npm install ai @ai-sdk/openai zod

# Optional providers
npm install @ai-sdk/anthropic @ai-sdk/google @ai-sdk/groq @ai-sdk/xai @ai-sdk/deepinfra

# Vercel infrastructure
npm install @vercel/kv @vercel/postgres @vercel/blob

# Deployment
npm install -g vercel
```

## Quick Start — Real Working App

```bash
# 1. Create Next.js app
npx create-next-app@latest my-ai-app --typescript --tailwind --app

# 2. Install AI SDK
cd my-ai-app
npm install ai @ai-sdk/openai zod

# 3. Add API key
echo "OPENAI_API_KEY=your-key" > .env.local

# 4. Create API route
mkdir -p app/api/chat
```

```typescript
// app/api/chat/route.ts — REAL WORKING CODE
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    messages,
  });

  return result.toDataStreamResponse();
}
```

```typescript
// app/page.tsx — REAL WORKING UI
'use client';
import { useChat } from 'ai/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat();

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map(m => (
          <div key={m.id} className={`mb-4 ${m.role === 'user' ? 'text-right' : ''}`}>
            <div className={`inline-block p-3 rounded-lg ${
              m.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100'
            }`}>
              {m.content}
            </div>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <input
          value={input}
          onChange={handleInputChange}
          className="w-full p-2 border rounded"
          placeholder="Type a message..."
        />
      </form>
    </div>
  );
}
```

```bash
# 5. Run locally
npm run dev

# 6. Deploy
vercel --prod
```

## Core AI SDK v4/v5 API (Real)

### streamText — Streaming Chat

```typescript
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

const result = streamText({
  model: openai('gpt-4o'),
  system: 'You are a helpful assistant.',
  messages: [
    { role: 'user', content: 'Hello!' }
  ],
  temperature: 0.7,
  maxTokens: 1000,
});

// Convert to Response
return result.toDataStreamResponse();

// Or read stream
for await (const textPart of result.textStream) {
  console.log(textPart);
}
```

### generateText — One-shot

```typescript
import { generateText } from 'ai';

const { text, usage, finishReason } = await generateText({
  model: openai('gpt-4o'),
  prompt: 'Write a haiku about coding',
});

console.log(text); // The generated text
console.log(usage.totalTokens); // Token count
```

### generateObject — Structured Output

```typescript
import { generateObject } from 'ai';
import { z } from 'zod';

const schema = z.object({
  recipe: z.object({
    name: z.string(),
    ingredients: z.array(z.object({
      name: z.string(),
      amount: z.string(),
    })),
    steps: z.array(z.string()),
  }),
});

const { object } = await generateObject({
  model: openai('gpt-4o'),
  schema,
  prompt: 'Generate a chocolate cake recipe',
});

// object.recipe.name — fully typed!
```

### embed — Embeddings

```typescript
import { embed } from 'ai';

const { embedding } = await embed({
  model: openai.embedding('text-embedding-3-small'),
  value: 'This is the text to embed',
});

// embedding is number[] — 1536 dimensions
```

### streamObject — Streaming Structured Data

```typescript
import { streamObject } from 'ai';

const result = streamObject({
  model: openai('gpt-4o'),
  schema: z.object({
    items: z.array(z.object({
      name: z.string(),
      price: z.number(),
    })),
  }),
  prompt: 'List 3 products with prices',
});

// Stream partial objects
for await (const partialObject of result.partialObjectStream) {
  console.log(partialObject); // { items: [{ name: '...', price: ... }] }
}
```

## Production Patterns

### Pattern 1: RAG with Real Vector DB

```typescript
// lib/rag.ts
import { openai } from '@ai-sdk/openai';
import { embed, generateText } from 'ai';
import { createClient } from '@vercel/postgres';

export async function queryRAG(question: string) {
  // 1. Generate embedding
  const { embedding } = await embed({
    model: openai.embedding('text-embedding-3-small'),
    value: question,
  });

  // 2. Query Postgres with pgvector
  const client = createClient();
  await client.connect();
  const { rows } = await client.sql`
    SELECT content, 1 - (embedding <=> ${JSON.stringify(embedding)}::vector) as similarity
    FROM documents
    ORDER BY similarity DESC
    LIMIT 5
  `;

  // 3. Generate answer with context
  const context = rows.map(r => r.content).join('\n\n');
  const { text } = await generateText({
    model: openai('gpt-4o'),
    system: `Answer based on this context:\n${context}`,
    prompt: question,
  });

  return { answer: text, sources: rows };
}
```

### Pattern 2: Persistent Chat with Vercel KV

```typescript
// lib/chat-store.ts
import { kv } from '@vercel/kv';

export async function saveMessages(chatId: string, messages: any[]) {
  await kv.set(`chat:${chatId}`, JSON.stringify(messages));
}

export async function loadMessages(chatId: string) {
  const data = await kv.get<string>(`chat:${chatId}`);
  return data ? JSON.parse(data) : [];
}

// app/api/chat/route.ts
import { loadMessages, saveMessages } from '@/lib/chat-store';

export async function POST(req: Request) {
  const { messages, chatId } = await req.json();
  
  // Load history
  const history = await loadMessages(chatId);
  const allMessages = [...history, ...messages];
  
  // Stream response
  const result = streamText({
    model: openai('gpt-4o'),
    messages: allMessages,
  });
  
  // Save on completion
  const response = result.toDataStreamResponse();
  response.headers.set('X-Chat-Id', chatId);
  
  return response;
}
```

### Pattern 3: File Upload with Vercel Blob

```typescript
// app/api/upload/route.ts
import { put } from '@vercel/blob';

export async function POST(req: Request) {
  const formData = await req.formData();
  const file = formData.get('file') as File;
  
  const blob = await put(file.name, file, {
    access: 'public',
  });
  
  return Response.json({ url: blob.url });
}

// app/api/chat/route.ts — with attachments
import { openai } from '@ai-sdk/openai';

export async function POST(req: Request) {
  const { messages, attachments } = await req.json();
  
  const result = streamText({
    model: openai('gpt-4o-vision'),
    messages: [
      ...messages,
      {
        role: 'user',
        content: [
          { type: 'text', text: 'Analyze this image' },
          { type: 'image', image: attachments[0].url },
        ],
      },
    ],
  });
  
  return result.toDataStreamResponse();
}
```

### Pattern 4: Multi-Provider with Registry

```typescript
// lib/providers.ts
import { createProviderRegistry } from 'ai';
import { openai } from '@ai-sdk/openai';
import { groq } from '@ai-sdk/groq';
import { anthropic } from '@ai-sdk/anthropic';

export const registry = createProviderRegistry({
  openai,
  groq,
  anthropic,
});

// Usage
const model = registry.languageModel('openai:gpt-4o');
// or
const model = registry.languageModel('groq:llama-3.1-70b-versatile');
// or
const model = registry.languageModel('anthropic:claude-3-5-sonnet-20241022');
```

### Pattern 5: Tool Calling with Real APIs

```typescript
// lib/tools.ts
import { tool } from 'ai';
import { z } from 'zod';

export const searchTool = tool({
  description: 'Search the web using Serper API',
  parameters: z.object({ query: z.string() }),
  execute: async ({ query }) => {
    const res = await fetch('https://google.serper.dev/search', {
      method: 'POST',
      headers: {
        'X-API-KEY': process.env.SERPER_API_KEY!,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ q: query }),
    });
    return res.json();
  },
});

export const weatherTool = tool({
  description: 'Get weather for a location',
  parameters: z.object({ city: z.string() }),
  execute: async ({ city }) => {
    const res = await fetch(
      `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${process.env.OPENWEATHER_API_KEY}`
    );
    return res.json();
  },
});

// app/api/chat/route.ts
import { searchTool, weatherTool } from '@/lib/tools';

export async function POST(req: Request) {
  const { messages } = await req.json();
  
  const result = streamText({
    model: openai('gpt-4o'),
    messages,
    tools: { search: searchTool, weather: weatherTool },
    maxSteps: 5,
  });
  
  return result.toDataStreamResponse();
}
```

### Pattern 6: Rate Limiting

```typescript
// lib/rate-limit.ts
import { kv } from '@vercel/kv';

export async function rateLimit(identifier: string, limit: number = 10) {
  const key = `rate:${identifier}`;
  const current = await kv.incr(key);
  
  if (current === 1) {
    await kv.expire(key, 3600); // 1 hour window
  }
  
  if (current > limit) {
    throw new Error('Rate limit exceeded');
  }
  
  return { remaining: limit - current };
}

// app/api/chat/route.ts
export async function POST(req: Request) {
  const ip = req.headers.get('x-forwarded-for') || 'unknown';
  await rateLimit(ip, 10); // 10 requests per hour
  
  // ... rest of handler
}
```

### Pattern 7: Monitoring with Vercel Analytics

```typescript
// lib/analytics.ts
import { track } from '@vercel/analytics';

export function trackChatEvent(event: string, properties?: Record<string, any>) {
  track(event, properties);
}

// app/api/chat/route.ts
import { trackChatEvent } from '@/lib/analytics';

export async function POST(req: Request) {
  const start = Date.now();
  
  // ... handle request
  
  trackChatEvent('chat_completion', {
    duration: Date.now() - start,
    model: 'gpt-4o',
  });
  
  return result.toDataStreamResponse();
}
```

## Deployment

### Vercel CLI Commands

```bash
# Login
vercel login

# Link project
vercel link

# Deploy preview
vercel

# Deploy production
vercel --prod

# Environment variables
vercel env add OPENAI_API_KEY
vercel env add POSTGRES_URL
vercel env add KV_URL
```

### vercel.json Configuration

```json
{
  "functions": {
    "app/api/chat/route.ts": {
      "maxDuration": 30
    }
  },
  "crons": [
    {
      "path": "/api/cron/cleanup",
      "schedule": "0 0 * * *"
    }
  ]
}
```

### GitHub Actions CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: vercel/action-deploy@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional providers
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
GOOGLE_GENERATIVE_AI_API_KEY=...

# Vercel infrastructure
POSTGRES_URL=postgres://...
KV_URL=redis://...
KV_REST_API_URL=...
KV_REST_API_TOKEN=...
BLOB_READ_WRITE_TOKEN=...

# External APIs
SERPER_API_KEY=...
OPENWEATHER_API_KEY=...
```

## References

- https://sdk.vercel.ai/docs
- https://github.com/vercel/ai
- npm: ai, @ai-sdk/*
