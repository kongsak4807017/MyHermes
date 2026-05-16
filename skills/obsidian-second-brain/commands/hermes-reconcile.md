---
description: Find and resolve contradictions across vault notes
category: operations
triggers: ["resolve contradictions", "fix conflicts", "hermes reconcile"]
---

# /hermes-reconcile

Find contradictions across vault notes and resolve them.

## Steps

1. Read `_HERMES.md` first
2. Scan vault for potential contradictions:
   - Same entity with different attributes
   - Same claim with different values
   - Decisions that contradict each other
   - Facts with different recency markers
3. For each contradiction found:
   - Identify source notes
   - Determine most recent/credible source
   - Rewrite notes with resolved truth
   - Document why resolution was chosen
   - Add to `wiki/decisions/Reconciliations.md`
4. Update affected notes with `updated:` frontmatter
5. Report: contradictions found, resolutions made

## Contradiction Types

| Type | Example | Resolution |
|------|---------|------------|
| Entity conflict | Person has different role in two notes | Use most recent interaction |
| Fact conflict | Same stat with different values | Use source with recency marker |
| Decision conflict | Two decisions point opposite ways | Check ADR, use most recent |
| Temporal conflict | Old fact vs new fact | Bi-temporal: track both with dates |

## AI-First Rule

Every note updated MUST follow `references/ai-first-rules.md`.
