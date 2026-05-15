# PaperBanana Skill Group Creation Log

Session: 2026-05-16
Trigger: User asked to study https://github.com/llmsresearch/paperbanana and create equivalent Hermes skills

## Source Analysis

PaperBanana is a multi-agent framework for generating publication-quality academic diagrams and statistical plots:
- 7-agent pipeline: Input Optimizer → Retriever → Planner → Stylist → Visualizer ↔ Critic
- Supports OpenAI (GPT-5.2 + GPT-Image-1.5), Azure, Google Gemini
- CLI, Python API, MCP server, Gradio Studio
- Batch generation, PDF input, composite figures, evaluation

## Environment Assessment

- `paperbanana` package: NOT installed
- `openai` package: NOT installed
- `google-genai` package: NOT installed
- `uvx`/`pipx`: NOT found
- Decision: Pure Hermes reimplementation (Option B) — no external dependencies

## Skill Group Structure Created

```
~/.hermes/skills/paperbanana/
├── shared-references/
│   ├── SKILL.md                          # Umbrella reference skill
│   └── references/
│       ├── prompts/
│       │   ├── context-enricher.md       # Phase 0: raw text → structured context
│       │   ├── caption-sharpener.md      # Phase 0: vague caption → visual spec
│       │   ├── planner.md                # Phase 1: structured context → diagram plan
│       │   ├── stylist.md                # Phase 2a: apply venue style guidelines
│       │   ├── visualizer.md             # Phase 2b: styled spec → image gen prompt
│       │   ├── critic.md                 # Phase 2c: evaluate + revise
│       │   ├── plot-planner.md           # Plot-specific planning
│       │   └── evaluator.md              # VLM-as-Judge 4-dimension rubric
│       └── venue-checklists.md           # NeurIPS/ICML/ACL/IEEE/arXiv requirements
├── shared-scripts/
│   └── paperbanana_utils.py              # LLM calls, image gen, PDF parsing, data sniffing
├── diagram/
│   ├── SKILL.md
│   └── scripts/
│       └── generate_diagram.py           # Full multi-agent diagram pipeline
├── plot/
│   ├── SKILL.md
│   └── scripts/
│       └── generate_plot.py              # Data → plot pipeline (matplotlib + image_gen fallback)
└── evaluate/
    ├── SKILL.md
    └── scripts/
        └── evaluate_figure.py            # 4-dimension evaluation with vision support
```

## Key Design Decisions

1. **Stdlib-first approach**: urllib instead of requests, no external packages required
2. **Mock mode for testing**: Pipeline runs without API keys, returns mock responses
3. **Matplotlib fallback**: Plot skill tries matplotlib first, falls back to DALL-E if unavailable
4. **Shared prompt templates**: All prompts as markdown files for easy editing/versioning
5. **4-dimension rubric reusable**: Faithfulness, Readability, Conciseness, Aesthetics — applicable to any figure evaluation

## Testing Results

- ✅ All Python files compile via py_compile
- ✅ Diagram pipeline runs all phases in mock mode
- ✅ Plot pipeline runs all phases in mock mode
- ✅ Evaluate pipeline returns correct verdict (REVISE for mock)

## Usage Examples

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Generate diagram
python3 ~/.hermes/skills/paperbanana/diagram/scripts/generate_diagram.py \
  --input method.txt --caption "Overview" --venue neurips --optimize --auto

# Generate plot
python3 ~/.hermes/skills/paperbanana/plot/scripts/generate_plot.py \
  --data results.csv --intent "Bar chart comparing accuracy" --venue neurips

# Evaluate figure
python3 ~/.hermes/skills/paperbanana/evaluate/scripts/evaluate_figure.py \
  --generated diagram.png --context method.txt --caption "Overview" --vision
```

## Pitfalls Discovered

- `skill_manage(action='create')` fails on complex frontmatter — use `write_file()` for all SKILL.md creation
- Python 3.9 `from __future__ import annotations` must be at absolute top (line 1)
- Missing dependencies should not block — always provide mock/placeholder fallback
- `hermes_tools` module not available in standalone scripts — use urllib or subprocess
