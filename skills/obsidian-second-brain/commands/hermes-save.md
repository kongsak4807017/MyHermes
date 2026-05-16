---
description: Save everything worth keeping from this conversation to the vault
category: operations
triggers: ["save this", "save the conversation", "save to vault", "hermes save"]
---

# /hermes-save

Save everything from the current conversation to the vault.

## Steps

1. Read `_HERMES.md` first if it exists in the vault root
2. Scan the entire conversation and identify vault-worthy items:
   - Decisions made
   - Tasks created or completed
   - People mentioned
   - Projects started or updated
   - Ideas generated
   - Learnings
   - Content-worthy items (hooks, data points, research findings)
3. Group items by type
4. For each group, search vault before creating — avoid duplicates
5. Create or update notes following AI-first rules
6. Update today's daily note with links
7. Report what was saved and where

## AI-First Rule

Every note MUST follow `references/ai-first-rules.md`:
- `## For future Hermes` preamble
- Rich frontmatter with `type`, `date`, `tags`, `ai-first: true`
- Recency markers per external claim
- Mandatory `[[wikilinks]]`
- Sources preserved verbatim
