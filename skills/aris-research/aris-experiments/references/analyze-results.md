---
name: analyze-results
category: research
---

> **ARIS Port**: Original from [Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
> **Group**: aris-experiments
> **Port Date**: 2026-05-10

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


# Analyze Experiment Results

Analyze: {{arguments}}

## Workflow

### Step 1: Locate Results
Find all relevant JSON/CSV result files:
- Check `figures/`, `results/`, or project-specific output directories
- Parse JSON results into structured data

### Step 2: Build Comparison Table
Organize results by:
- **Independent variables**: model type, hyperparameters, data config
- **Dependent variables**: primary metric (e.g., perplexity, accuracy, loss), secondary metrics
- **Delta vs baseline**: always compute relative improvement

### Step 3: Statistical Analysis
- If multiple seeds: report mean +/- std, check reproducibility
- If sweeping a parameter: identify trends (monotonic, U-shaped, plateau)
- Flag outliers or suspicious results

### Step 4: Generate Insights
For each finding, structure as:
1. **Observation**: what the data shows (with numbers)
2. **Interpretation**: why this might be happening
3. **Implication**: what this means for the research question
4. **Next step**: what experiment would test the interpretation

### Step 5: Update Documentation
If findings are significant:
- Propose updates to project notes or experiment reports
- Draft a concise finding statement (1-2 sentences)

## Output Format
Always include:
1. Raw data table
2. Key findings (numbered, concise)
3. Suggested next experiments (if any)
