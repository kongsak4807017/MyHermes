---
name: paperbanana-diagram
description: "Generate publication-quality academic methodology diagrams from text descriptions using a multi-agent pipeline. Wraps PaperBanana-style generation with Hermes native tools."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [paperbanana, diagram, academic-figures, methodology, multi-agent, image-generation]
    related_skills: [paperbanana-plot, paperbanana-evaluate, paperbanana-shared-references]
    category: creative
---

# PaperBanana Diagram

Generate publication-quality academic methodology diagrams from text descriptions using a multi-agent pipeline with iterative refinement.

## When to Use

- User asks to create a diagram for a research paper
- User has methodology text and wants a visual representation
- User needs a figure for NeurIPS/ICML/ACL/IEEE submission
- User wants to convert a paper section into an illustration

## When NOT to Use

- User wants a simple sketch or mockup → use `sketch` skill
- User wants a non-academic image → use `comfyui` or `stable-diffusion-image-generation`
- User wants an architecture/cloud diagram → use `architecture-diagram` or `excalidraw`

## Prerequisites

- Python 3.10+ with `pip` available
- API key for at least one provider: OpenAI, Google Gemini, or OpenRouter
- `paperbanana` Python package (auto-installed on first use via setup script)

## Quick Start

### Step 1: Set API Keys

```bash
# Option A: OpenAI (recommended for best quality)
export OPENAI_API_KEY="sk-..."

# Option B: Google Gemini (free tier)
export GOOGLE_API_KEY="..."

# Option C: OpenRouter (flexible routing)
export OPENROUTER_API_KEY="..."
```

Or write to `~/.paperbanana/.env`:
```bash
mkdir -p ~/.paperbanana
cat > ~/.paperbanana/.env << 'EOF'
OPENAI_API_KEY=sk-...
EOF
```

### Step 2: Generate a Diagram

```bash
# Basic generation
python3 ~/.hermes/skills/paperbanana/diagram/scripts/generate_diagram.py \
  --input method.txt \
  --caption "Overview of our encoder-decoder framework" \
  --output ./outputs/diagram.png

# With input optimization and auto-refine
python3 ~/.hermes/skills/paperbanana/diagram/scripts/generate_diagram.py \
  --input method.txt \
  --caption "Overview of our framework" \
  --optimize --auto \
  --venue neurips

# From PDF input
python3 ~/.hermes/skills/paperbanana/diagram/scripts/generate_diagram.py \
  --input paper.pdf \
  --caption "System overview" \
  --pdf-pages "3-8"
```

### Python API

```python
import asyncio
import sys
sys.path.insert(0, "~/.hermes/skills/paperbanana/diagram/scripts")
from generate_diagram import DiagramPipeline

pipeline = DiagramPipeline(
    vlm_provider="openai",
    image_provider="openai",
    venue="neurips",
    optimize=True,
    auto_refine=True
)

result = asyncio.run(pipeline.generate(
    source_context="Our framework consists of...",
    caption="Overview of the proposed method."
))
print(f"Output: {result['image_path']}")
```

## Multi-Agent Pipeline

```
Input Text
    │
    ▼
┌─────────────────┐     ┌─────────────────┐
│ Context Enricher│     │ Caption Sharpener│
│ (parallel)      │     │ (parallel)       │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
            ┌─────────────────┐
            │     Planner     │ ← Retrieves reference examples
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │    Stylist      │ ← Applies venue guidelines
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │   Visualizer    │ ← Calls image_gen tool
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │    Critic       │ ← Evaluates output
            └────────┬────────┘
                     │
            ┌────────┴────────┐
            │  Satisfied?     │
            │  Yes → Output   │
            │  No  → Revise   │
            └─────────────────┘
```

## CLI Reference

| Flag | Short | Description |
|------|-------|-------------|
| `--input` | `-i` | Path to methodology text file or PDF |
| `--caption` | `-c` | Figure caption / communicative intent |
| `--output` | `-o` | Output image path (default: auto-generated) |
| `--iterations` | `-n` | Number of Visualizer-Critic rounds (default: 3) |
| `--auto` | | Loop until critic is satisfied |
| `--max-iterations` | | Safety cap for auto mode (default: 30) |
| `--optimize` | | Enable input optimization |
| `--venue` | | Target venue: neurips, icml, acl, ieee, arxiv (default: neurips) |
| `--vlm-provider` | | VLM provider: openai, gemini, openrouter (default: openai) |
| `--image-provider` | | Image provider: openai, gemini, openrouter (default: openai) |
| `--format` | `-f` | Output format: png, jpeg, webp (default: png) |
| `--pdf-pages` | | PDF page selection: "1-5", "2,4,6-8" |
| `--verbose` | `-v` | Show detailed agent progress |

## Providers

| Provider | VLM Model | Image Model | Notes |
|----------|-----------|-------------|-------|
| openai | gpt-4o | dall-e-3 | Best quality, requires API key |
| gemini | gemini-2.0-flash | gemini-2.0-flash | Free tier available |
| openrouter | Any | Any | Flexible routing |

## Common Pitfalls

1. **Missing API key** — Set at least one of OPENAI_API_KEY, GOOGLE_API_KEY, or OPENROUTER_API_KEY
2. **Vague captions** — Use `--optimize` to sharpen captions automatically
3. **Wrong venue style** — Always specify `--venue` for correct color palette and formatting
4. **PDF without pages** — Use `--pdf-pages` to select relevant sections, not the whole paper
5. **Auto-refine too long** — Set `--max-iterations` to prevent infinite loops

## Verification Checklist

- [ ] API key is set and valid
- [ ] Input file exists and is readable
- [ ] Caption is specific (or --optimize is enabled)
- [ ] Venue is specified correctly
- [ ] Output directory is writable
- [ ] Generated image opens correctly
- [ ] Image matches source methodology
