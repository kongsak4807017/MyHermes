---
name: vercel-v0-prompt-to-ui
description: "v0.dev integration: convert prompts, screenshots, and sketches to production React components using AI."
version: 1.0.0
author: Hermes Agent
license: MIT
dependencies: [nextjs, react, typescript, ai-sdk]
metadata:
  hermes:
    tags: [v0, v0.dev, Generative UI, Image-to-Code, Prompt-to-UI, React]
---

# v0.dev Prompt-to-UI Integration

Patterns for building v0.dev-like generative UI capabilities in your own applications.

## When to use

**Use when:**
- Converting text prompts to React components
- Converting screenshots/images to code
- Building AI-powered design tools
- Generating UI from natural language
- Creating rapid prototyping workflows

## Architecture

```
User Input (Prompt/Image)
         │
         ▼
┌─────────────────────┐
│  AI Vision Model     │
│  (GPT-4o / Claude)  │
│                     │
│  "Generate React     │
│   component for..."  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Generated Code      │
│  (React + Tailwind)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Live Preview        │
│  (Sandpack/Preview)  │
└─────────────────────┘
```

## Quick Start

### Installation

```bash
npm install ai @ai-sdk/openai @codesandbox/sandpack-react
```

## Patterns

### Pattern 1: Text-to-React Component

```typescript
// app/api/generate-ui/route.ts
import { openai } from '@ai-sdk/openai';
import { generateText } from 'ai';

const SYSTEM_PROMPT = `You are an expert React developer. Generate production-ready React components using:
- React 18+ with TypeScript
- Tailwind CSS for styling
- Lucide React for icons
- shadcn/ui patterns where applicable

Output ONLY the component code, no explanations. Use default export.`;

export async function POST(req: Request) {
  const { prompt } = await req.json();

  const { text } = await generateText({
    model: openai('gpt-4o'),
    system: SYSTEM_PROMPT,
    prompt: `Generate a React component for: ${prompt}`,
    temperature: 0.7,
  });

  // Extract code from markdown if wrapped
  const code = text.replace(/```tsx?\n?/g, '').replace(/```\n?/g, '').trim();

  return Response.json({ code });
}
```

```typescript
// app/generate/page.tsx
'use client';
import { useState } from 'react';
import { Sandpack } from '@codesandbox/sandpack-react';

export default function GenerateUIPage() {
  const [prompt, setPrompt] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);

  async function generate() {
    setLoading(true);
    const res = await fetch('/api/generate-ui', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
    const data = await res.json();
    setCode(data.code);
    setLoading(false);
  }

  return (
    <div className="p-4">
      <textarea
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        placeholder="Describe the UI you want..."
        className="w-full h-32 p-2 border rounded"
      />
      <button onClick={generate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate UI'}
      </button>
      
      {code && (
        <Sandpack
          template="react-ts"
          files={{
            '/App.tsx': code,
          }}
          options={{
            showNavigator: true,
            showTabs: true,
          }}
        />
      )}
    </div>
  );
}
```

### Pattern 2: Screenshot-to-Code

```typescript
// app/api/screenshot-to-code/route.ts
import { openai } from '@ai-sdk/openai';
import { generateText } from 'ai';

export async function POST(req: Request) {
  const formData = await req.formData();
  const image = formData.get('image') as File;
  
  // Convert to base64
  const bytes = await image.arrayBuffer();
  const base64 = Buffer.from(bytes).toString('base64');
  const dataUrl = `data:image/png;base64,${base64}`;

  const { text } = await generateText({
    model: openai('gpt-4o-vision'),
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'text',
            text: `Convert this screenshot to a React component. 
Use Tailwind CSS. Match the design exactly.
Output only the code.`,
          },
          {
            type: 'image',
            image: dataUrl,
          },
        ],
      },
    ],
  });

  return Response.json({ code: text });
}
```

### Pattern 3: Sketch-to-Code

```typescript
// app/api/sketch-to-code/route.ts
import { openai } from '@ai-sdk/openai';

export async function POST(req: Request) {
  const { sketchDataUrl, description } = await req.json();

  const { text } = await generateText({
    model: openai('gpt-4o-vision'),
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'text',
            text: `This is a hand-drawn sketch of: ${description}
Convert it to a polished React component with Tailwind CSS.`,
          },
          {
            type: 'image',
            image: sketchDataUrl,
          },
        ],
      },
    ],
  });

  return Response.json({ code: text });
}
```

### Pattern 4: Iterative Refinement

```typescript
// app/api/refine-ui/route.ts
import { openai } from '@ai-sdk/openai';

export async function POST(req: Request) {
  const { currentCode, feedback } = await req.json();

  const { text } = await generateText({
    model: openai('gpt-4o'),
    system: `You are refining a React component. Keep the same structure but apply the requested changes.
Output ONLY the updated code.`,
    messages: [
      {
        role: 'user',
        content: `Current code:\n\n${currentCode}\n\nChanges requested: ${feedback}`,
      },
    ],
  });

  return Response.json({ code: text });
}
```

### Pattern 5: Component Library Generation

```typescript
// lib/ui-generator.ts
import { generateObject } from 'ai';
import { z } from 'zod';

const componentSchema = z.object({
  name: z.string(),
  description: z.string(),
  props: z.array(z.object({
    name: z.string(),
    type: z.string(),
    required: z.boolean(),
    description: z.string(),
  })),
  code: z.string(),
});

export async function generateComponentLibrary(requirements: string[]) {
  const components = [];
  
  for (const req of requirements) {
    const { object } = await generateObject({
      model: openai('gpt-4o'),
      schema: componentSchema,
      prompt: `Generate a React component for: ${req}`,
    });
    
    components.push(object);
  }
  
  return components;
}
```

### Pattern 6: Live Preview with Sandpack

```typescript
// components/live-preview.tsx
'use client';
import { Sandpack } from '@codesandbox/sandpack-react';

interface LivePreviewProps {
  code: string;
  dependencies?: Record<string, string>;
}

export function LivePreview({ code, dependencies = {} }: LivePreviewProps) {
  return (
    <Sandpack
      template="react-ts"
      files={{
        '/App.tsx': code,
      }}
      customSetup={{
        dependencies: {
          'lucide-react': 'latest',
          'tailwind-merge': 'latest',
          'clsx': 'latest',
          ...dependencies,
        },
      }}
      options={{
        showNavigator: true,
        showTabs: true,
        showLineNumbers: true,
        editorHeight: 400,
      }}
    />
  );
}
```

## Deployment

```bash
# Install dependencies
npm install ai @ai-sdk/openai @codesandbox/sandpack-react

# Environment variables
echo "OPENAI_API_KEY=sk-..." > .env.local

# Deploy
vercel --prod
```

## References

- https://v0.dev
- https://sandpack.codesandbox.io
- https://sdk.vercel.ai/docs
