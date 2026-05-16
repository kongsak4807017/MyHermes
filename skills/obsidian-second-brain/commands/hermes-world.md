---
description: Load your identity, values, priorities, and current state with progressive context levels
category: context
triggers: ["load context", "what is going on", "where am I", "load my world", "hermes world"]
---

# /hermes-world

Load identity + state with progressive L0-L3 context levels.

## Steps

1. **L0 — Identity (~170 tokens)**
   - Read `SOUL.md` — who the user is, communication style
   - Read `CRITICAL_FACTS.md` — timezone, manager, location, role
   - Read `PINNED.md` — session-specific pinned context

2. **L1 — Navigation (~1-2K tokens)**
   - Read `index.md` — catalog of all vault pages
   - Read `log.md` (last 10 entries) — recent activity

3. **L2 — Current State (~2-5K tokens)**
   - Read `Dashboard.md` or `Home.md` — current priorities
   - Read today's daily note
   - Read last 3 daily notes for momentum
   - Scan active kanban boards

4. **L3 — Deep Context (~5-20K tokens, on demand only)**
   - Read active project notes
   - Read full source articles if asked
   - Identify key people from last 7 days

## Output

Present brief status after L0-L2:
- Who I am to you (persona confirmation)
- Current priorities (top 3-5 active threads)
- Open threads from last session
- Overdue / needs attention
- Today so far

## Core Memory Pinning

During complex tasks, pin critical info to `PINNED.md`:
- Task-specific facts, schemas, reference data
- Loaded at L0 alongside SOUL.md
- Clear when task done
- Proactively suggest pinning when user is deep in complex task

## AI-First Rule

Every note created MUST follow `references/ai-first-rules.md`.
