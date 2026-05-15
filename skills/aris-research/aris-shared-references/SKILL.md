---
name: aris-shared-references
description: "ARIS shared reference contracts — assurance, citation discipline, effort, experiment integrity, integration, output protocols, reviewer independence, venue checklists, writing principles, wiki helper resolution. All ARIS skills reference these contracts."
category: research
---

# ARIS Shared References

This skill contains the canonical reference contracts used across all ARIS research workflows.

## Reference Files

| File | Purpose |
|------|---------|
| `references/assurance-contract.md` | 6-state verdict system for audits (PASS / FAIL / FIX / KEEP / REPLACE / REMOVE) |
| `references/citation-discipline.md` | Hallucination prevention for citations |
| `references/effort-contract.md` | Effort axis (lite/balanced/max/beast) vs assurance axis mapping |
| `references/experiment-integrity.md` | Protocol for experiment reproducibility |
| `references/integration-contract.md` | How skills integrate with each other |
| `references/output-language.md` | Output language protocol (Thai/English/Chinese) |
| `references/output-manifest.md` | Manifest format for deliverables |
| `references/output-versioning.md` | Versioning protocol for outputs |
| `references/review-tracing.md` | Review tracing for accountability |
| `references/reviewer-independence.md` | Cross-model reviewer independence rules |
| `references/reviewer-routing.md` | Model routing for executor vs reviewer |
| `references/venue-checklists.md` | Venue-specific checklists (ICLR, NeurIPS, ICML, IEEE, etc.) |
| `references/wiki-helper-resolution.md` | Research wiki helper resolution chain |
| `references/writing-principles.md` | Orchestra-adapted writing principles |

## 6-State Verdict System

All ARIS audits emit machine-readable verdicts:

| Verdict | Meaning | Action |
|---------|---------|--------|
| `PASS` | No issues found | None |
| `FAIL` | Critical issue, blocks submission | Must fix |
| `FIX` | Issue found, fix proposed | Apply fix |
| `KEEP` | Content acceptable as-is | None |
| `REPLACE` | Content should be replaced | Rewrite |
| `REMOVE` | Content should be removed | Delete |
| `USER_DECISION` | Needs human judgment | Pause for approval |

## Assurance Levels

| Level | Behavior | Use Case |
|-------|----------|----------|
| `draft` | Audits run if content matches. Silent skip allowed. | Rapid iteration |
| `submission` | All mandatory audits must emit verdict. Silent skip forbidden. | Conference submission |

Default mapping: `lite/balanced` → `draft`; `max/beast` → `submission`.

## Cross-Model Review Architecture

ARIS uses **executor × reviewer** pattern (not self-play):

- **Executor**: Fast, fluid execution (Claude/Hermes main model)
- **Reviewer**: Deliberate, rigorous critique (via `delegate_task` to different model)

This avoids local minima from single-model self-review.
