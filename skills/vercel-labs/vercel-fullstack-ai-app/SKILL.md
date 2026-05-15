---
name: vercel-fullstack-ai-app
description: "End-to-end workflow: plan, build, and deploy fullstack AI apps with Vercel AI SDK, KV, Postgres, Blob, and v0.dev patterns."
version: 1.0.0
author: Hermes Agent
license: MIT
dependencies: [nextjs, react, typescript, ai, vercel]
metadata:
  hermes:
    tags: [Fullstack, AI, Vercel, Next.js, Complete Workflow, Deploy]
---

# Vercel Fullstack AI App — Complete Workflow

End-to-end workflow for building and deploying production AI applications on Vercel.

## Workflow Overview

```
1. PLAN → 2. SETUP → 3. BUILD → 4. INTEGRATE → 5. DEPLOY → 6. MONITOR
```

## Phase 1: Plan

### Define Requirements

```typescript
// project-spec.ts — ใช้เป็น checklist
interface ProjectSpec {
  name: string;
  type: 'chatbot' | 'rag' | 'agent' | 'generative-ui' | 'workflow';
  features: string[];
  aiModels: string[];
  infrastructure: ('kv' | 'postgres' | 'blob' | 'edge-config')[];
  auth: boolean;
  externalApis: string[];
}

// ตัวอย่าง: RAG Chatbot
const spec: ProjectSpec = {
  name: 'my-rag-chatbot',
  type: 'rag',
  features: ['streaming', 'file-upload', 'persistent-chat', 'rate-limit'],
  aiModels: ['gpt-4o', 'text-embedding-3-small'],
  infrastructure: ['kv', 'postgres'],
  auth: true,
  externalApis: [],
};
```

### Architecture Decision

| ถ้าอยากได้... | ใช้ pattern... |
|--------------|--------------|
| Chatbot ธรรมดา | `vercel-ai-sdk-production` → streamText |
| Chatbot + จำประวัติ | `vercel-ai-sdk-production` + KV |
| Chatbot + อ่านเอกสาร | `vercel-ai-sdk-production` → RAG pattern |
| Chatbot + อัพโหลดรูป | `vercel-ai-sdk-production` + Blob |
| AI สร้าง UI | `vercel-v0-prompt-to-ui` |
| AI Agent ทำงานซับซ้อน | `vercel-ai-agents` |
| เชื่อม external API | `vercel-mcp-integration` |

## Phase 2: Setup

### 1. Create Project

```bash
npx create-next-app@latest my-ai-app \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir

cd my-ai-app
```

### 2. Install Dependencies

```bash
# Core AI SDK
npm install ai @ai-sdk/openai zod

# Vercel infrastructure
npm install @vercel/kv @vercel/postgres @vercel/blob

# UI
npm install lucide-react @codesandbox/sandpack-react

# Auth (ถ้าต้องการ)
npm install next-auth
```

### 3. Environment Variables

```bash
# .env.local
cat > .env.local << EOF
OPENAI_API_KEY=sk-...
POSTGRES_URL=postgres://...
KV_URL=redis://...
KV_REST_API_URL=...
KV_REST_API_TOKEN=...
BLOB_READ_WRITE_TOKEN=...
NEXTAUTH_SECRET=...
GITHUB_ID=...
GITHUB_SECRET=...
EOF
```

### 4. Database Setup (ถ้าใช้ Postgres)

```sql
-- schema.sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  chat_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_chat_id ON messages(chat_id);
```

## Phase 3: Build

### File Structure

```
my-ai-app/
├── app/
│   ├── api/
│   │   ├── chat/route.ts          # Main chat API
│   │   ├── upload/route.ts        # File upload
│   │   └── auth/[...nextauth]/    # Auth
│   ├── page.tsx                   # Main UI
│   └── layout.tsx                 # Root layout
├── lib/
│   ├── ai.ts                      # AI SDK config
│   ├── db.ts                      # Database client
│   ├── rag.ts                     # RAG logic
│   ├── tools.ts                   # AI tools
│   └── rate-limit.ts              # Rate limiting
├── components/
│   ├── chat.tsx                   # Chat UI
│   ├── message.tsx                # Message bubble
│   └── file-upload.tsx            # File upload
└── types/
    └── index.ts                   # TypeScript types
```

### Core Files

```typescript
// lib/ai.ts — AI SDK configuration
import { openai } from '@ai-sdk/openai';
import { createProviderRegistry } from 'ai';

export const registry = createProviderRegistry({
  openai,
});

export const defaultModel = openai('gpt-4o');
export const embeddingModel = openai.embedding('text-embedding-3-small');
```

```typescript
// lib/db.ts — Database client
import { createClient } from '@vercel/postgres';
import { kv } from '@vercel/kv';

export const db = createClient();

export async function saveMessage(chatId: string, message: any) {
  await db.sql`
    INSERT INTO messages (chat_id, role, content)
    VALUES (${chatId}, ${message.role}, ${message.content})
  `;
}

export async function loadMessages(chatId: string) {
  const { rows } = await db.sql`
    SELECT role, content FROM messages
    WHERE chat_id = ${chatId}
    ORDER BY created_at ASC
  `;
  return rows;
}

export async function saveToKV(key: string, value: any) {
  await kv.set(key, JSON.stringify(value));
}

export async function loadFromKV(key: string) {
  const data = await kv.get(key);
  return data ? JSON.parse(data as string) : null;
}
```

```typescript
// lib/rag.ts — RAG implementation
import { embed, generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { db } from './db';

export async function addDocument(content: string, metadata?: any) {
  const { embedding } = await embed({
    model: openai.embedding('text-embedding-3-small'),
    value: content,
  });

  await db.sql`
    INSERT INTO documents (content, embedding, metadata)
    VALUES (${content}, ${JSON.stringify(embedding)}::vector, ${JSON.stringify(metadata)})
  `;
}

export async function queryRAG(question: string) {
  const { embedding } = await embed({
    model: openai.embedding('text-embedding-3-small'),
    value: question,
  });

  const { rows } = await db.sql`
    SELECT content, 1 - (embedding <=> ${JSON.stringify(embedding)}::vector) as similarity
    FROM documents
    ORDER BY similarity DESC
    LIMIT 5
  `;

  const context = rows.map(r => r.content).join('\n\n');

  const { text } = await generateText({
    model: openai('gpt-4o'),
    system: `Answer based on this context:\n${context}`,
    prompt: question,
  });

  return { answer: text, sources: rows };
}
```

```typescript
// app/api/chat/route.ts — Main API
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { loadMessages, saveMessage } from '@/lib/db';
import { rateLimit } from '@/lib/rate-limit';

export async function POST(req: Request) {
  try {
    // Rate limiting
    const ip = req.headers.get('x-forwarded-for') || 'unknown';
    await rateLimit(ip, 10);

    const { messages, chatId } = await req.json();

    // Load history
    const history = chatId ? await loadMessages(chatId) : [];
    const allMessages = [...history, ...messages];

    // Stream response
    const result = streamText({
      model: openai('gpt-4o'),
      messages: allMessages,
    });

    // Save to DB (fire and forget)
    if (chatId) {
      const lastMessage = messages[messages.length - 1];
      saveMessage(chatId, lastMessage).catch(console.error);
    }

    return result.toDataStreamResponse();
  } catch (error) {
    return Response.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
```

```typescript
// components/chat.tsx — Main Chat UI
'use client';
import { useChat } from 'ai/react';
import { useState } from 'react';

export function Chat() {
  const [chatId] = useState(() => Math.random().toString(36).slice(2));
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
    body: { chatId },
  });

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(m => (
          <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${
              m.role === 'user' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 text-gray-900'
            }`}>
              {m.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-3 rounded-lg animate-pulse">
              Thinking...
            </div>
          </div>
        )}
      </div>
      
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={handleInputChange}
            placeholder="Type a message..."
            className="flex-1 p-2 border rounded-lg"
          />
          <button 
            type="submit" 
            disabled={isLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
```

## Phase 4: Integrate

### Add File Upload

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
```

### Add Vision Support

```typescript
// app/api/chat/route.ts — with vision
import { openai } from '@ai-sdk/openai';

export async function POST(req: Request) {
  const { messages, imageUrl } = await req.json();

  const result = streamText({
    model: openai('gpt-4o-vision'),
    messages: [
      ...messages,
      {
        role: 'user',
        content: [
          { type: 'text', text: 'What do you see in this image?' },
          { type: 'image', image: imageUrl },
        ],
      },
    ],
  });

  return result.toDataStreamResponse();
}
```

### Add Tool Calling

```typescript
// lib/tools.ts
import { tool } from 'ai';
import { z } from 'zod';

export const tools = {
  search: tool({
    description: 'Search the web',
    parameters: z.object({ query: z.string() }),
    execute: async ({ query }) => {
      const res = await fetch(`https://api.search.com?q=${query}`);
      return res.json();
    },
  }),
  
  calculator: tool({
    description: 'Calculate expression',
    parameters: z.object({ expression: z.string() }),
    execute: async ({ expression }) => {
      return { result: eval(expression) };
    },
  }),
};
```

## Phase 5: Deploy

### 1. Vercel CLI

```bash
# Login
vercel login

# Link project
vercel link

# Deploy preview
vercel

# Deploy production
vercel --prod
```

### 2. Environment Variables on Vercel

```bash
vercel env add OPENAI_API_KEY
vercel env add POSTGRES_URL
vercel env add KV_URL
```

### 3. Database Migration

```bash
# Run schema on Vercel Postgres
psql $POSTGRES_URL -f schema.sql
```

### 4. Custom Domain

```bash
vercel domains add your-domain.com
```

## Phase 6: Monitor

### Add Analytics

```typescript
// lib/analytics.ts
import { track } from '@vercel/analytics';

export function logChatEvent(event: string, data: any) {
  track(event, data);
}
```

### Add Error Tracking

```typescript
// lib/error.ts
export function logError(error: Error, context?: any) {
  console.error('[ERROR]', error.message, context);
  // Send to error tracking service
}
```

## Complete Project Checklist

- [ ] Next.js app created
- [ ] AI SDK installed
- [ ] API routes working
- [ ] Chat UI functional
- [ ] Database connected
- [ ] File upload working
- [ ] Auth implemented (if needed)
- [ ] Rate limiting active
- [ ] Deployed to Vercel
- [ ] Custom domain (optional)
- [ ] Analytics enabled

## References

- `vercel-ai-sdk-production` — Core AI SDK patterns
- `vercel-ai-agents` — Agent patterns
- `vercel-mcp-integration` — External API integration
- `vercel-v0-prompt-to-ui` — Generative UI
- `vercel-nextjs-patterns` — Next.js patterns
- `vercel-edge-deployment` — Edge deployment
