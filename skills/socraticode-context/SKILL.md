---
name: socraticode-context
description: Deep codebase intelligence from SocratiCode — dependency graphs, hybrid search, impact analysis, and symbol-level tracing. Static context for Hermes Agent without Docker/Node.js overhead.
category: software-development
tags: [codebase, search, graph, dependencies, indexing]
---

# SocratiCode Context Skill

## When to Use
- Working on large codebases (>100K LOC) where grep is insufficient
- Need to understand cross-file dependencies and blast radius
- Want semantic search (conceptual queries, not just exact matches)
- Planning refactors and need impact analysis
- Debugging circular dependencies or architectural issues

## Architecture Overview

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

## Key Concepts

### 1. Hybrid Search
- **Semantic**: dense vector embeddings (concept matching)
- **Keyword**: BM25 sparse vectors (exact identifier matching)
- **Fusion**: RRF (Reciprocal Rank Fusion) combines both

### 2. Dependency Graph
- **File-level**: import/require relationships
- **Symbol-level**: function/class call graphs
- **Analysis**: circular deps, orphans, entry points, blast radius

### 3. AST-Aware Chunking
- Split at function/class boundaries (not arbitrary lines)
- Higher quality embeddings
- Better search precision

## Workflow Patterns

### Explore Codebase
1. `codebase_search` — broad conceptual query
2. `codebase_graph_query` — see file dependencies
3. `codebase_symbol` — drill into specific function

### Before Refactoring
1. `codebase_impact` — blast radius of target
2. `codebase_flow` — trace execution paths
3. `codebase_graph_circular` — check for cycles

### Maintain Index
1. `codebase_index` — initial full index
2. `codebase_watch` — auto-update on changes
3. `codebase_status` — check health

## References
- `references/dependency-graph.md` — graph system details
- `references/indexing-system.md` — indexing architecture
- `references/search-system.md` — search internals
- `references/tool-reference.md` — all 25 MCP tools
- `references/extraction-methodology.md` — reusable pattern for converting any MCP tool into a static Hermes skill
- `references/mempalace-comparison.md` — MemPalace vs SocratiCode comparison (extracted from session analysis)

## Source
- Repository: https://github.com/giancarloerra/socraticode
- License: AGPL-3.0
- Version: 1.7.2
