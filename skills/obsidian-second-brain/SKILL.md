---
name: obsidian-second-brain
description: "Hermes implementation of obsidian-second-brain: self-rewriting vault with AI-first notes, auto-synthesis, scheduled agents, and progressive context loading. Turns any Obsidian vault into a living second brain."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [obsidian, cronjob]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Obsidian, Second Brain, AI-First, Auto-Synthesis, Vault, Knowledge Management, Context Loading, Scheduled Agents]
---

# obsidian-second-brain for Hermes

Hermes implementation of Eugeniu Ghelbur's obsidian-second-brain pattern. A self-rewriting vault that maintains itself while you sleep.

## What's inside

- **AI-first note rules** — Notes written for future-Hermes, not humans
- **Progressive context loading** — L0-L3 context levels to avoid token burn
- **Auto-synthesis** — Finds patterns and writes connection pages automatically
- **Auto-reconcile** — Resolves contradictions across sources
- **Scheduled agents** — Nightly, weekly, health checks via cronjob
- **33 commands** — 4 layers: Operations, Thinking, Context, Research

## Quick start

```bash
# 1. Initialize vault
/hermes-world init

# 2. Set your identity
/hermes-world identity

# 3. Save a conversation
/hermes-save

# 4. Load context for new session
/hermes-world
```

## Architecture

```
Hermes Session
    |
    +-- L0: Identity (~170 tokens) — SOUL.md, CRITICAL_FACTS.md, PINNED.md
    +-- L1: Navigation (~1-2K) — index.md, log.md (last 10)
    +-- L2: Current State (~2-5K) — Dashboard, today's note, active boards
    +-- L3: Deep Context (~5-20K) — Full project notes, source articles (on demand)
    |
    +-- Operations Layer — save, ingest, synthesize, reconcile, daily, task, etc.
    +-- Thinking Layer — challenge, emerge, connect, graduate
    +-- Context Layer — world loading, identity, state
    +-- Research Layer — x-read, x-pulse, research, research-deep, youtube
    |
    +-- Scheduled Agents (cronjob)
        +-- nightly — close day, reconcile, synthesize, heal orphans
        +-- weekly — review, pattern detection
        +-- health — vault audit, stale claims, contradictions
```

## AI-First Note Rules (Non-negotiable)

Every note MUST follow these rules. See `references/ai-first-rules.md` for full spec.

1. **Self-contained** — Explain what, why, when inside the note
2. **`## For future Hermes` preamble** — 2-3 sentence summary at top
3. **Rich frontmatter** — `type`, `date`, `tags`, `ai-first: true`
4. **Recency markers** — `(as of YYYY-MM, source.com)` per external claim
5. **Sources verbatim** — URLs inline, not paraphrased
6. **Mandatory `[[wikilinks]]`** — Every person, project, concept linked
7. **Confidence levels** — `stated | high | medium | speculation`

## Commands

### Operations Layer (21 commands)

| Command | What it does |
|---------|-------------|
| `/hermes-save` | Save conversation — decisions, tasks, people, ideas to vault |
| `/hermes-ingest` | Ingest URL/PDF/audio/image — vault rewrites itself |
| `/hermes-synthesize` | Auto-find patterns, write synthesis pages |
| `/hermes-reconcile` | Find and resolve contradictions |
| `/hermes-export` | Clean JSON/markdown snapshot |
| `/hermes-daily` | Create/update today's daily note |
| `/hermes-log` | Log work session, link everywhere |
| `/hermes-task` | Add task to right board with priority/due |
| `/hermes-person` | Create/update person note |
| `/hermes-decide` | Log decision to project note |
| `/hermes-capture` | Zero-friction idea capture |
| `/hermes-find` | Smart search with context |
| `/hermes-recap` | Summary of day/week/month |
| `/hermes-review` | Structured weekly/monthly review |
| `/hermes-board` | Kanban board view and updates |
| `/hermes-project` | Project note with board and daily links |
| `/hermes-health` | Vault audit — contradictions, gaps, stale claims |
| `/hermes-adr` | Decision records |
| `/hermes-visualize` | Generate visual canvas map |
| `/hermes-learn` | Review learnings, prune stale, surface patterns |
| `/hermes-init` | Generate _HERMES.md, index.md, log.md |

### Thinking Layer (4 commands)

| Command | What it does |
|---------|-------------|
| `/hermes-challenge` | Vault argues against your idea using your history |
| `/hermes-emerge` | Surface patterns from 30 days of notes |
| `/hermes-connect` | Bridge two unrelated domains |
| `/hermes-graduate` | Turn idea fragment into full project |

### Context Layer (1 command)

| Command | What it does |
|---------|-------------|
| `/hermes-world` | Load identity + state with L0-L3 progressive loading |

### Research Layer (6 commands)

| Command | What it does |
|---------|-------------|
| `/x-read` | Deep-read X post — verbatim + TL;DR + claims |
| `/x-pulse` | Scan X for trending topics |
| `/research` | Web research with citations |
| `/research-deep` | Vault-first synthesis — scan vault, fill gaps |
| `/notebooklm` | Vault-grounded synthesis |
| `/youtube` | Extract transcript + summary + quotes |

## Scheduled Agents

Set up via `cronjob`:

```bash
# Nightly agent (10 PM)
hermes cronjob create --name "osb-nightly" --schedule "0 22 * * *" \
  --prompt "Run obsidian-second-brain nightly agent: close day, reconcile contradictions, synthesize patterns, heal orphans, rebuild index"

# Weekly review (Fridays 6 PM)
hermes cronjob create --name "osb-weekly" --schedule "0 18 * * 5" \
  --prompt "Run obsidian-second-brain weekly review"

# Health check (Sundays 9 PM)
hermes cronjob create --name "osb-health" --schedule "0 21 * * 0" \
  --prompt "Run obsidian-second-brain vault health audit"
```

## Vault Structure

```
vault/
├── _HERMES.md          # Operating manual (Claude's CLAUDE.md equivalent)
├── index.md            # Page catalog
├── log.md              # Activity timeline
├── SOUL.md             # Identity
├── CRITICAL_FACTS.md   # ~120 tokens always loaded
├── PINNED.md           # Session-specific pinned context
├── raw/                # Immutable sources
│   ├── urls/
│   ├── pdfs/
│   ├── audio/
│   └── images/
├── wiki/
│   ├── entities/       # People, companies, tools
│   ├── concepts/       # Ideas, frameworks
│   ├── projects/       # Project notes
│   ├── daily/          # Daily notes (YYYY-MM-DD.md)
│   ├── logs/           # Work session logs
│   ├── reviews/        # Weekly/monthly reviews
│   ├── tasks/          # Task notes
│   └── decisions/      # ADRs
├── boards/             # Kanban boards
├── templates/          # Note templates
└── Research/           # Research outputs
    ├── Web/
    ├── X/
    ├── YouTube/
    └── NotebookLM/
```

## Resources

- Original: https://github.com/eugeniughelbur/obsidian-second-brain
- Karpathy's LLM Wiki: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Hermes obsidian skill: `skill_view(name="obsidian")`
