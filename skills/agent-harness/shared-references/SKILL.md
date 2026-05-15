---
name: agent-harness-shared-references
description: Shared reference contracts for agent-harness skills — observability patterns, guardrails templates, evaluation rubrics, sandbox configs, and protocol specifications. Referenced by all agent-harness sub-skills.
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Agent Harness, Observability, Guardrails, Evaluation, Sandbox, Protocols, Shared References]
---

# Agent Harness Shared References

Central contract for all agent-harness skills. Contains reusable patterns, configs, and templates.

## Directory Structure

```
shared-references/
├── SKILL.md                          # This file
├── references/
│   ├── observability-patterns.md     # Tracing, metrics, logging patterns
│   ├── guardrails-templates.md       # Validation templates
│   ├── evaluation-rubrics.md         # Scoring rubrics
│   ├── sandbox-configs.md            # Sandbox configurations
│   └── protocol-specs.md             # MCP, ACP, AGENTS.md specs
└── templates/
    ├── trace-template.json           # OpenTelemetry trace template
    ├── guardrail-config.yaml         # Guardrail configuration template
    └── eval-report-template.md       # Evaluation report template
```

## Usage

Other skills reference these via relative path:
```
See [observability-patterns](references/observability-patterns.md) for tracing setup.
```

## Key Concepts

### Agent Harness Architecture

```
┌─────────────────────────────────────────┐
│           Agent Application              │
├─────────────────────────────────────────┤
│  Orchestration  │  Context/State        │
│  - LangGraph    │  - Memory             │
│  - AutoGen      │  - Session            │
│  - Symphony     │  - Working State      │
├─────────────────────────────────────────┤
│  Tools/Protocols │  Execution            │
│  - MCP          │  - Sandbox            │
│  - ACP          │  - Container          │
│  - AGENTS.md    │  - VM                 │
├─────────────────────────────────────────┤
│  Observability  │  Guardrails           │
│  - Tracing      │  - Input Validation   │
│  - Metrics      │  - Output Filtering   │
│  - Logging      │  - Security           │
├─────────────────────────────────────────┤
│           Evaluation Layer              │
│  - Benchmarks   │  - Regression Tests   │
└─────────────────────────────────────────┘
```

### Observability Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Tracing | Langfuse, Phoenix | Request/response traces |
| Metrics | Helicone, Opik | Token usage, latency, cost |
| Logging | AgentOps, MLflow | Agent action logs |
| Evaluation | Promptfoo, DeepEval | Quality assessment |

### Guardrails Categories

| Category | Examples |
|----------|----------|
| Input | Prompt injection, PII detection, toxicity |
| Output | Hallucination check, fact verification |
| Security | Rate limiting, permission boundaries |
| Compliance | Data retention, audit trails |
