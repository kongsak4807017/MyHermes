---
name: auto-mempalace
description: "Make Hermes automatically use MemPalace MCP tools without explicit user commands."
title: Auto MemPalace
version: 1.1.0
category: memory
---

# Auto MemPalace

Make Hermes automatically use MemPalace MCP tools without waiting for explicit user commands. This skill covers both the behavioral guidance approach (system prompt injection) and the operational patterns for keeping a MemPalace palace populated and useful.

## When to Use

- User wants Hermes to "just know" what they did in past sessions
- User asks recall questions: "what did we do", "why did we decide X", "tell me about project Y"
- User wants automatic memory capture after significant work sessions
- Memory is full (2,200 char limit) and can't hold more procedural instructions

## How It Works

MemPalace exposes 33 MCP tools. By default, Hermes only calls them when the user explicitly mentions MemPalace. To make them **auto-trigger**, inject behavioral guidance into the system prompt. See the `native-mcp` skill for the full pattern — this skill covers MemPalace-specific usage.

## Trigger Conditions for Search

Before answering, ALWAYS call `mcp_mempalace_search` when the user asks:
- "เราเคยทำอะไรไว้" / "what did we do"
- "ทำไมถึงตัดสินใจแบบนี้" / "why did we decide"
- "บอกเรื่อง project X" / "tell me about project X"
- "ฉันรู้อะไรเกี่ยวกับ Y" / "what do I know about Y"
- "หาให้หน่อย" / "find that thing we talked about"
- Any question referencing past work, decisions, or stored knowledge

## Auto-Write After Sessions

After significant sessions, call `mcp_mempalace_diary_write` to record:
- Bug fixes and workarounds discovered
- Important decisions and their rationale
- Project structure changes
- Tool/dependency setup steps
- Provider quirks or API behavior learned

## Tool Quick Reference

| Tool | When to Use |
|------|-------------|
| `mcp_mempalace_search` | Before answering recall questions |
| `mcp_mempalace_diary_write` | After significant sessions |
| `mcp_mempalace_mine` | Store verbatim facts (API keys, paths, config values) |
| `mcp_mempalace_add_drawer` | Create a new topic/drawer |
| `mcp_mempalace_graph_query` | Find connections between topics |
| `mcp_mempalace_status` | Check palace health |

## Palace Info

- Path: `/home/user/.mempalace/palace`
- Embedding: `all-MiniLM-L6-v2` (local CPU, no API key needed)
- Backend: ChromaDB with HNSW cosine index
- 33 tools available via MCP

## Setup Checklist

1. Install MemPalace: `pip install -e ".[dev]"` in a venv
2. Init palace: `mempalace init ~/mempalace-palace --yes`
3. Add to `~/.hermes/config.yaml` under `mcp_servers`
4. Restart Hermes — tools auto-discover
5. Inject system prompt guidance (see `native-mcp` skill)
6. Populate palace with initial data (project contexts, user preferences)

## Pitfalls

- **Empty palace**: Search returns nothing if no data was ever written. Populate early.
- **Wrong tool names**: Tools are prefixed — use `mcp_mempalace_search` not `mempalace_search`.
- **Model ignores guidance**: Some models need explicit reminders. If auto-trigger fails, fall back to calling the tool directly.
- **Over-capture**: Don't diary-write after every trivial chat. Save significant sessions only.

## References

- `references/code-patches.md` — exact patches for system prompt injection (MemPalace + generic MCP pattern)
- `references/multi-agent-delegation.md` — using delegate_task with different providers/models
- `references/delegation-auto-trigger.md` — same injection pattern applied to auto-delegate
