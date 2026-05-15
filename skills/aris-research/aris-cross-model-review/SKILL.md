---
name: aris-cross-model-review
description: "Cross-model adversarial review system for Hermes. Routes executor work to main model and reviewer work to delegate_task subagents with different models. Prevents self-play local minima."
category: research
---

# ARIS Cross-Model Review for Hermes

> **ARIS Port**: Cross-model adversarial collaboration pattern
> **Hermes Adaptation**: Uses delegate_task with model overrides

## Why Cross-Model Review?

Single-model self-review creates **local minima** — the same model reviewing its own patterns creates blind spots. Think of it like:

- **Self-play** = stochastic bandits (predictable reward noise)
- **Cross-model** = adversarial bandits (reviewer actively probes weaknesses)

Two is the minimum needed to break blind spots. Adding more reviewers increases cost with diminishing returns.

## Hermes Implementation

### Basic Pattern
```python
# Executor: Main model (fast, fluid)
# Reviewer: Subagent with different model (deliberate, rigorous)

delegate_task(
    goal="Review this paper section for logical flaws and missing citations",
    context="PAPER SECTION: (content here)\n\nREVIEW CRITERIA: Every claim must have evidence; No hallucinated citations; Check for circular reasoning; Identify unstated assumptions",
    toolsets=["file", "search", "web"],
    # Optional: specify different model for reviewer
    # model={"provider": "openrouter", "model": "anthropic/claude-sonnet-4"}
)
```

### Model Combinations

| Executor | Reviewer | Use Case |
|----------|----------|----------|
| kimi-for-coding | claude-sonnet-4 | Speed x rigor |
| claude-sonnet-4 | kimi-for-coding | Different perspective |
| local-ollama | paid-model | Cost optimization |
| main-model | delegate_task (default) | Standard review |

### Reviewer Independence Rules

1. **No shared context** — reviewer starts fresh, reads only what's provided
2. **No tool access to executor files** — reviewer gets copies, not paths
3. **Verdict-only output** — reviewer emits verdicts, not fixes
4. **Adversarial stance** — reviewer assumes the work is wrong until proven otherwise

## Review Routing Script

See `scripts/review_router.py` — prepares review packages for delegate_task.

## Integration with Quality Gates

```python
# Step 1: Executor produces content (main model)
# Step 2: Route to reviewer via review_router.py
# Step 3: Parse verdicts
# Step 4: Fix and re-review if needed
```

## Session Recovery

If review session is interrupted:
1. Load REVIEW_STATE.json from project directory
2. Resume from last completed review round
3. Re-run pending reviews

## Example: Full Paper Review

```
# Phase 1: Executor writes paper
# Phase 2: Reviewer audits via review_router
# Phase 3: Quality gate verification
# Phase 4: Fix loop (if needed)
```
