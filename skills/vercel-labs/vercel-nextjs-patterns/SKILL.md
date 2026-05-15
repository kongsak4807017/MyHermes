---
name: vercel-nextjs-patterns
description: "Next.js patterns from Vercel Labs: App Router, auth, data fetching, partial prerendering, RSC, and Edge deployment."
version: 1.0.0
author: Hermes Agent (derived from vercel-labs repos)
license: MIT
dependencies: [nextjs, react, typescript]
metadata:
  hermes:
    tags: [Next.js, App Router, Auth, Data Fetching, Edge, RSC, Vercel]
---

# Vercel Next.js Patterns

Patterns for building Next.js applications from vercel-labs repositories.

## When to use

**Use when building:**
- Next.js App Router applications
- Authentication flows with Next.js
- Data fetching patterns
- Partial prerendering (PPR)
- React Server Components with AI
- Edge-deployed Next.js apps

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js App Router                          │
│              ┌─────────────┐  ┌─────────────┐             │
│              │     RSC      │  │   Client    │             │
│              │  (Server)    │  │ Components  │             │
│              └──────┬──────┘  └──────┬──────┘             │
│                     │                │                     │
│              ┌──────▼────────────────▼──────┐             │
│              │      API Routes / Edge        │             │
│              └─────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
npx create-next-app@latest my-app --typescript --tailwind --app
```

## Patterns

### Pattern 1: App Router Auth

From `app-router-auth`:

```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth';
import GitHub from 'next-auth/providers/github';

const handler = NextAuth({
  providers: [
    GitHub({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
  ],
  callbacks: {
    async session({ session, token }) {
      session.user.id = token.sub;
      return session;
    },
  },
});

export { handler as GET, handler as POST };
```

```typescript
// middleware.ts
import { withAuth } from 'next-auth/middleware';

export default withAuth({
  callbacks: {
    authorized({ req, token }) {
      if (req.nextUrl.pathname.startsWith('/admin')) {
        return token?.role === 'admin';
      }
      return !!token;
    },
  },
});

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*'],
};
```

### Pattern 2: Data Fetching

From `next-fetch`:

```typescript
// lib/data.ts
export async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 60 }, // ISR
  });
  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
}

// app/posts/page.tsx (RSC)
import { getPosts } from '@/lib/data';

export default async function PostsPage() {
  const posts = await getPosts();
  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

### Pattern 3: Partial Prerendering (PPR)

From `next-partial-prerendering`:

```typescript
// next.config.js
module.exports = {
  experimental: {
    ppr: true,
  },
};
```

```typescript
// app/page.tsx
import { Suspense } from 'react';
import { StaticContent } from './static';
import { DynamicContent } from './dynamic';

export default function Page() {
  return (
    <div>
      {/* Static - prerendered at build time */}
      <StaticContent />
      
      {/* Dynamic - streamed at request time */}
      <Suspense fallback={<Skeleton />}>
        <DynamicContent />
      </Suspense>
    </div>
  );
}
```

```typescript
// app/dynamic.tsx
export const dynamic = 'force-dynamic'; // Opt out of static

export default async function DynamicContent() {
  const data = await fetchRealtimeData();
  return <div>{data}</div>;
}
```

### Pattern 4: RSC with LLM

From `rsc-llm-on-the-edge`:

```typescript
// app/api/generate/route.ts
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

export const runtime = 'edge';

export async function POST(req: Request) {
  const { prompt } = await req.json();
  
  const { text } = await generateText({
    model: openai('gpt-4o-mini'),
    prompt,
  });
  
  return Response.json({ text });
}
```

```typescript
// app/page.tsx
export const runtime = 'edge';

export default async function Page() {
  // Server-side LLM call
  const { text } = await generateText({
    model: openai('gpt-4o-mini'),
    prompt: 'Generate a welcome message',
  });
  
  return <h1>{text}</h1>;
}
```

### Pattern 5: Edge Runtime

From `next-on-the-edge`:

```typescript
// app/api/edge/route.ts
export const runtime = 'edge';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const query = searchParams.get('q');
  
  // Edge-compatible fetch
  const res = await fetch(`https://api.example.com?q=${query}`);
  const data = await res.json();
  
  return Response.json(data);
}
```

### Pattern 6: SPA with Drizzle

From `next-spa-drizzle`:

```typescript
// db/schema.ts
import { pgTable, serial, varchar, timestamp } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull(),
  createdAt: timestamp('created_at').defaultNow(),
});
```

```typescript
// app/api/users/route.ts
import { db } from '@/db';
import { users } from '@/db/schema';

export async function GET() {
  const allUsers = await db.select().from(users);
  return Response.json(allUsers);
}
```

### Pattern 7: Flight Search (Complex Forms)

From `next-flights`:

```typescript
// app/search/page.tsx
import { searchFlights } from './actions';

export default function SearchPage() {
  return (
    <form action={searchFlights}>
      <input name="origin" required />
      <input name="destination" required />
      <input type="date" name="departure" required />
      <button type="submit">Search</button>
    </form>
  );
}
```

```typescript
// app/search/actions.ts
'use server';

export async function searchFlights(formData: FormData) {
  const origin = formData.get('origin');
  const destination = formData.get('destination');
  
  // Server-side search
  const flights = await fetchFlightData({ origin, destination });
  
  // Revalidate and redirect
  revalidatePath('/results');
  redirect(`/results?${new URLSearchParams({ origin, destination })}`);
}
```

## Deployment

### Vercel
```bash
vercel --prod
```

### Environment Variables
```
NEXTAUTH_SECRET=...
GITHUB_ID=...
GITHUB_SECRET=...
DATABASE_URL=...
OPENAI_API_KEY=...
```

## References

- https://github.com/vercel-labs/next-fetch
- https://github.com/vercel-labs/app-router-auth
- https://github.com/vercel-labs/next-partial-prerendering
