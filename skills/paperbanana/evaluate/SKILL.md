---
name: paperbanana-evaluate
description: "Evaluate generated academic figures using VLM-as-Judge across 4 dimensions (faithfulness, readability, conciseness, aesthetics). Supports comparative evaluation against human references."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [paperbanana, evaluation, vlm-as-judge, academic-figures, quality-assessment]
    related_skills: [paperbanana-diagram, paperbanana-plot, paperbanana-shared-references]
    category: creative
---

# PaperBanana Evaluate

Evaluate generated academic figures using VLM-as-Judge across four dimensions. Supports both standalone evaluation and comparative evaluation against human references.

## When to Use

- User wants to evaluate quality of a generated diagram
- User wants to compare AI-generated figure against human reference
- User needs structured feedback for iterative improvement
- User wants to ensure figure meets publication standards

## When NOT to Use

- User wants to generate a figure → use `paperbanana-diagram` or `paperbanana-plot`
- User wants general image analysis → use `vision` toolset
- User wants aesthetic scoring only → use `comfyui` or image generation tools

## Prerequisites

- Python 3.10+ with `pip` available
- API key for at least one VLM provider: OpenAI, Google Gemini, or OpenRouter
- Generated image file (PNG, JPEG, or WebP)
- Optional: human reference image for comparative mode

## Quick Start

### Standalone Evaluation

```bash
python3 ~/.hermes/skills/paperbanana/evaluate/scripts/evaluate_figure.py \
  --generated diagram.png \
  --context method.txt \
  --caption "Overview of our framework"
```

### Comparative Evaluation

```bash
python3 ~/.hermes/skills/paperbanana/evaluate/scripts/evaluate_figure.py \
  --generated diagram.png \
  --reference human_diagram.png \
  --context method.txt \
  --caption "Overview of our framework"
```

### Python API

```python
import asyncio
import sys
sys.path.insert(0, "~/.hermes/skills/paperbanana/evaluate/scripts")
from evaluate_figure import FigureEvaluator

evaluator = FigureEvaluator(vlm_provider="openai")

result = asyncio.run(evaluator.evaluate(
    generated_path="diagram.png",
    reference_path="human_diagram.png",  # optional
    context="Our framework consists of...",
    caption="Overview of our method."
))

print(f"Aggregate Score: {result['aggregate_score']}")
print(f"Verdict: {result['verdict']}")
```

## 4-Dimension Evaluation Rubric

| Dimension | Weight | Focus | Thresholds |
|-----------|--------|-------|------------|
| Faithfulness | Primary | Accuracy vs source text | ≥7 required for ACCEPT |
| Readability | Primary | Clarity and comprehension | ≥7 required for ACCEPT |
| Conciseness | Secondary | Freedom from clutter | ≥5 required for ACCEPT |
| Aesthetics | Secondary | Visual appeal | ≥5 required for ACCEPT |

### Verdict Thresholds
- **ACCEPT**: aggregate ≥ 8.0, no primary < 7.0
- **REVISE**: aggregate ≥ 5.0, no primary < 4.0
- **REJECT**: aggregate < 5.0 or any primary < 4.0

## CLI Reference

| Flag | Short | Description |
|------|-------|-------------|
| `--generated` | `-g` | Path to generated image (required) |
| `--reference` | `-r` | Path to human reference image (optional) |
| `--context` | | Path to source context text file or PDF (required) |
| `--caption` | `-c` | Figure caption (required) |
| `--vlm-provider` | | VLM provider: openai, gemini, openrouter (default: openai) |
| `--output` | `-o` | Output JSON path for evaluation results |
| `--verbose` | `-v` | Show detailed evaluation reasoning |

## Output Format

```json
{
  "evaluation_mode": "comparative | standalone",
  "aggregate_score": 7.75,
  "verdict": "ACCEPT | REVISE | REJECT",
  "primary_dimensions": {
    "faithfulness": {
      "score": 8.5,
      "rationale": "Detailed explanation...",
      "findings": ["specific observations"]
    },
    "readability": {
      "score": 7.0,
      "rationale": "...",
      "findings": ["..."]
    }
  },
  "secondary_dimensions": {
    "conciseness": { "score": 8.0, ... },
    "aesthetics": { "score": 7.5, ... }
  },
  "recommendations": ["actionable improvements"],
  "comparison_notes": "For comparative mode only"
}
```

## Common Pitfalls

1. **Missing context** — Always provide source text for faithfulness evaluation
2. **Wrong caption** — Caption must match the communicative intent
3. **Image too large** — Some VLMs have size limits; resize if needed
4. **Comparative without reference** — Omit `--reference` for standalone mode

## Verification Checklist

- [ ] Generated image exists and is readable
- [ ] Source context is provided
- [ ] Caption matches the figure's intent
- [ ] VLM provider API key is set
- [ ] Output JSON is valid and complete
