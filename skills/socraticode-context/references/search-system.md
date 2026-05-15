# SocratiCode Search System

## Hybrid Search Architecture
1. **Dense vector search** (semantic) — HNSW index in Qdrant
2. **Sparse BM25 search** (keyword) — inverted index in Qdrant
3. **RRF Fusion** — Reciprocal Rank Fusion รวมผลทั้งสอง

## Embedding Providers
| Provider | Model | Dimensions | Speed |
|----------|-------|------------|-------|
| Ollama (local) | nomic-embed-text | 768 | Medium |
| OpenAI | text-embedding-3-small | 1536 | Fastest |
| Google | gemini-embedding-001 | 3072 | Free tier |

## Query Parameters
- `limit`: 1-50 results (default 10)
- `minScore`: 0-1 threshold (default 0.10)
- `fileFilter`: filter by relative path
- `languageFilter`: filter by language
- `includeLinked`: cross-project search

## Search Workflow
```
query → parse → dense_vector + sparse_vector → Qdrant → RRF fuse → rank → return chunks
```

## Result Format
Each result contains:
- file path (relative)
- line range (start-end)
- code content (chunk)
- RRF score (0-1)
- language
