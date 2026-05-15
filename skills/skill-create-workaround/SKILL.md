---
name: skill-create-workaround
description: Workaround for skill_create failures — when skill_manage(action='create') rejects YAML frontmatter, use write_file to create SKILL.md directly at the correct path
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skill, create, workaround, skill_manage, write_file]
---

# Skill Create Workaround

When `skill_manage(action='create')` fails with "SKILL.md must start with YAML frontmatter (---)" despite content starting with `---`, use this workaround:

## The Problem

`skill_manage` validates YAML frontmatter by parsing the first `---` block. If the content string contains characters or encoding that confuse the parser (e.g., markdown lists with `-` inside the frontmatter or special unicode), it may reject valid frontmatter.

## The Solution

Write the SKILL.md directly:

```python
write_file(
    content="""---
name: my-skill
description: Short description
version: 1.0.0
author: Your Name
license: MIT
metadata:
  hermes:
    tags: [tag1, tag2]
---
# Skill Title

Content here...
""",
    path="~/.hermes/skills/my-skill/SKILL.md"
)
```

The directory is created automatically. The skill will be detected by Hermes on the next session or after a `/reset`.

## Important Notes

- Path MUST be `~/.hermes/skills/<skill-name>/SKILL.md` (or with category subdirectory)
- Frontmatter must end with `---` followed by content
- If the skill already exists and you need to update it, use `skill_manage(action='patch')` instead
