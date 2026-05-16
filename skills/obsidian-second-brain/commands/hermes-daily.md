---
description: Create or update today's daily note
category: operations
triggers: ["daily note", "today's note", "start my day", "hermes daily"]
---

# /hermes-daily

Create or update today's daily note.

## Steps

1. Read `_HERMES.md` first
2. Check if today's note exists: `wiki/daily/YYYY-MM-DD.md`
3. If not exists, create from template
4. Populate with:
   - Calendar events (if available)
   - Overdue tasks from boards
   - Active project priorities
   - Links to yesterday's note
   - Open threads from last session
5. If exists, update with:
   - New tasks added today
   - Decisions made
   - People interacted with
   - Links to notes created today
6. Update `log.md`

## Daily Note Template

```markdown
---
date: YYYY-MM-DD
type: daily
tags: [daily]
mood: ""
energy: ""
ai-first: true
---

## For future Hermes
Daily note for YYYY-MM-DD. Contains tasks, events, decisions, and links.

## Morning
- [ ] 

## Tasks
- [ ] 

## Decisions
- 

## People
- [[People/]]

## Projects
- [[Projects/]]

## Notes Created
- [[ ]]

## Evening
- 

## Links
- Yesterday: [[wiki/daily/YYYY-MM-DD]]
- Tomorrow: [[wiki/daily/YYYY-MM-DD]]
```

## AI-First Rule

Every note MUST follow `references/ai-first-rules.md`.
