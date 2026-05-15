---
name: aris-research-core
description: "ARIS Workflow 1: Idea Discovery — research pipeline, literature search, idea creation, novelty checking, and review"
category: research
---

# Aris Research Core

> **ARIS Port**: Original from [Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
> **Port Date**: 2026-05-10

## Sub-Skills

- `research-refine` — see `references/research-refine.md`
- `research-refine-pipeline` — see `references/research-refine-pipeline.md`
- `idea-discovery-robot` — see `references/idea-discovery-robot.md`

## Quick Start

```
skill_view(name="aris-research-core")
```

To use a specific sub-skill:
```
skill_view(name="aris-research-core", file_path="references/research-refine.md")
```

## Shared References

All ARIS skills reference `aris-shared-references` for contracts:
```
skill_view(name="aris-research/aris-shared-references")
```
