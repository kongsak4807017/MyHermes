---
name: vercel-ai-sdk-patterns
description: "Vercel AI SDK patterns: streaming, RAG, generative UI, multi-step agents, tool calling, and provider integration."
version: 1.0.0
author: Hermes Agent (derived from vercel-labs repos)
license: MIT
dependencies: [nextjs, react, typescript]
metadata:
  hermes:
    tags: [AI SDK, Vercel, Streaming, RAG, Generative UI, Next.js, React]
---

# Vercel AI SDK Patterns

Comprehensive patterns extracted from vercel-labs repositories for building AI-powered applications with the Vercel AI SDK.

## When to use

**Use when building:**
- Streaming AI chatbots with React/Next.js
- RAG (Retrieval-Augmented Generation) applications
- Generative UI with React Server Components
- Multi-step AI agents with tool calling
- AI applications with persistent memory
- Provider-agnostic AI integrations (OpenAI, Groq, xAI, DeepInfra, etc.)

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (React)                    │
│              ┌─────────────┐  ┌─────────────┐             │
│              │  Chat Input   │  │  Message UI │             │
│              └──────┬──────┘  └─────────────┘             │
└─────────────────────┬─────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│              API Route (Next.js App Router)                  │
│              ┌─────────────────────────────┐                │
│              │   streamText / streamUI     │                │
│              │   generateText / generateObject            │
│              └─────────────────────────────┘                │
└─────────────────────┬─────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│              AI SDK Core (Provider Agnostic)                 │
│         ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│         │  OpenAI  │ │   Groq   │ │   xAI    │           │
│         │  Gemini  │ │ DeepInfra│ │Anthropic │           │
│         └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
npm install ai @ai-sdk/openai zod
# or for other providers
npm install @ai-sdk/groq @ai-sdk/anthropic @ai-sdk/google
```

### Basic Streaming Chat

```typescript
// app/api/chat/route.ts
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
// app/page.tsx
'use client';
import { useChat } from 'ai/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat();

  return (
    <div>
      {messages.map(m => (
        <div key={m.id}>
          <strong>{m.role}:</strong> {m.content}
        </div>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

## Patterns

### Pattern 1: RAG with Vector Search

From `ai-sdk-preview-rag`, `semantic-image-search`:

```typescript
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { createClient } from '@vercel/postgres';

export async function POST(req: Request) {
  const { messages } = await req.json();
  const lastMessage = messages[messages.length - 1];

  // 1. Generate embedding for query
  const embedding = await generateEmbedding(lastMessage.content);

  // 2. Search vector database
  const client = createClient();
  await client.connect();
  const { rows } = await client.sql`
    SELECT content, 1 - (embedding <=> ${embedding}::vector) as similarity
    FROM documents
    ORDER BY similarity DESC
    LIMIT 5
  `;

  // 3. Augment prompt with retrieved context
  const context = rows.map(r => r.content).join('\n');
  const augmentedMessages = [
    { role: 'system', content: `Context: ${context}` },
    ...messages
  ];

  // 4. Stream response
  const result = streamText({
    model: openai('gpt-4o'),
    messages: augmentedMessages,
  });

  return result.toDataStreamResponse();
}
```

### Pattern 2: Generative UI with React Server Components

From `ai-sdk-preview-rsc-genui`:

```typescript
// app/action.ts
'use server';
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { createStreamableUI } from 'ai/rsc';

export async function generateUI(prompt: string) {
  const stream = createStreamableUI();

  (async () => {
    const { text } = await generateText({
      model: openai('gpt-4o'),
      prompt: `Generate a React component for: ${prompt}`,
    });
    stream.update(<pre>{text}</pre>);
    stream.done();
  })();

  return stream.value;
}
```

### Pattern 3: Multi-Step Agents with Tool Calling

From `ai-sdk-preview-multi-steps`, `ai-sdk-computer-use`:

```typescript
import { openai } from '@ai-sdk/openai';
import { generateText, tool } from 'ai';
import { z } from 'zod';

const result = await generateText({
  model: openai('gpt-4o'),
  tools: {
    search: tool({
      description: 'Search the web',
      parameters: z.object({ query: z.string() }),
      execute: async ({ query }) => {
        // Implementation
        return { results: [...] };
      },
    }),
    calculate: tool({
      description: 'Calculate expression',
      parameters: z.object({ expression: z.string() }),
      execute: async ({ expression }) => {
        return { result: eval(expression) };
      },
    }),
  },
  maxSteps: 5, // Allow up to 5 tool call rounds
  prompt: 'Find the current weather in Tokyo and calculate 25 * 4',
});
```

### Pattern 4: Structured Output (Object Generation)

From `ai-sdk-preview-use-object`:

```typescript
import { openai } from '@ai-sdk/openai';
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
```

### Pattern 5: Persistent Chat with Database

From `ai-sdk-persistence-db`:

```typescript
import { createClient } from '@vercel/postgres';
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

export async function saveMessage(chatId: string, message: any) {
  const client = createClient();
  await client.connect();
  await client.sql`
    INSERT INTO messages (chat_id, role, content, created_at)
    VALUES (${chatId}, ${message.role}, ${message.content}, NOW())
  `;
}

export async function loadMessages(chatId: string) {
  const client = createClient();
  await client.connect();
  const { rows } = await client.sql`
    SELECT role, content FROM messages
    WHERE chat_id = ${chatId}
    ORDER BY created_at ASC
  `;
  return rows;
}
```

### Pattern 6: Provider Registry (Multi-Provider)

From `ai-sdk-preview-provider-registry`:

```typescript
import { createProviderRegistry } from 'ai';
import { openai } from '@ai-sdk/openai';
import { groq } from '@ai-sdk/groq';
import { anthropic } from '@ai-sdk/anthropic';

const registry = createProviderRegistry({
  openai,
  groq,
  anthropic,
});

// Use dynamically
const model = registry.languageModel('openai:gpt-4o');
// or
const model = registry.languageModel('groq:llama-3.1-70b');
```

### Pattern 7: PDF Support

From `ai-sdk-preview-pdf-support`:

```typescript
import { openai } from '@ai-sdk/openai';
import { generateText } from 'ai';

export async function analyzePDF(file: File) {
  const bytes = await file.arrayBuffer();
  const base64 = Buffer.from(bytes).toString('base64');

  const result = await generateText({
    model: openai('gpt-4o-vision'),
    messages: [
      {
        role: 'user',
        content: [
          { type: 'text', text: 'Analyze this PDF' },
          { type: 'image', image: base64 },
        ],
      },
    ],
  });

  return result.text;
}
```

### Pattern 8: Attachment/File Upload

From `ai-sdk-preview-attachments`:

```typescript
import { useChat } from 'ai/react';

export default function ChatWithAttachments() {
  const { messages, input, handleSubmit, handleInputChange, attachments, handleSubmit } = useChat();

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" multiple onChange={handleFileChange} />
      <input value={input} onChange={handleInputChange} />
      <button type="submit">Send</button>
    </form>
  );
}
```

### Pattern 9: Roundtrips (Tool Results)

From `ai-sdk-preview-roundtrips`:

```typescript
import { streamText } from 'ai';

const result = streamText({
  model: openai('gpt-4o'),
  messages,
  tools: { /* ... */ },
  experimental_continueSteps: true, // Enable roundtrips
});
```

### Pattern 10: Array Output Mode

From `ai-sdk-preview-array-output-mode`:

```typescript
import { generateObject } from 'ai';
import { z } from 'zod';

const { object } = await generateObject({
  model: openai('gpt-4o'),
  output: 'array',
  schema: z.object({
    name: z.string(),
    description: z.string(),
  }),
  prompt: 'Generate 3 product ideas',
});
// Returns array of objects
```

### Pattern 11: No Schema (Flexible Output)

From `ai-sdk-preview-no-schema`:

```typescript
import { generateObject } from 'ai';

const { object } = await generateObject({
  model: openai('gpt-4o'),
  prompt: 'Generate any structured data about planets',
  // No schema - model decides structure
});
```

### Pattern 12: Internal Knowledge Base

From `ai-sdk-preview-internal-knowledge-base`:

```typescript
// Load documents from internal source
const documents = await loadInternalDocs();

// Create embeddings and store
for (const doc of documents) {
  const embedding = await embed({ model: openai.embedding('text-embedding-3-small'), value: doc.content });
  await storeDocument(doc.id, doc.content, embedding);
}

// Query
const result = await streamText({
  model: openai('gpt-4o'),
  system: `You have access to: ${documents.map(d => d.title).join(', ')}`,
  messages,
});
```

### Pattern 13: Reasoning Mode

From `ai-sdk-reasoning-starter`:

```typescript
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('o1-preview'), // Reasoning model
    messages,
  });

  return result.toDataStreamResponse({
    sendReasoning: true, // Stream reasoning tokens
  });
}
```

### Pattern 14: Image Generation

From `ai-sdk-image-generator`:

```typescript
import { generateImage } from 'ai';
import { openai } from '@ai-sdk/openai';

const { image } = await generateImage({
  model: openai.image('dall-e-3'),
  prompt: 'A serene mountain landscape at sunset',
});

// image.base64 contains the generated image
```

### Pattern 15: Computer Use Agent

From `ai-sdk-computer-use`:

```typescript
import { generateText, tool } from 'ai';
import { z } from 'zod';

const computerTool = tool({
  description: 'Control computer (screenshot, click, type)',
  parameters: z.object({
    action: z.enum(['screenshot', 'click', 'type', 'scroll']),
    coordinates: z.object({ x: z.number(), y: z.number() }).optional(),
    text: z.string().optional(),
  }),
  execute: async ({ action, coordinates, text }) => {
    // Puppeteer/Playwright implementation
    if (action === 'screenshot') return await page.screenshot();
    if (action === 'click') await page.mouse.click(coordinates!.x, coordinates!.y);
    // ...
  },
});
```

### Pattern 16: Gateway Integration

From `ai-sdk-gateway-demo`:

```typescript
import { createOpenAI } from '@ai-sdk/openai';

const openai = createOpenAI({
  baseURL: 'https://api.vercel.ai/gateway', // Vercel AI Gateway
  headers: {
    'x-vercel-ai-gateway': 'your-gateway-id',
  },
});
```

### Pattern 17: Edge Config with Feature Flags

From `ai-sdk-flags-edge-config`:

```typescript
import { get } from '@vercel/edge-config';

export async function POST(req: Request) {
  const modelFlag = await get('model-version'); // 'gpt-4o' | 'gpt-4o-mini'

  const result = streamText({
    model: openai(modelFlag as string),
    messages,
  });

  return result.toDataStreamResponse();
}
```

### Pattern 18: Chrome Extension

From `ai-sdk-chrome-extension`:

```typescript
// Background script
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

chrome.runtime.onMessage.addListener(async (request, sender, sendResponse) => {
  if (request.type === 'SUMMARIZE') {
    const { text } = await generateText({
      model: openai('gpt-4o-mini'),
      prompt: `Summarize: ${request.text}`,
    });
    sendResponse({ summary: text });
  }
});
```

### Pattern 19: Natural Language to SQL

From `natural-language-postgres`:

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

export async function nlToSQL(naturalQuery: string, schema: string) {
  const { text } = await generateText({
    model: openai('gpt-4o'),
    system: `Convert natural language to SQL. Schema: ${schema}`,
    prompt: naturalQuery,
  });
  return text;
}
```

### Pattern 20: Slack Bot

From `ai-sdk-slackbot`:

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

export async function handleSlackEvent(event: any) {
  if (event.type === 'app_mention') {
    const { text } = await generateText({
      model: openai('gpt-4o'),
      prompt: event.text,
    });
    await postToSlack(event.channel, text);
  }
}
```

## Provider Starters

### Groq
```typescript
import { groq } from '@ai-sdk/groq';
const model = groq('llama-3.1-70b-versatile');
```

### xAI
```typescript
import { xai } from '@ai-sdk/xai';
const model = xai('grok-2');
```

### DeepInfra
```typescript
import { deepinfra } from '@ai-sdk/deepinfra';
const model = deepinfra('meta-llama/Llama-3.3-70B-Instruct');
```

### Braintrust
```typescript
import { braintrust } from '@ai-sdk/braintrust';
const model = braintrust('openai/gpt-4o');
```

## Deployment

### Vercel Deployment
```bash
vercel --prod
```

### Environment Variables
```
OPENAI_API_KEY=...
POSTGRES_URL=...
EDGE_CONFIG=...
```

## References

- https://sdk.vercel.ai/docs
- https://github.com/vercel-labs (all ai-sdk-* repos)
