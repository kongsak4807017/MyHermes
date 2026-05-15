---
name: aris-experiments
description: "ARIS Workflow 1.5: Experiment Bridge — experiment planning, execution, monitoring, GPU management, and result analysis"
category: research
---

# Aris Experiments

> **ARIS Port**: Original from [Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
> **Port Date**: 2026-05-10

## Sub-Skills

- `experiment-bridge` — see `references/experiment-bridge.md`
- `experiment-plan` — see `references/experiment-plan.md`
- `run-experiment` — see `references/run-experiment.md`
- `monitor-experiment` — see `references/monitor-experiment.md`
- `analyze-results` — see `references/analyze-results.md`
- `experiment-audit` — see `references/experiment-audit.md`
- `experiment-queue` — see `references/experiment-queue.md`
- `ablation-planner` — see `references/ablation-planner.md`
- `training-check` — see `references/training-check.md`
- `result-to-claim` — see `references/result-to-claim.md`
- `vast-gpu` — see `references/vast-gpu.md`
- `serverless-modal` — see `references/serverless-modal.md`

## Quick Start

```
skill_view(name="aris-experiments")
```

To use a specific sub-skill:
```
skill_view(name="aris-experiments", file_path="references/experiment-bridge.md")
```

## Shared References

All ARIS skills reference `aris-shared-references` for contracts:
```
skill_view(name="aris-research/aris-shared-references")
```
