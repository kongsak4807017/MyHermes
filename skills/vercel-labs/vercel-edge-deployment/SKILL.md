---
name: vercel-edge-deployment
description: "Edge deployment patterns from Vercel Labs: React/Remix on Edge, ffmpeg, image generation, and Edge Functions."
version: 1.0.0
author: Hermes Agent (derived from vercel-labs repos)
license: MIT
dependencies: [vercel, edge-functions]
metadata:
  hermes:
    tags: [Edge, Vercel Edge Functions, Remix, React, ffmpeg, Deployment]
---

# Vercel Edge Deployment

Patterns for deploying applications to Vercel Edge from vercel-labs repositories.

## When to use

**Use when:**
- Deploying React/Remix to Edge Functions
- Running ffmpeg on Vercel
- Building Edge-native APIs
- Deploying React 19 experimental features
- Need low-latency global execution

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Vercel Edge Network                         │
│         ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│         │  Edge   │ │  Edge   │ │  Edge   │              │
│         │  Node 1 │ │  Node 2 │ │  Node N │              │
│         │ (US)    │ │ (EU)    │ │ (Asia)  │              │
│         └────┬────┘ └────┬────┘ └────┬────┘              │
│              │           │           │                     │
│              └───────────┴───────────┘                     │
│                         │                                  │
│              ┌──────────▼──────────┐                      │
│              │    Vercel Origin     │                      │
│              └───────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Edge Function

```typescript
// app/api/hello/route.ts
export const runtime = 'edge';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const name = searchParams.get('name') || 'World';
  
  return Response.json({ 
    message: `Hello ${name}!`,
    region: process.env.VERCEL_REGION,
  });
}
```

## Patterns

### Pattern 1: React on Edge

From `react-on-the-edge`:

```typescript
// app/page.tsx
export const runtime = 'edge';

export default async function Page() {
  // Edge-rendered React
  const data = await fetch('https://api.example.com/data', {
    cf: { cacheTtl: 300 },
  }).then(r => r.json());
  
  return (
    <div>
      <h1>Edge Rendered</h1>
      <pre>{JSON.stringify(data)}</pre>
    </div>
  );
}
```

### Pattern 2: Remix on Edge

From `remix-on-the-edge`:

```typescript
// entry.server.tsx
import { handleRequest } from '@vercel/remix';

export default function (
  request: Request,
  responseStatusCode: number,
  responseHeaders: Headers,
  remixContext: EntryContext
) {
  return handleRequest(
    request,
    responseStatusCode,
    responseHeaders,
    remixContext
  );
}
```

```typescript
// app/routes/_index.tsx
export const config = { runtime: 'edge' };

export default function Index() {
  return <div>Remix on Edge!</div>;
}
```

### Pattern 3: ffmpeg on Vercel

From `ffmpeg-on-vercel`:

```typescript
// app/api/convert/route.ts
import { ffmpeg } from '@ffmpeg/ffmpeg';

export const runtime = 'edge';

export async function POST(req: Request) {
  const formData = await req.formData();
  const file = formData.get('file') as File;
  
  const bytes = await file.arrayBuffer();
  
  // Run ffmpeg in Edge Function
  const result = await ffmpeg({
    args: ['-i', 'input.mp4', '-vf', 'scale=640:-2', 'output.mp4'],
    stdin: Buffer.from(bytes),
  });
  
  return new Response(result.stdout, {
    headers: { 'Content-Type': 'video/mp4' },
  });
}
```

### Pattern 4: React 19 on Vercel

From `react-19-on-vercel`:

```typescript
// next.config.js
module.exports = {
  experimental: {
    reactCompiler: true,
  },
};
```

```typescript
// app/page.tsx
// React 19 features: use(), Suspense boundaries, Server Actions
import { use } from 'react';

export default function Page() {
  const data = use(fetchData());
  
  return <div>{data.title}</div>;
}
```

### Pattern 5: Image Generation on Edge

From `vercel-fal-image-generator`:

```typescript
// app/api/generate-image/route.ts
export const runtime = 'edge';

export async function POST(req: Request) {
  const { prompt } = await req.json();
  
  const response = await fetch('https://fal.run/fal-ai/flux', {
    method: 'POST',
    headers: {
      'Authorization': `Key ${process.env.FAL_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt }),
  });
  
  const result = await response.json();
  return Response.json(result);
}
```

## Deployment

### Vercel CLI
```bash
vercel --prod
```

### Edge Config
```typescript
import { get } from '@vercel/edge-config';

export async function GET(req: Request) {
  const featureFlag = await get('new-feature');
  if (featureFlag) {
    return Response.json({ version: 'v2' });
  }
  return Response.json({ version: 'v1' });
}
```

## References

- https://github.com/vercel-labs/react-on-the-edge
- https://github.com/vercel-labs/remix-on-the-edge
- https://github.com/vercel-labs/ffmpeg-on-vercel
