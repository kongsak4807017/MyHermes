# MemPalace vs SocratiCode Comparison

Extracted from session analysis comparing two MCP-based memory systems.

## Overview

| | MemPalace | SocratiCode |
|---|-----------|-------------|
| **Focus** | Personal memory / conversation context | Codebase intelligence |
| **Data** | Conversations, entities, diary entries | Source code, dependencies, AST |
| **Storage** | ChromaDB (SQLite) | Qdrant + Ollama |
| **Docker** | ❌ No | ✅ Required |
| **API Key** | ❌ Optional | ❌ Optional |
| **Embedding** | ONNX local (~80MB) | Ollama/OpenAI/Google |
| **MCP Tools** | 29 | 25 |
| **Graph** | Knowledge graph (entities/relationships) | Code dependency graph |
| **License** | MIT | AGPL-3.0 |
| **Runtime** | Python venv | Docker + Node.js |

## MemPalace Architecture

```
MemPalace v3.3.3
├── mcp_server.py          # 29 MCP tools (stdio)
├── mempalace/
│   ├── core.py            # Palace: wing/room/drawer hierarchy
│   ├── search.py          # ChromaDB hybrid search
│   ├── graph.py           # Knowledge graph (entity relationships)
│   ├── indexer.py         # Drawer indexing + embedding
│   └── diary.py           # Agent journaling
├── ChromaDB (SQLite)      # Local vector store
└── ONNX Runtime           # all-MiniLM-L6-v2 embeddings
```

### Palace Hierarchy

```
Palace
├── Wing (e.g., "conversations", "projects")
│   ├── Room (e.g., "hermes-sessions", "omk-dev")
│   │   ├── Drawer (atomic unit: text + metadata + embedding)
│   │   └── Drawer
│   └── Room
└── Wing
```

### Tool Categories (29 tools)

| Category | Count | Examples |
|----------|-------|----------|
| Read | 7 | status, list_wings, list_rooms, search, get_drawer |
| Write | 3 | add_drawer, delete_drawer, update_drawer |
| Graph | 7 | traverse, find_tunnels, graph_stats, create_tunnel |
| Knowledge Graph | 5 | kg_query, kg_add, kg_invalidate, kg_timeline |
| Diary | 2 | diary_write, diary_read |
| Settings | 5 | hook_settings, memories_filed_away, reconnect |

## SocratiCode Architecture

```
SocratiCode v1.7.2
├── MCP Server (stdio)
│   ├── Index Tools → indexer.ts → Qdrant + Ollama
│   ├── Query Tools → qdrant.ts → hybrid search
│   ├── Graph Tools → code-graph.ts → ast-grep analysis
│   ├── Impact Tools → symbol-graph-*.ts → call tracing
│   └── Context Tools → context-artifacts.ts → schema/spec indexing
├── Docker (managed)
│   ├── Qdrant v1.17.0 (vector DB, port 16333)
│   └── Ollama (embeddings, port 11435)
└── AST Parsing (@ast-grep/napi)
    └── 18+ language parsers
```

## When to Choose Which

### Use MemPalace when:
- You want conversation memory that persists across sessions
- You need entity tracking (people, projects, concepts)
- You want an agent diary/journal
- You don't want Docker overhead
- You prefer lightweight local storage (SQLite)

### Use SocratiCode when:
- You're working on large codebases (>100K LOC)
- You need AST-aware code analysis
- You want dependency graph visualization
- You need impact analysis for refactors
- You have Docker available

### Use Both when:
- MemPalace for session memory + SocratiCode for codebase analysis
- They serve different purposes and can coexist

## Installation Comparison

### MemPalace (No Docker)

```bash
# ~2 minutes, ~300MB total
python3 -m venv ~/.mempalace-venv
source ~/.mempalace-venv/bin/activate
pip install -e ".[dev]"
mempalace init ~/mempalace-palace --yes
```

### SocratiCode (Requires Docker)

```bash
# ~5 minutes, ~2GB total (Qdrant + Ollama images)
npm install -g socraticode
socraticode init ~/codebase
socraticode index ~/codebase
```

## Hermes Integration

Both can be configured in `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  mempalace:
    command: /home/user/.mempalace-venv/bin/mempalace-mcp
    env:
      MEMPALACE_PALACE_PATH: /home/user/.mempalace/palace
  socraticode:
    command: npx
    args: ["-y", "socraticode"]
```

MemPalace is more practical for Hermes because:
1. No Docker daemon required
2. Faster startup (no container spin-up)
3. Lower resource usage
4. Can run on systems without Docker (WSL, minimal VMs)
