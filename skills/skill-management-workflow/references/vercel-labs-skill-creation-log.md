# Vercel Labs → Skills Conversion Session Log

## Session: 2026-05-07

## What was requested

User asked to study all repos in https://github.com/vercel-labs and convert them to Hermes Agent skills.

## Approach taken

### Phase 1: Discovery
- Fetched 100 repos from GitHub API (`/orgs/vercel-labs/repos?per_page=100`)
- Sorted by stargazers_count
- Grouped by domain: ai-sdk (33), mcp (8), chatbot (3), nextjs (12), edge (8), microfrontends, other (35)

### Phase 2: README Fetching
- Fetched raw README.md from each repo (main branch, fallback to master)
- Got 65/67 repos successfully
- Stored at `/tmp/vercel-labs-readmes.json`

### Phase 3: Analysis
- Extracted tech stack mentions (nextjs, react, ai_sdk, vercel, openai, postgres, mcp, edge, streaming, rag, auth)
- Counted code blocks per repo
- Grouped into skill domains

### Phase 4: Skill Creation
Created 10 skills under `~/.hermes/skills/vercel-labs/`:

| Skill | Lines | Source repos | Content |
|-------|-------|-------------|---------|
| vercel-ai-sdk-patterns | 607 | 40 ai-sdk-* repos | 20 patterns: streaming, RAG, generative UI, multi-step agents, tool calling, structured output, provider registry, image generation, computer use, reasoning mode |
| vercel-ai-sdk-production | 549 | Same + deploy docs | Real npm packages, Vercel KV/Postgres/Blob integration, rate limiting, monitoring, CI/CD |
| vercel-mcp-integration | 403 | 8 mcp-* repos | stdio/HTTP/SSE transport, AI SDK bridge, Express MCP, Stripe/Contentful integration |
| vercel-ai-agents | 488 | coding-agent-template, tersa, lead-agent, deep-research-template, etc. | 10 patterns: coding agent with sandbox, dev timeline, workflow canvas, lead gen, data analyst, deep research, x402 payment, Vectr, multi-agent orchestration |
| vercel-nextjs-patterns | 314 | next-fetch, app-router-auth, next-partial-prerendering, etc. | App Router auth, data fetching, PPR, RSC+LLM, Edge runtime, SPA+Drizzle |
| vercel-edge-deployment | 223 | react-on-the-edge, remix-on-the-edge, ffmpeg-on-vercel, etc. | React/Remix on Edge, ffmpeg, image generation, React 19 |
| vercel-chatbot-patterns | 239 | gemini-chatbot, chatgpt-apps-sdk-nextjs-starter, etc. | Gemini chatbot, ChatGPT starter, AI gateway, generative UI, multi-model |
| vercel-v0-prompt-to-ui | 336 | v0 patterns from ai-sdk repos | Text-to-React, Screenshot-to-code, Sketch-to-code, Sandpack live preview |
| vercel-web-interface-guidelines | 156 | web-interface-guidelines | Loading states, command palette, toast notifications, responsive tables |
| vercel-fullstack-ai-app | 509 | All above combined | End-to-end workflow: PLAN → SETUP → BUILD → INTEGRATE → DEPLOY → MONITOR |

### Phase 5: Production Upgrade
User asked to make skills "as powerful as vercel.com" — created production-focused skills with:
- Real `npm install ai @ai-sdk/openai` commands
- Actual `.env.local` templates
- `vercel --prod` deploy commands
- Database schemas and migration scripts
- Rate limiting with `@vercel/kv`
- Monitoring with `@vercel/analytics`
- v0.dev-like patterns with `@codesandbox/sandpack-react`

## Key techniques learned

### README fetching at scale
```python
for repo in repos:
    for branch in ['main', 'master']:
        url = f"https://raw.githubusercontent.com/{org}/{repo}/{branch}/README.md"
        r = subprocess.run(["curl", "-sL", "--max-time", "10", url], ...)
        if success: break
```

### Tech stack detection from README
```python
tech_patterns = {
    'nextjs': bool(re.search(r'next\.js|Next\.js|nextjs', readme, re.I)),
    'ai_sdk': bool(re.search(r'ai sdk|AI SDK|@ai-sdk', readme, re.I)),
    'mcp': bool(re.search(r'mcp|MCP', readme, re.I)),
    # ...
}
```

### Using write_file() for complex skills
For skills >300 lines, `write_file(path="~/.hermes/skills/<name>/SKILL.md", content="...")` is more reliable than `skill_manage(action='create')` which can fail on complex YAML frontmatter parsing.

## Pitfalls encountered

1. **skill_manage create fails on long content** — use write_file() instead for complex skills
2. **YAML frontmatter parsing** — keep frontmatter simple, put complex content in body
3. **Grouping decisions** — some repos fit multiple categories (e.g., coding-agent-template has both ai-sdk and mcp). Chose primary domain based on main purpose.
4. **README truncation** — GitHub raw READMEs can be very long. Truncated at 5000 chars for analysis, but fetched full content for important repos.

## User preference signals

- User prefers Thai/English mixed communication
- User wants direct, efficient execution without excessive back-and-forth
- User expects production-ready code, not just theory/patterns
- User values comprehensive skill libraries (10 skills created in one session)
