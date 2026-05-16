---
description: Vault audit — contradictions, gaps, stale claims, orphans
category: operations
triggers: ["vault health", "audit vault", "check vault", "hermes health"]
---

# /hermes-health

Run vault health audit.

## Steps

1. Read `_HERMES.md` first
2. Scan vault for issues:
   - **Contradictions**: Same entity with different values
   - **Stale claims**: Facts older than 90 days without update
   - **Orphan notes**: Notes with no incoming links
   - **Broken links**: `[[wikilinks]]` pointing to non-existent notes
   - **Missing frontmatter**: Notes without AI-first structure
   - **Empty notes**: Notes with no content
   - **Duplicate notes**: Similar titles or content
3. For each issue:
   - Document in health report
   - Suggest fix
   - Priority: critical | warning | info
4. Write report to `wiki/reviews/Vault Health YYYY-MM-DD.md`
5. Update `log.md`
6. Report summary

## Health Report Template

```markdown
---
date: YYYY-MM-DD
type: review
tags: [health, audit]
ai-first: true
---

## For future Hermes
Vault health audit from YYYY-MM-DD. Found X issues.

## Critical
- [ ] Contradiction: ...

## Warnings
- [ ] Stale claim: ...

## Info
- [ ] Orphan note: ...

## Actions Taken
- 

## Recommended Actions
- 
```

## AI-First Rule

Every note MUST follow `references/ai-first-rules.md`.
