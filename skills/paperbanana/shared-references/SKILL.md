---
name: paperbanana-shared-references
description: "Shared reference contracts for PaperBanana skills — prompt templates, venue checklists, style guidelines, and evaluation rubrics. Referenced by paperbanana-diagram, paperbanana-plot, and paperbanana-evaluate."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [paperbanana, academic-figures, diagram-generation, shared-references]
    related_skills: [paperbanana-diagram, paperbanana-plot, paperbanana-evaluate]
    category: creative
---

# PaperBanana Shared References

This skill contains the canonical reference contracts used across all PaperBanana skills for academic figure generation.

## Reference Files

| File | Purpose |
|------|---------|
| `references/prompts/context-enricher.md` | Prompt for transforming raw methodology text into diagram-ready structured format |
| `references/prompts/caption-sharpener.md` | Prompt for sharpening vague captions into precise visual specifications |
| `references/prompts/planner.md` | Prompt for generating detailed diagram plans from structured context |
| `references/prompts/stylist.md` | Prompt for applying venue-specific aesthetic guidelines |
| `references/prompts/visualizer.md` | Prompt for converting styled specs into image generation prompts |
| `references/prompts/critic.md` | Prompt for evaluating generated diagrams with structured feedback |
| `references/prompts/plot-planner.md` | Prompt for planning statistical plots from data schemas |
| `references/prompts/evaluator.md` | Prompt for VLM-as-Judge evaluation across 4 dimensions |
| `references/venue-checklists.md` | Venue-specific requirements (NeurIPS, ICML, ACL, IEEE, arXiv) |

## Multi-Agent Pipeline Architecture

All PaperBanana skills follow this pipeline pattern:

```
Input → [Optimizer] → [Planner] → [Stylist] → [Visualizer] → [Critic] → Output
         (optional)    (required)  (required)  (required)   (iterative)
```

- **Optimizer**: Parallel context enrichment + caption sharpening
- **Planner**: Generates detailed textual description
- **Stylist**: Applies venue-specific aesthetic guidelines
- **Visualizer**: Renders description into image (via image_gen tool or code)
- **Critic**: Evaluates and provides revision feedback (iterative)

## 4-Dimension Evaluation Rubric

All evaluation skills use the same rubric:

| Dimension | Weight | Focus |
|-----------|--------|-------|
| Faithfulness | Primary | Accuracy vs source text |
| Readability | Primary | Clarity and comprehension |
| Conciseness | Secondary | Freedom from clutter |
| Aesthetics | Secondary | Visual appeal and professionalism |

### Verdict Thresholds
- **ACCEPT**: aggregate >= 8.0, no primary < 7.0
- **REVISE**: aggregate >= 5.0, no primary < 4.0
- **REJECT**: aggregate < 5.0 or any primary < 4.0

## Venue Defaults

| Venue | Key Requirements |
|-------|-----------------|
| neurips | Flat colors, no 3D, 300 DPI, sans-serif |
| icml | Math clarity, significance markers |
| acl | Sequential structure, token annotations |
| ieee | Grayscale-safe, high contrast, formal |
| arxiv | Vector PDF preferred, embedded fonts |

## Color Palettes

See `references/venue-checklists.md` for full color tables including hex codes.

## Cross-Skill Integration

- `paperbanana-diagram` uses: context-enricher, caption-sharpener, planner, stylist, visualizer, critic
- `paperbanana-plot` uses: plot-planner, stylist (colors), visualizer, critic
- `paperbanana-evaluate` uses: evaluator prompt, 4-dimension rubric
