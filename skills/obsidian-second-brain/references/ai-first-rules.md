# AI-First Note Rules

The vault is designed for **future-Hermes** to read and reason over, not for human review. The owner rarely opens notes directly — they call Hermes to retrieve, synthesize, and connect dots across years of accumulated knowledge. **Every command that writes to the vault must produce notes that follow these rules.**

---

## The 7 Rules

### 1. Self-contained context
Each note must explain itself. Future-Hermes may pull this single note via `/hermes-find` or vault scan with no surrounding context. Don't rely on backlinks alone for meaning. State the *what*, the *why*, and the *when* inside the note itself.

### 2. "For future Hermes" preamble
Every note begins with a 2–3 sentence summary in plain English under a `## For future Hermes` header (immediately after the frontmatter). Future-Hermes reads this to decide relevance in 10 seconds before parsing the rest.

```markdown
## For future Hermes
This note is a [type] about [topic] saved on [date]. It [main purpose].
[Optional caveat about staleness, confidence, or scope.]
```

### 3. Rich, consistent frontmatter
Filterable metadata. Different note types have different schemas but every note has machine-readable frontmatter.

**Universal fields (every note):**
```yaml
---
date: YYYY-MM-DD              # creation or update date
type: <note-type>             # see Type Schemas below
tags: [...]                   # always include the type as a tag
ai-first: true                # explicit flag
---
```

### 4. Recency markers per claim
When stating external facts, attach the date inline:

```markdown
- Mem0 raised $24M Series A (as of 2026-04, mem0.ai/blog/series-a)
- Anthropic released native memory tool (as of 2026-02, anthropic.com/news/memory)
```

### 5. Sources preserved verbatim
Every external claim has its source URL inline. Don't paraphrase a citation — keep the actual URL so the claim can be re-verified or refreshed years later.

### 6. Cross-links are mandatory
Every person, project, idea, decision, or concept referenced uses `[[wikilinks]]` so the graph is traversable:

```markdown
Sarah at [[People/Sarah Chen]] decided to ship the [[Projects/Dashboard Refactor]] by Friday.
```

If a linked note doesn't exist, create a stub.

### 7. Confidence levels
Where applicable, mark claims with confidence:
- `stated` — directly quoted or claimed by a source
- `high` — multiple sources agree
- `medium` — single source, plausible
- `speculation` — your inference

---

## Type Schemas

### `type: daily`
```yaml
---
date: YYYY-MM-DD
type: daily
tags: [daily]
mood: ""
energy: ""
ai-first: true
---
```

### `type: project`
```yaml
---
date: YYYY-MM-DD
updated: YYYY-MM-DD
type: project
status: active                # active | planning | completed | archived | on-hold
tags: [project, ...]
related-people: ["[[People/...]]", ...]
related-projects: ["[[Projects/...]]", ...]
ai-first: true
---
```

### `type: person`
```yaml
---
date: YYYY-MM-DD
updated: YYYY-MM-DD
type: person
tags: [person, ...]
role: ""
company: ""
relationship: weak | medium | strong
last-interaction: YYYY-MM-DD
related-projects: ["[[Projects/...]]", ...]
ai-first: true
---
```

### `type: idea`
```yaml
---
date: YYYY-MM-DD
type: idea
tags: [idea, ...]
status: captured              # captured | exploring | graduated | shelved
related-projects: ["[[Projects/...]]", ...]
ai-first: true
---
```

### `type: task`
```yaml
---
date: YYYY-MM-DD
type: task
status: in-progress           # in-progress | done | waiting | cancelled
priority: 🔴 | 🟡 | 🟢
due: YYYY-MM-DD
tags: [task, ...]
related-projects: ["[[Projects/...]]", ...]
related-people: ["[[People/...]]", ...]
ai-first: true
---
```

### `type: decision`
```yaml
---
date: YYYY-MM-DD
type: decision
tags: [decision, ...]
related-projects: ["[[Projects/...]]", ...]
confidence: stated | high | medium | speculation
sources: [...]
ai-first: true
---
```

### `type: research`
```yaml
---
date: YYYY-MM-DD
type: research
tags: [research, ...]
topic: ""
sources: [...]
ai-first: true
---
```
