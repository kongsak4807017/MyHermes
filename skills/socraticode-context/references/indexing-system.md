# SocratiCode Indexing System

## Architecture
- **Phase 1**: File scanning (glob + ignore rules)
- **Phase 2**: AST-aware chunking (function/class boundaries via ast-grep)
- **Phase 3**: Embedding generation (Ollama/OpenAI/Google)
- **Phase 4**: Vector upsert to Qdrant (hybrid dense + BM25)
- **Phase 5**: Symbol graph building (import analysis)
- **Phase 6**: Incremental watcher setup

## Key Constants
- `FILE_SCAN_BATCH` = 50
- `INCREMENTAL_SYMBOL_THRESHOLD` = 50

## Chunking Strategy
- AST-aware: split at function/class boundaries
- Fallback: line-based chunking for unsupported languages
- Overlap: N/A chars between chunks
- Max chunk: N/A bytes

## Resumable Indexing
- Batched processing: N/A files per batch
- Checkpoints after each batch (hashes stored in Qdrant)
- Crash recovery: resume from last checkpoint
- Incremental updates: only changed files (content hash comparison)

## File Watcher
- @parcel/watcher for native file system events
- Debounced: 2 seconds
- Auto-incremental update on change
- Cross-process coordination (proper-lockfile)
