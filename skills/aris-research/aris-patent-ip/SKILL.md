---
name: aris-patent-ip
description: "ARIS Patent Pipeline — novelty checking, claims drafting, specification writing, and prior art search"
category: research
---

# Aris Patent Ip

> **ARIS Port**: Original from [Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
> **Port Date**: 2026-05-10

## Sub-Skills

- `patent-pipeline` — see `references/patent-pipeline.md`
- `patent-novelty-check` — see `references/patent-novelty-check.md`
- `patent-review` — see `references/patent-review.md`
- `specification-writing` — see `references/specification-writing.md`
- `invention-structuring` — see `references/invention-structuring.md`
- `prior-art-search` — see `references/prior-art-search.md`
- `embodiment-description` — see `references/embodiment-description.md`
- `jurisdiction-format` — see `references/jurisdiction-format.md`

## Quick Start

```
skill_view(name="aris-patent-ip")
```

To use a specific sub-skill:
```
skill_view(name="aris-patent-ip", file_path="references/patent-pipeline.md")
```

## Shared References

All ARIS skills reference `aris-shared-references` for contracts:
```
skill_view(name="aris-research/aris-shared-references")
```
