---
name: aris-review-quality
description: "ARIS Workflow 2: Auto Review + Quality Gates — adversarial review loops, proof checking, claim auditing, citation auditing"
category: research
---

# Aris Review Quality

> **ARIS Port**: Original from [Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
> **Port Date**: 2026-05-10

## Sub-Skills

- `auto-review-loop` — see `references/auto-review-loop.md`
- `auto-review-loop-llm` — see `references/auto-review-loop-llm.md`
- `auto-review-loop-minimax` — see `references/auto-review-loop-minimax.md`
- `kill-argument` — see `references/kill-argument.md`
- `proof-checker` — see `references/proof-checker.md`
- `paper-claim-audit` — see `references/paper-claim-audit.md`
- `citation-audit` — see `references/citation-audit.md`

## Quick Start

```
skill_view(name="aris-review-quality")
```

To use a specific sub-skill:
```
skill_view(name="aris-review-quality", file_path="references/auto-review-loop.md")
```

## Shared References

All ARIS skills reference `aris-shared-references` for contracts:
```
skill_view(name="aris-research/aris-shared-references")
```
