# ARIS Deep Port Log — Reference for Future Framework Adoptions

## Source
- **Repo**: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep
- **Size**: 78 skills, 19 shared-references, 22 tools, 18 templates, 6 MCP servers, 15 tests
- **Stars**: 8,649 (as of 2026-05-10)

## Port Decisions

### Umbrella Grouping (Critical)
User explicitly prefers "sub-skills per domain" over monolithic skills. Grouped 78 ARIS skills into 12 umbrellas:

| Umbrella | ARIS Skills | Purpose |
|----------|-------------|---------|
| aris-research-core | 9 skills | W1: Idea Discovery |
| aris-experiments | 12 skills | W1.5: Experiment Bridge |
| aris-review-quality | 7 skills | W2: Auto Review + Quality Gates |
| aris-paper-writing | 20 skills | W3: Paper Writing |
| aris-rebuttal-resubmit | 2 skills | W4+W5: Rebuttal + Resubmit |
| aris-patent-ip | 9 skills | Patent Pipeline |
| aris-infrastructure | 7 skills | Wiki, Meta-optimize, Notifications |
| aris-literature-search | 7 skills | arXiv, Semantic Scholar, etc. |
| aris-grant-proposal | 1 skill | Grant writing |
| aris-shared-references | 19 files | Reference contracts |
| aris-workflow-orchestrator | 1 skill | Master pipeline |
| aris-cross-model-review | 1 skill | Review routing |
| aris-smart-hospital | 1 skill | Project adaptation |
| aris-ioc-system | 1 skill | Project adaptation |

### Tool Mapping
| ARIS | Hermes |
|------|--------|
| Bash(*) | terminal |
| Read | read_file |
| Write | write_file |
| Edit | patch |
| Grep | search_files |
| Glob | search_files (target='files') |
| WebSearch | web_search |
| WebFetch | browser |
| Agent | delegate_task |
| Skill | skill_view / skill_manage |
| mcp__codex__codex | delegate_task (reviewer subagent) |

### Technical Fixes During Port
1. **Python 3.9 `from __future__ import annotations`** — ARIS had it after docstrings, caused SyntaxError. Fixed by moving to line 1.
2. **Unicode em-dashes (U+2014)** in source comments caused Python SyntaxError. Replaced with ASCII hyphens.
3. **skill_manage(action='create') failures** — All SKILL.md creation used write_file() instead to bypass YAML parser issues.

### Verification Results
- `find ~/.hermes/skills/aris-research -type f` → 133 files, 1.9MB
- `research_wiki.py stats ~/.hermes/aris-wiki` → wiki initialized, 0 papers
- `project_pipeline.py "test" --type smart-hospital` → project created with 6 phases
- `quality_gate_runner.py <project> --type project --assurance draft` → ALL GATES PASSED
- `research_wiki.py ingest_paper ~/.hermes/aris-wiki --arxiv-id 2406.04329` → SUCCESS, paper ingested

## Key Files
- `~/.hermes/skills/aris-research/aris-workflow-orchestrator/SKILL.md` — Master pipeline
- `~/.hermes/skills/aris-research/aris-infrastructure/scripts/research_wiki.py` — Wiki tool
- `~/.hermes/skills/aris-research/aris-review-quality/scripts/quality_gate_runner.py` — Quality gates
- `~/.hermes/skills/aris-research/aris-cross-model-review/scripts/review_router.py` — Review routing
