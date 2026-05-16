---
description: Auto-find patterns across sources and write synthesis pages
category: operations
triggers: ["find patterns", "synthesize vault", "connect dots", "hermes synthesize"]
---

# /hermes-synthesize

Find unnamed patterns across vault sources and write synthesis pages.

## Steps

1. Read `_HERMES.md` first
2. Scan recent notes (last 30 days):
   - Daily notes
   - Project updates
   - Research outputs
   - Idea captures
3. Identify recurring themes:
   - Same concept mentioned in different contexts
   - Similar problems across projects
   - Connected ideas not yet linked
   - Emerging patterns
4. For each pattern found:
   - Check if synthesis page already exists
   - If not: Create `wiki/concepts/Pattern Name.md`
   - Link all source notes with `[[wikilinks]]`
   - Write synthesis with evidence
5. Update `index.md`
6. Report: patterns found, synthesis pages created

## Example Output

```
Patterns found:
1. "Onboarding friction" — mentioned in 4 unrelated projects
   → Created: wiki/concepts/Onboarding Friction.md

2. "API versioning" — recurring concern across 3 projects
   → Created: wiki/concepts/API Versioning Strategy.md

3. "Memory tools" — research + project overlap
   → Updated: wiki/concepts/AI Memory Tools.md
```

## AI-First Rule

Every synthesis page MUST follow `references/ai-first-rules.md`.
