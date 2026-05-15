# Multi-Skill Group Example: PaperBanana

Concrete example of the class-level umbrella pattern for external tool reimplementation.

## Context

PaperBanana (https://github.com/llmsresearch/paperbanana) is a multi-agent academic figure generation framework. Rather than installing it as a Python package, we reimplemented its pipeline as Hermes skills.

## Directory Structure

```
~/.hermes/skills/paperbanana/
├── shared-references/
│   ├── SKILL.md                          # Index of all shared prompts
│   └── references/
│       ├── prompts/
│       │   ├── context-enricher.md       # Phase 0 agent prompt
│       │   ├── caption-sharpener.md      # Phase 0 agent prompt
│       │   ├── planner.md                # Phase 1 agent prompt
│       │   ├── stylist.md                # Phase 2a agent prompt
│       │   ├── visualizer.md             # Phase 2b agent prompt
│       │   ├── critic.md                 # Phase 2c agent prompt
│       │   ├── plot-planner.md           # Plot-specific planner
│       │   └── evaluator.md              # VLM-as-Judge prompt
│       └── venue-checklists.md           # NeurIPS/ICML/ACL/IEEE requirements
├── shared-scripts/
│   └── paperbanana_utils.py              # LLM calls, image gen, PDF parsing
├── diagram/
│   ├── SKILL.md                          # Triggers: "create methodology diagram"
│   └── scripts/
│       └── generate_diagram.py           # Full pipeline: Optimizer→Planner→Stylist→Visualizer↔Critic
├── plot/
│   ├── SKILL.md                          # Triggers: "create plot from CSV"
│   └── scripts/
│       └── generate_plot.py              # Pipeline: DataAnalyzer→PlotPlanner→Visualizer↔Critic
└── evaluate/
    ├── SKILL.md                          # Triggers: "evaluate figure quality"
    └── scripts/
        └── evaluate_figure.py            # 4-dimension VLM-as-Judge evaluation
```

## Why This Structure

1. **Shared prompts**: All 8 prompt templates live in one place. If we improve the critic prompt, all three sub-skills benefit.
2. **Shared utilities**: `paperbanana_utils.py` handles LLM API calls (with fallback chain: requests → urllib → mock), image generation, PDF parsing, and data schema sniffing. No duplication.
3. **Focused sub-skills**: Each SKILL.md targets a specific trigger class. A user asking for a plot doesn't need to read about diagram optimization.
4. **Reusable pattern**: The same structure works for any external tool with multiple capabilities (e.g., `vercel-labs/` already uses this pattern).

## Key Design Decisions

### Fallback Chain for LLM Calls

Since Hermes doesn't expose `hermes_tools` as an importable Python module, the shared utility implements a fallback chain:

```
1. Try importing hermes_tools (for future compatibility)
2. Try requests (if installed)
3. Try urllib (stdlib, always available)
4. Return mock response (for testing without API keys)
```

This lets the skills work immediately without installing dependencies, while still supporting real API calls when keys are available.

### Plot Visualization Dual Path

Plot generation tries matplotlib first (deterministic, data-accurate), then falls back to DALL-E (for complex or stylized plots). This is different from PaperBanana's approach which always uses image_gen.

### Evaluation Modes

- **Text-only**: Describes the image and evaluates from description (works with any LLM)
- **Vision**: Sends base64-encoded image to vision-capable model (GPT-4o, Gemini) for direct visual evaluation

## Lessons Learned

- Sub-skills should reference the umbrella in `related_skills` for discoverability
- Shared scripts should use stdlib where possible to minimize setup friction
- Mock mode is essential for testing pipelines before API keys are configured
- Venue-specific guidelines (NeurIPS vs IEEE) should be shared references, not hardcoded
