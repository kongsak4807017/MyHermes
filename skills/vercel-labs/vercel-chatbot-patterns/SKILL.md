---
name: vercel-chatbot-patterns
description: "Chatbot patterns from Vercel Labs: Gemini chatbot, ChatGPT apps, AI chatbot gateway, and conversational UI patterns."
version: 1.0.0
author: Hermes Agent (derived from vercel-labs repos)
license: MIT
dependencies: [nextjs, react, ai-sdk]
metadata:
  hermes:
    tags: [Chatbot, AI SDK, Next.js, Gemini, ChatGPT, Conversational UI]
---

# Vercel Chatbot Patterns

Patterns for building AI chatbots from vercel-labs repositories.

## When to use

**Use when building:**
- Generative UI chatbots
- ChatGPT-style applications
- Conversational AI interfaces
- Multi-model chatbots
- Chatbots with tool integration

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Chat Interface (React)                    │
│              ┌─────────────┐  ┌─────────────┐             │
│              │   Messages   │  │   Input     │             │
│              │   (Stream)   │  │  (Submit)   │             │
│              └──────┬──────┘  └──────┬──────┘             │
│                     │                │                     │
│              ┌──────▼────────────────▼──────┐             │
│              │      useChat Hook              │             │
│              │      (ai/react)                │             │
│              └─────────────┬─────────────────┘             │
└────────────────────────────┼────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    API Route (Next.js)                         │
│              ┌─────────────────────────────┐                │
│              │   streamText / streamUI      │                │
│              │   (AI SDK Core)                │                │
│              └─────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
npm install ai @ai-sdk/openai @ai-sdk/google
```

## Patterns

### Pattern 1: Gemini Chatbot

From `gemini-chatbot`:

```typescript
// app/api/chat/route.ts
import { google } from '@ai-sdk/google';
import { streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: google('gemini-1.5-pro-latest'),
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
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();

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
        {isLoading && <div className="text-gray-400">Thinking...</div>}
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <input
          value={input}
          onChange={handleInputChange}
          className="w-full p-2 border rounded"
          placeholder="Ask Gemini..."
        />
      </form>
    </div>
  );
}
```

### Pattern 2: ChatGPT Apps SDK Starter

From `chatgpt-apps-sdk-nextjs-starter`:

```typescript
// app/api/chat/route.ts
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    system: 'You are a helpful assistant.',
    messages,
  });

  return result.toDataStreamResponse();
}
```

### Pattern 3: AI Chatbot Gateway

From `ai-chatbot-gateway`:

```typescript
// app/api/chat/route.ts
import { createOpenAI } from '@ai-sdk/openai';
import { streamText } from 'ai';

const openai = createOpenAI({
  baseURL: 'https://gateway.ai.cloudflare.com/v1/...',
  headers: {
    'Authorization': `Bearer ${process.env.GATEWAY_TOKEN}`,
  },
});

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    messages,
  });

  return result.toDataStreamResponse();
}
```

### Pattern 4: Generative UI Chatbot

```typescript
// components/chat-message.tsx
import { UIMessage } from 'ai';

export function ChatMessage({ message }: { message: UIMessage }) {
  if (message.parts) {
    return (
      <div>
        {message.parts.map((part, i) => {
          if (part.type === 'text') {
            return <p key={i}>{part.text}</p>;
          }
          if (part.type === 'tool-invocation') {
            return <ToolCall key={i} tool={part.toolInvocation} />;
          }
          return null;
        })}
      </div>
    );
  }
  return <p>{message.content}</p>;
}
```

### Pattern 5: Multi-Model Chatbot

```typescript
// lib/models.ts
import { openai } from '@ai-sdk/openai';
import { google } from '@ai-sdk/google';
import { anthropic } from '@ai-sdk/anthropic';

export const models = {
  gpt4o: openai('gpt-4o'),
  gemini: google('gemini-1.5-pro-latest'),
  claude: anthropic('claude-3-5-sonnet-20241022'),
};

// app/api/chat/route.ts
export async function POST(req: Request) {
  const { messages, model } = await req.json();
  const selectedModel = models[model as keyof typeof models] || models.gpt4o;

  const result = streamText({
    model: selectedModel,
    messages,
  });

  return result.toDataStreamResponse();
}
```

## Deployment

### Vercel
```bash
vercel --prod
```

### Environment Variables
```
OPENAI_API_KEY=...
GOOGLE_GENERATIVE_AI_API_KEY=...
ANTHROPIC_API_KEY=...
```

## References

- https://github.com/vercel-labs/gemini-chatbot
- https://github.com/vercel-labs/chatgpt-apps-sdk-nextjs-starter
- https://github.com/vercel-labs/ai-chatbot-gateway
