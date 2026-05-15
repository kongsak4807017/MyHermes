# MCP Integration Patterns for OMK CLI

## MemPalace MCP Server Setup

### Installation Pattern (Python venv)

```bash
# 1. Create isolated venv
python3 -m venv ~/.mempalace-venv
source ~/.mempalace-venv/bin/activate

# 2. Install from source
pip install -e ".[dev]"

# 3. Verify
mempalace --version  # MemPalace 3.3.3
```

### Hermes Config Integration

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  mempalace:
    command: /home/user/.mempalace-venv/bin/mempalace-mcp
    env:
      MEMPALACE_PALACE_PATH: /home/user/.mempalace/palace
```

### Palace Initialization

```bash
# Create palace directory
mkdir -p ~/mempalace-palace

# Initialize (auto-detect rooms, skip LLM if unavailable)
mempalace init ~/mempalace-palace --yes

# Mine content
mempalace mine ~/mempalace-palace

# Check status
mempalace status
```

### Embedding Model Download

First search triggers automatic download:
```bash
mempalace search "test"
# Downloads all-MiniLM-L6-v2 (~80 MB) to ~/.cache/chroma/
```

## SocratiCode Static Export Pattern

When a tool requires Docker/Node.js runtime (like SocratiCode), export static context instead:

```bash
# 1. Clone and analyze
git clone --depth 1 https://github.com/giancarloerra/socraticode.git /tmp/socraticode

# 2. Extract architecture from source
# - Read package.json for dependencies
# - Read src/index.ts for MCP tool definitions
# - Read src/services/*.ts for core logic

# 3. Create Hermes skill with static references
mkdir -p ~/.hermes/skills/socraticode-context/references

# 4. Generate SKILL.md + reference files
# - dependency-graph.md (from graph-imports.ts, graph-analysis.ts)
# - indexing-system.md (from indexer.ts)
# - search-system.md (from query-tools.ts, embeddings.ts)
# - tool-reference.md (all 25 MCP tools from index.ts)
```

### Static Export Benefits

| Aspect | MCP Server | Static Skill |
|--------|-----------|--------------|
| Runtime | Docker + Node.js | None |
| Latency | ~5 min setup | Instant |
| Portability | Tied to Docker | File-based |
| Semantic Search | ✅ Real | ❌ Concept only |
| Deep Analysis | ✅ Live graph | ⚠️ Documented |

## Config.yaml Editing Pitfalls

### YAML Structure Corruption

When adding `mcp_servers` section, common errors:

1. **Duplicate sections** — `terminal:` appears twice
2. **Wrong indentation** — `mcp_servers` nested under `terminal`
3. **Missing fields** — `docker_image`, `modal_image` lost during patch

### Safe Editing Pattern

```bash
# 1. Backup
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak

# 2. Validate structure
python3 -c "import yaml; yaml.safe_load(open('~/.hermes/config.yaml'))"

# 3. Add section at ROOT level (not nested)
# mcp_servers:
#   name:
#     command: ...
#     env: ...

# 4. Verify no duplicates
grep -n "^mcp_servers:" ~/.hermes/config.yaml
grep -n "^terminal:" ~/.hermes/config.yaml
```

## MemPalace vs SocratiCode Comparison

| | MemPalace | SocratiCode |
|---|-----------|-------------|
| **Focus** | Personal memory | Codebase intelligence |
| **Data** | Conversations, entities | Source code, dependencies |
| **Storage** | ChromaDB (SQLite) | Qdrant + Ollama |
| **Docker** | ❌ No | ✅ Required |
| **API Key** | ❌ Optional | ❌ Optional |
| **Embedding** | ONNX local (~300 MB) | Ollama/OpenAI/Google |
| **MCP Tools** | 29 | 25 |
| **Graph** | Knowledge graph (entities) | Code dependency graph |
| **License** | MIT | AGPL-3.0 |

## MemPalace MCP Tool Categories

| Category | Tools | Use Case |
|----------|-------|----------|
| **Read** | status, list_wings, list_rooms, get_taxonomy, search, check_duplicate, get_drawer, list_drawers | Query palace contents |
| **Write** | add_drawer, delete_drawer, update_drawer | Modify palace data |
| **Graph** | traverse, find_tunnels, graph_stats, create_tunnel, list_tunnels, delete_tunnel, follow_tunnels | Cross-wing navigation |
| **Knowledge Graph** | kg_query, kg_add, kg_invalidate, kg_timeline, kg_stats | Entity relationships |
| **Diary** | diary_write, diary_read | Agent journaling |
| **Settings** | hook_settings, memories_filed_away, reconnect, get_aaak_spec | Configuration |

## Hermes Native MCP Client

Hermes auto-discovers MCP tools from `mcp_servers` config:

```yaml
mcp_servers:
  mempalace:
    command: /path/to/mempalace-mcp
  socraticode:
    command: npx
    args: ["-y", "socraticode"]
```

Tools appear in Hermes tool registry automatically after restart.
