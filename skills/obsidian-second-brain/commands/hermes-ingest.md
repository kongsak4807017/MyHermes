---
description: Ingest a URL, PDF, audio file, or screenshot — the vault rewrites itself
category: operations
triggers: ["ingest this", "add to vault", "process source", "hermes ingest"]
---

# /hermes-ingest

Ingest external source into vault. The vault rewrites itself.

## Steps

1. Read `_HERMES.md` first
2. Determine source type (URL, PDF, audio, image)
3. Save original to `raw/` (immutable)
4. Extract content:
   - URL: Fetch and parse
   - PDF: Extract text
   - Audio: Transcribe with Whisper
   - Image: OCR + description
5. Identify entities, concepts, claims
6. For each entity/concept:
   - Search vault for existing note
   - If exists: REWRITE with new context
   - If new: Create note
7. Check for contradictions with existing notes
8. Create synthesis pages if patterns emerge
9. Update `index.md`, `log.md`, daily note
10. Report: what was created, updated, reconciled

## One In, Vault Rewrites

One source can touch 5-15 vault pages:
- Entity pages updated
- Concept pages rewritten
- Synthesis pages created
- Contradictions resolved
- Daily note updated

## AI-First Rule

Every note MUST follow `references/ai-first-rules.md`.
