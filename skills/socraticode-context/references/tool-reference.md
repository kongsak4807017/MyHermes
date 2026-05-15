# SocratiCode MCP Tools Reference

## Index Tools
| Tool | Description |
|------|-------------|
| `codebase_index` | Start indexing a codebase in the background. Returns immediately. Call codebase_... |
| `codebase_update` | Incrementally update an existing codebase index. Only re-indexes changed files. ... |
| `codebase_remove` | Remove a project's codebase index entirely from the vector database. Safely stop... |
| `codebase_stop` | Gracefully stop an in-progress indexing operation. The current batch will finish... |
| `codebase_watch` | Start/stop watching a project directory for file changes and automatically updat... |
| `codebase_search` | Semantic search across an indexed codebase. Only use after codebase_index is com... |
| `codebase_status` | Check index status: chunk count, indexing progress (%), last completed operation... |
| `codebase_graph_build` | Build a dependency graph of the codebase using static analysis (ast-grep). Maps ... |
| `codebase_graph_query` | Query the code dependency graph for a specific file. Returns what the file impor... |
| `codebase_graph_stats` | Get statistics about the code dependency graph: total files, edges, most connect... |
| `codebase_graph_circular` | Find circular dependencies in the codebase. |
| `codebase_graph_remove` | Remove a project's persisted code graph. Waits for any in-flight graph build to ... |
| `codebase_graph_status` | Check the status of the code dependency graph: build progress (if building), nod... |
| `codebase_impact` | Impact Analysis — return the BLAST RADIUS for a file or symbol. Lists every file... |
| `codebase_flow` | Trace the EXECUTION FLOW forward from an entry point — what does this code call ... |
| `codebase_symbol` | 360° view of a symbol: definition, kind, callers, callees, confidence levels. Us... |
| `codebase_symbols` | List symbols in a file, or search by name across the project. Use to discover wh... |
| `codebase_context` | List all context artifacts defined in .socraticodecontextartifacts.json — databa... |
| `codebase_context_search` | Semantic search across context artifacts (database schemas, API specs, infra con... |
| `codebase_context_index` | Index or re-index all context artifacts defined in .socraticodecontextartifacts.... |
| `codebase_context_remove` | Remove all indexed context artifacts for a project from the vector database. Blo... |
| `codebase_health` | Check the health of all infrastructure: Docker, Qdrant container, Ollama, and em... |
| `codebase_list_projects` | List all projects that have been indexed (have collections in Qdrant). |
| `codebase_about` | Display information about SocratiCode — what it is, its tools and how to use it.... |

## Tool Categories
- **Index**: codebase_index, codebase_update, codebase_remove, codebase_stop, codebase_watch
- **Query**: codebase_search, codebase_status
- **Graph**: codebase_graph_build, codebase_graph_query, codebase_graph_stats, codebase_graph_circular, codebase_graph_visualize, codebase_graph_remove, codebase_graph_status
- **Impact**: codebase_impact, codebase_flow, codebase_symbol, codebase_symbols
- **Context**: codebase_context, codebase_context_search, codebase_context_index, codebase_context_remove
- **Manage**: codebase_health, codebase_list_projects, codebase_about
