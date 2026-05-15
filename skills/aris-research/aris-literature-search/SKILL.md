---
name: aris-literature-search
description: "ARIS Literature Search — multi-source paper discovery across arXiv, Semantic Scholar, DeepXiv, Exa, OpenAlex, and Gemini"
category: research
---

# Aris Literature Search

> **ARIS Port**: Original from [Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
> **Port Date**: 2026-05-10

## Sub-Skills

- `arxiv` — see `references/arxiv.md`
- `alphaxiv` — see `references/alphaxiv.md`
- `deepxiv` — see `references/deepxiv.md`
- `semantic-scholar` — see `references/semantic-scholar.md`
- `exa-search` — see `references/exa-search.md`
- `openalex` — see `references/openalex.md`
- `gemini-search` — see `references/gemini-search.md`

## Quick Start

```
skill_view(name="aris-literature-search")
```

To use a specific sub-skill:
```
skill_view(name="aris-literature-search", file_path="references/arxiv.md")
```

## Shared References

All ARIS skills reference `aris-shared-references` for contracts:
```
skill_view(name="aris-research/aris-shared-references")
```
