---
name: aris-workflow-orchestrator
description: "Master orchestrator for all 5 ARIS workflows: Idea Discovery → Experiment Bridge → Auto Review → Paper Writing → Rebuttal/Resubmit. Adapts to research papers, Smart Hospital systems, and IOC projects."
category: research
---

# ARIS Workflow Orchestrator for Hermes

> **ARIS Port**: Original from [Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
> **Adapted for**: Hermes Agent, Smart Hospital, IOC Systems
> **Port Date**: 2026-05-10

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ARIS WORKFLOW ORCHESTRATOR                │
├─────────────────────────────────────────────────────────────┤
│  W1: Idea Discovery                                          │
│    └─ research-lit → idea-creator → novelty-check          │
│       → research-review → research-wiki ingest               │
├─────────────────────────────────────────────────────────────┤
│  W1.5: Experiment Bridge                                     │
│    └─ experiment-plan → run-experiment → monitor            │
│       → analyze-results → result-to-claim                    │
├─────────────────────────────────────────────────────────────┤
│  W2: Auto Review Loop                                        │
│    └─ auto-review-loop → kill-argument (theory papers)       │
│       → proof-checker → claim-audit → citation-audit       │
├─────────────────────────────────────────────────────────────┤
│  W3: Paper Writing                                          │
│    └─ paper-plan → paper-figure → paper-write               │
│       → paper-compile → auto-paper-improvement-loop         │
├─────────────────────────────────────────────────────────────┤
│  W4: Rebuttal                                               │
│    └─ rebuttal → (auto-experiment if needed)                │
├─────────────────────────────────────────────────────────────┤
│  W5: Resubmit                                               │
│    └─ resubmit-pipeline → kill-argument → overleaf-sync     │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Research Paper (Full Pipeline)
```
skill_view(name="aris-research/aris-workflow-orchestrator")
# Then execute via:
# /research-pipeline "federated learning for medical imaging"
```

### Smart Hospital Project
```
skill_view(name="aris-research/aris-workflow-orchestrator")
# /project-pipeline "Smart Hospital patient monitoring system"
#   — type: smart-hospital
#   — compliance: HIPAA, Thai FDA
#   — assurance: submission
```

### IOC (Integrated Operations Center)
```
skill_view(name="aris-research/aris-workflow-orchestrator")
# /project-pipeline "IOC system for smart city"
#   — type: ioc-system
#   — assurance: submission
```

## Hermes Tool Mapping

| ARIS Tool | Hermes Equivalent |
|-----------|-------------------|
| `Bash` | `terminal` |
| `Read` | `read_file` |
| `Write` | `write_file` |
| `Edit` | `patch` |
| `Grep` | `search_files` |
| `Glob` | `search_files (target='files')` |
| `WebSearch` | `web_search` |
| `WebFetch` | `browser` |
| `Agent` | `delegate_task` |
| `Skill` | `skill_view` / `skill_manage` |
| `mcp__codex__codex` | `delegate_task` (reviewer subagent) |

## Workflow Parameters

### Global Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `effort` | `balanced` | `lite` / `balanced` / `max` / `beast` |
| `assurance` | derived | `draft` / `submission` |
| `lang` | `en` | `th` / `en` / `zh` |
| `AUTO_PROCEED` | `true` | Auto-continue at gates |
| `HUMAN_CHECKPOINT` | `false` | Pause for approval |

### Research-Specific
| Parameter | Default | Description |
|-----------|---------|-------------|
| `REF_PAPER` | — | Reference paper PDF/URL |
| `BASE_REPO` | — | GitHub repo for experiments |
| `GPU` | `local` | `local` / `remote` / `vast` / `modal` |
| `TARGET_VENUE` | `ICLR` | Conference target |
| `MAX_ROUNDS` | `4` | Review loop iterations |

### Project-Specific (Smart Hospital / IOC)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `type` | `research` | `research` / `smart-hospital` / `ioc-system` |
| `compliance` | — | HIPAA, GDPR, Thai FDA, ISO 27001 |
| `stakeholders` | — | Clinical staff, IT, management |
| `tech_stack` | — | Preferred technologies |

## Cross-Model Review

ARIS uses **executor × reviewer** pattern:
- **Executor**: Hermes main model (fast execution)
- **Reviewer**: `delegate_task` to different model (rigorous critique)

This avoids single-model self-review blind spots.

```python
# Example: Run reviewer as subagent
delegate_task(
    goal="Review this paper section for logical flaws",
    context="<paper section text>",
    toolsets=["file", "search"]
)
```

## Quality Gates

All workflows pass through quality gates:
```
python3 ~/.hermes/skills/aris-research/aris-review-quality/scripts/quality_gate_runner.py     <project_dir> --type paper --assurance submission
```

## Research Wiki Integration

Persistent knowledge across sessions:
```
python3 ~/.hermes/skills/aris-research/aris-infrastructure/scripts/research_wiki.py     ingest_paper ~/.hermes/aris-wiki --arxiv-id 2406.04329
```

## Output Manifest

Each workflow produces:
- `WORKFLOW_REPORT.md` — structured summary
- `QUALITY_GATE_REPORT.json` — audit verdicts
- `RESEARCH_WIKI/` — persistent knowledge (if enabled)
