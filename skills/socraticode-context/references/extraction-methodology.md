# Static Skill Extraction Methodology

Reusable pattern for converting any MCP-based tool (SocratiCode, MemPalace, etc.) into a Hermes static skill without runtime services.

## When to Use This Pattern

- The tool requires Docker/Node.js/Python service that you don't want running constantly
- You want the *concepts* and *tool definitions* available instantly in Hermes
- The tool's value is 80% knowledge / 20% live computation
- You want portability (no runtime dependencies)

## Steps

### 1. Clone and Inspect

```bash
cd /tmp
git clone --depth 1 <repo-url>
cd <repo>
```

Key files to read:
- `README.md` — purpose, benchmarks, features
- `package.json` / `pyproject.toml` — dependencies, version
- Main entry point (`src/index.ts`, `mcp_server.py`) — tool definitions
- Core service files — architecture understanding

### 2. Extract Tool Catalog

From the MCP server entry point, extract all tool names + descriptions:

```python
import re

# For TypeScript/Zod MCP servers (SocratiCode style)
tools = re.findall(r'server\.tool\(\s*"([^"]+)"\s*,\s*"([^"]+)"', src)

# For Python dict-based MCP servers (MemPalace style)
tools = re.findall(r'"(mempalace_[a-z_]+)"\s*:\s*\{[^}]*"description"\s*:\s*"([^"]+)"', src)
```

### 3. Extract Architecture

Read imports and module structure to build architecture diagram:

```bash
find src/ -type f | sort  # or find mempalace/ -type f
```

Map:
- Entry point → tool handlers → core services → external dependencies
- Data flow: input → processing → storage → output

### 4. Generate Static Files

Create skill structure:

```
~/.hermes/skills/<tool-name>-context/
├── SKILL.md                    # Architecture + workflow + concepts
└── references/
    ├── tool-reference.md       # All MCP tools with descriptions
    ├── architecture.md         # Module dependency graph
    ├── comparison.md           # vs other tools (optional)
    └── extraction-methodology.md  # This file (reusable)
```

### 5. Install to Hermes

```bash
mkdir -p ~/.hermes/skills/<tool-name>-context/references
cp SKILL.md ~/.hermes/skills/<tool-name>-context/
cp references/*.md ~/.hermes/skills/<tool-name>-context/references/
```

## Size Guidelines

- SKILL.md: ~2-3 KB (concepts, when-to-use, architecture)
- references/tool-reference.md: ~3-5 KB (tool catalog)
- references/architecture.md: ~1-2 KB (module map)
- **Total: ~8-15 KB** vs potentially GB of runtime

## Verification

Test that Hermes can load it:

```
skill_view("<tool-name>-context")
```

## Examples Created with This Pattern

| Tool | Skill Name | Size |
|------|-----------|------|
| SocratiCode | `socraticode-context` | 8.7 KB |
| MemPalace | (can be created same way) | ~10 KB est. |

## Limitations of Static Skills

- ❌ No live semantic search (concepts only)
- ❌ No live dependency graph computation
- ❌ No real-time indexing
- ✅ Instant availability
- ✅ Zero runtime cost
- ✅ Portable across environments
