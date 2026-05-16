---
description: Initialize vault with _HERMES.md, index.md, log.md, templates
category: operations
triggers: ["init vault", "setup vault", "hermes init"]
---

# /hermes-init

Initialize a new vault with required files.

## Steps

1. Ask for vault path (default: ~/obsidian-vault)
2. Create directory structure
3. Generate files:
   - `_HERMES.md` — Operating manual
   - `index.md` — Page catalog
   - `log.md` — Activity timeline
   - `SOUL.md` — Identity template
   - `CRITICAL_FACTS.md` — Critical facts template
   - `PINNED.md` — Empty pinned file
4. Create subdirectories:
   - raw/{urls,pdfs,audio,images}
   - wiki/{entities,concepts,projects,daily,logs,reviews,tasks,decisions}
   - boards
   - templates
   - Research/{Web,X,YouTube,NotebookLM}
5. Copy templates from skill templates/
6. Report: vault initialized at [path]

## _HERMES.md Template

```markdown
# HERMES Operating Manual

This vault uses AI-first note rules.
Every note must follow `references/ai-first-rules.md`.

## Commands
- /hermes-save — Save conversation
- /hermes-world — Load context
- /hermes-ingest — Ingest source
- /hermes-synthesize — Find patterns
- /hermes-reconcile — Resolve contradictions
- /hermes-daily — Daily note
- /hermes-health — Vault audit

## Structure
- wiki/entities/ — People, companies
- wiki/concepts/ — Ideas, frameworks
- wiki/projects/ — Active work
- wiki/daily/ — Daily notes
- boards/ — Kanban
- Research/ — Research outputs

## Rules
1. Self-contained notes
2. "For future Hermes" preamble
3. Rich frontmatter
4. Recency markers
5. Sources verbatim
6. Mandatory [[wikilinks]]
7. Confidence levels
```

## AI-First Rule

Every generated file MUST follow `references/ai-first-rules.md`.
