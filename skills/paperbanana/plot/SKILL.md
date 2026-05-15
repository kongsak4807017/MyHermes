---
name: paperbanana-plot
description: "Generate publication-quality statistical plots from CSV/JSON data using a multi-agent pipeline. Wraps PaperBanana-style plot generation with Hermes native tools."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [paperbanana, plot, data-visualization, statistical-plots, academic-figures, multi-agent]
    related_skills: [paperbanana-diagram, paperbanana-evaluate, paperbanana-shared-references]
    category: creative
---

# PaperBanana Plot

Generate publication-quality statistical plots from CSV/JSON data using a multi-agent pipeline with data-aware planning and venue-specific styling.

## When to Use

- User has experimental results in CSV/JSON and wants a publication figure
- User needs a bar chart, line plot, scatter plot, heatmap, etc. for a paper
- User wants venue-appropriate styling (NeurIPS, ICML, ACL, IEEE)
- User needs error bars, significance markers, or confidence intervals

## When NOT to Use

- User wants a non-statistical diagram → use `paperbanana-diagram`
- User wants an interactive visualization → use `p5js` or web tools
- User wants a simple chart quickly → use spreadsheet tools

## Prerequisites

- Python 3.10+ with `pip` available
- Data file in CSV or JSON format
- API key for at least one provider: OpenAI, Google Gemini, or OpenRouter

## Quick Start

### Step 1: Set API Keys

```bash
export OPENAI_API_KEY="sk-..."
# or
export GOOGLE_API_KEY="..."
```

### Step 2: Generate a Plot

```bash
# Basic plot
python3 ~/.hermes/skills/paperbanana/plot/scripts/generate_plot.py \
  --data results.csv \
  --intent "Bar chart comparing model accuracy across benchmarks" \
  --output ./outputs/plot.png

# With venue styling
python3 ~/.hermes/skills/paperbanana/plot/scripts/generate_plot.py \
  --data results.csv \
  --intent "Line plot showing training convergence" \
  --venue neurips \
  --aspect-ratio 16:9
```

### Python API

```python
import asyncio
import sys
sys.path.insert(0, "~/.hermes/skills/paperbanana/plot/scripts")
from generate_plot import PlotPipeline

pipeline = PlotPipeline(
    vlm_provider="openai",
    venue="neurips",
    aspect_ratio="16:9"
)

result = asyncio.run(pipeline.generate(
    data_path="results.csv",
    intent="Bar chart comparing accuracy across models"
))
print(f"Output: {result['image_path']}")
```

## Supported Plot Types

| Type | Best For | Example Intent |
|------|----------|---------------|
| Bar | Comparing categories | "Bar chart comparing model accuracy" |
| Line | Trends over time/epochs | "Line plot showing training loss" |
| Scatter | Relationships, correlations | "Scatter plot of accuracy vs params" |
| Heatmap | Matrix data, attention | "Heatmap of confusion matrix" |
| Box | Distribution comparison | "Box plot of latency across methods" |
| Violin | Distribution with density | "Violin plot of score distributions" |
| Histogram | Data distribution | "Histogram of prediction errors" |

## CLI Reference

| Flag | Short | Description |
|------|-------|-------------|
| `--data` | `-d` | Path to CSV or JSON file (required) |
| `--intent` | | Communicative intent for the plot (required) |
| `--output` | `-o` | Output image path |
| `--venue` | | Target venue: neurips, icml, acl, ieee (default: neurips) |
| `--aspect-ratio` | `-ar` | Aspect ratio: 16:9, 4:3, 1:1 (default: 4:3) |
| `--vlm-provider` | | VLM provider: openai, gemini, openrouter |
| `--iterations` | `-n` | Refinement iterations (default: 3) |
| `--format` | `-f` | Output format: png, jpeg, webp |
| `--verbose` | `-v` | Show detailed progress |

## Common Pitfalls

1. **Wrong data format** — Ensure CSV has headers, JSON is a list of objects
2. **Vague intent** — Be specific: "Bar chart" not "Chart"
3. **Missing error bars** — Mention if uncertainty should be shown
4. **Too many series** — Consider faceting or simplifying

## Verification Checklist

- [ ] Data file exists and is readable
- [ ] Intent clearly specifies plot type
- [ ] Venue is appropriate for target publication
- [ ] Output directory is writable
