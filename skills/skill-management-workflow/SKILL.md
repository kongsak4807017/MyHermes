---
name: skill-management-workflow
description: วิธีสร้างและ update skills ใน Hermes Agent — รู้ว่าเมื่อไหร่ใช้ skill_manage() vs write_file()โดยตรง รวมถึง pitfalls ของ YAML frontmatter และโครงสร้างไฟล์
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, skill_manage, write_file, frontmatter, troubleshooting]
    related_skills: [hermes-agent]
---

# Skill Management Workflow

## วิธีการสร้าง Skill

### วิธีที่ 1: `skill_manage(action='create')` (แนะนำ)
ใช้สำหรับสร้าง skill ใหม่ — ตรวจสอบ YAML frontmatter อัตโนมัติ

```python
skill_manage(
    action='create',
    name='my-skill',
    content="""---
name: my-skill
description: Description of the skill
version: 1.0.0
author: You
license: MIT
---
# Skill Content
...""",
)
```

**ข้อจำกัด**: content ต้องเป็น string เดียว ที่ขึ้นต้นด้วย `---` YAML frontmatter โดยตรง — ไม่มี line breaks หรือ formatting ที่ทำให้ parser fail

### วิธีที่ 2: `write_file()` (fallback สำหรับ complex content)
ถ้า `skill_manage` fail บ่อย ๆ จากปัญหา frontmatter parsing:

```
write_file(
    path="/home/user/.hermes/skills/my-skill/SKILL.md",
    content="""---
name: my-skill
description: ...
---
# Content
..."""
)
```

**ข้อดี**: bypasses YAML parser ของ skill_manage — direct file write
**ข้อเสีย**: ไม่มี validation, ไม่มี auto-discovery metadata

## เมื่อไหร่ใช้อะไร

| สถานการณ์ | วิธีที่ใช้ |
|-----------|-----------|
| Content สั้น, straight YAML | `skill_manage(action='create')` |
| Content ยาว, มี special chars | `write_file()` → `~/.hermes/skills/<name>/SKILL.md` |
| แค่ add reference files | `skill_manage(action='write_file')` |
| แก้ไข SKILL.md | `skill_manage(action='patch')` |

## Pitfalls

### ❌ `skill_manage` + YAML frontmatter errors
ถ้าเจอ error "SKILL.md must start with YAML frontmatter (---)" ทั้งที่ content ขึ้นต้นด้วย `---`:
- เป็น bug ใน YAML parser — string ที่ซับซ้อนอาจถูก parse ผิด
- วิธีแก้: ใช้ `write_file()` แทน โดยเขียนไฟล์ไปที่ `~/.hermes/skills/<name>/SKILL.md` โดยตรง

### ❌ ห้าม hardcode `~/.hermes` ใน tool code
แต่ในการเขียน skills — path `~/.hermes/skills/` ใช้ได้ใน `write_file()` เพราะเรากำลังสร้างไฟล์ skill ไม่ใช่ running code

### ❌ ลบ skills ด้วย `rm` ไม่ได้ผ่าน system
ถ้าต้องลบ skill ที่สร้างผิด: ต้องใช้ terminal tool แต่ user อาจปฏิเสธ — ให้แจ้ง user แทน

## โครงสร้าง Skill ที่ดี

```
~/.hermes/skills/<name>/
├── SKILL.md              # Main file — YAML frontmatter + markdown
├── references/           # Reference docs
├── scripts/              # Shell/Python scripts
├── templates/            # Template files
└── assets/               # Images, data files
```

## Pattern: Converting GitHub Org Repos to Skills

When a user asks to study all repos in a GitHub organization and convert them to skills:

```python
# 1. Fetch repo list via GitHub API
result = subprocess.run(
    ["curl", "-s", "https://api.github.com/orgs/<org>/repos?per_page=100"],
    capture_output=True, text=True
)
repos = json.loads(result.stdout)

# 2. Group by domain (AI SDK, MCP, chatbot, Next.js, edge, etc.)
# 3. Fetch READMEs for each repo
# 4. Analyze tech stack, patterns, code examples
# 5. Create class-level umbrella skills (not per-repo)
# 6. Start with write_file() for complex content to avoid YAML parser issues
```

**Key decisions:**
- Group repos by domain → create umbrella skills (e.g., `vercel-ai-sdk-patterns`, not `vercel-labs-repo-123`)
- Use `write_file()` not `skill_manage(action='create')` for long/complex SKILL.md to avoid frontmatter parsing failures
- Place skills under `~/.hermes/skills/<org>/` for organization

**Example output structure (from vercel-labs session):**
```
~/.hermes/skills/vercel-labs/
├── vercel-ai-sdk-patterns/        # Theory + patterns from READMEs
├── vercel-ai-sdk-production/      # Real npm packages, deployable code
├── vercel-mcp-integration/        # MCP server/client patterns
├── vercel-ai-agents/             # Multi-agent, coding agent patterns
├── vercel-nextjs-patterns/        # App Router, auth, PPR
├── vercel-edge-deployment/        # Edge Functions, ffmpeg
├── vercel-chatbot-patterns/       # Gemini, ChatGPT starters
├── vercel-v0-prompt-to-ui/        # Generative UI, Sandpack
├── vercel-web-interface-guidelines/ # UI/UX patterns
└── vercel-fullstack-ai-app/       # Master workflow: PLAN → DEPLOY
```

**Critical workflow insight:** When the user says "make it as powerful as vercel.com", don't just add more content to existing theory skills — create NEW production-focused skills with:
- Real `npm install` commands (not just "install ai")
- Actual `.env.local` variables
- Deploy commands (`vercel --prod`)
- Database schemas + migration scripts
- Rate limiting, monitoring, error handling
- v0.dev-like generative UI patterns (GPT-4o vision + Sandpack)

## Pattern: Upgrading Theory Skills to Production Skills

When skills contain only conceptual patterns but user wants production-ready code:

```python
# Phase 1: Create production skill with REAL npm packages
# - Replace "import { openai } from '@ai-sdk/openai'" with actual working code
# - Add real environment variables (.env.local)
# - Add deployment commands (vercel --prod)
# - Add database schemas and migration scripts
# - Add rate limiting, monitoring, error handling

# Phase 2: Create v0.dev-like generative UI skill
# - Screenshot-to-code with GPT-4o vision
# - Text-to-React with Sandpack preview
# - Iterative refinement patterns

# Phase 3: Create master workflow skill
# - End-to-end: PLAN → SETUP → BUILD → INTEGRATE → DEPLOY → MONITOR
# - Complete file structure
# - Checklist for each phase
```

**Pitfall:** Don't try to put everything in one skill — create umbrella skills per domain + a master workflow skill that references them.

## Pattern: Deep Port External Research Frameworks to Hermes Skills

When a user asks to adopt a large external research framework (e.g., ARIS with 78 skills, 19 shared-references, 22 tools):

```python
# Phase 0: Clone and audit the external repo
# - git clone --depth 1 <repo_url> /tmp/<name>-source
# - Count skills, tools, templates, docs, tests
# - Map ARIS tool names → Hermes equivalents (Bash→terminal, Agent→delegate_task, etc.)

# Phase 1: Port skills as class-level umbrella groups (NOT 78 individual skills)
# - Group by workflow domain: research-core, experiments, review-quality, paper-writing, etc.
# - Create 8-12 umbrella skills, each with references/ directory containing ported sub-skills
# - Transform frontmatter: replace mcp__codex__codex with delegate_task (reviewer subagent)

# Phase 2: Port shared-references as standalone skill
# - assurance-contract, citation-discipline, effort-contract, venue-checklists, etc.
# - All reference files go under references/ directory

# Phase 3: Port tools to scripts/ directories
# - research_wiki.py → aris-infrastructure/scripts/
# - arxiv_fetch.py, semantic_scholar_fetch.py → aris-literature-search/scripts/
# - quality_gate_runner.py, verify_paper_audits.py → aris-review-quality/scripts/
# - Add Hermes-specific headers and defaults

# Phase 4: Create project-specific adaptations
# - Smart Hospital: clinical-discovery → prototype → compliance → documentation
# - IOC System: operations-discovery → simulation → security → ops-docs
# - Workflow orchestrator: master pipeline that routes by --type

# Phase 5: Build cross-model review routing
# - Executor (main model) × Reviewer (delegate_task subagent)
# - review_router.py prepares review packages for delegate_task
# - 6-state verdict system: PASS/FAIL/FIX/KEEP/REPLACE/REMOVE/USER_DECISION

# Phase 6: Initialize persistent infrastructure
# - Research wiki at ~/.hermes/aris-wiki/
# - Project pipeline script for initialization
# - Quality gate runner with draft/submission assurance levels
```

**Critical decisions for deep ports:**
- **Umbrella grouping is mandatory** — user explicitly prefers "sub-skills per domain" over monolithic skills
- **Use write_file() for all SKILL.md creation** — skill_manage(action='create') fails on complex frontmatter
- **Port tools as runnable scripts** — not just documentation, but actual Python/shell scripts
- **Create Hermes-native wrappers** — don't just copy; add Hermes defaults, tool mappings, session persistence
- **Test end-to-end** — initialize wiki, ingest paper, run quality gate, verify all green

**Pitfall: Don't create 78 individual skills.** Even though the source has 78 skills, the user wants class-level organization. Create 8-12 umbrellas with references/ subdirectories. Example:
```
~/.hermes/skills/aris-research/
├── aris-research-core/          # W1: Idea Discovery
├── aris-experiments/             # W1.5: Experiment Bridge
├── aris-review-quality/          # W2: Auto Review + Quality Gates
├── aris-paper-writing/           # W3: Paper Writing
├── aris-rebuttal-resubmit/       # W4+W5: Rebuttal + Resubmit
├── aris-patent-ip/               # Patent Pipeline
├── aris-infrastructure/          # Wiki, Meta-optimize, Notifications
├── aris-literature-search/       # arXiv, Semantic Scholar, etc.
├── aris-grant-proposal/          # Grant writing
├── aris-shared-references/       # 19 reference contracts
├── aris-workflow-orchestrator/   # Master pipeline
├── aris-cross-model-review/      # Review routing
├── aris-smart-hospital/          # Project adaptation
└── aris-ioc-system/              # Project adaptation
```

**Pitfall: Python 3.9 compatibility.** When porting tools, check for `from __future__ import annotations` placement — must be at absolute top of file, before docstrings. The original ARIS code had it after docstrings which caused SyntaxError on Python 3.9. Fix: move to line 1, or remove if not needed.

**Pitfall: Unicode em-dashes in source code.** ARIS source contains Unicode em-dashes (U+2014) in comments that cause Python SyntaxError. Replace with ASCII hyphens before writing.

**Verification checklist after deep port:**
1. `find ~/.hermes/skills/aris-research -type f | wc -l` — should be ~130+ files
2. `python3 research_wiki.py stats ~/.hermes/aris-wiki` — wiki initialized
3. `python3 project_pipeline.py "test topic" --type smart-hospital` — project creates
4. `python3 quality_gate_runner.py <project> --type project --assurance draft` — passes
5. `python3 research_wiki.py ingest_paper <wiki> --arxiv-id <id>` — paper ingests successfully

## Pattern: Create Multi-Agent Tool Wrappers as Skill Groups

When a user asks to wrap an external tool (e.g., PaperBanana) or reimplement its capabilities as Hermes skills:

```python
# Phase 1: Study the source
# - Fetch README via curl/raw.githubusercontent.com
# - Identify core capabilities, pipeline stages, providers
# - Map to Hermes equivalents (image_gen, vision, delegate_task, terminal)

# Phase 2: Assess environment
# - Check if tool is installed (pip show, which)
# - Check dependencies (openai, google-genai, uvx, pipx)
# - Decide: wrap CLI (A) or pure Hermes reimplementation (B)

# Phase 3: Create shared infrastructure
# - shared-references/ with prompt templates (context-enricher, caption-sharpener, planner, stylist, visualizer, critic)
# - shared-references/ with venue checklists (NeurIPS, ICML, ACL, IEEE, arXiv)
# - shared-scripts/ with utilities (LLM calls, image generation, PDF parsing, data sniffing)

# Phase 4: Create per-capability skills
# - <name>-diagram/ — methodology diagram generation
# - <name>-plot/ — statistical plot generation from data
# - <name>-evaluate/ — VLM-as-Judge evaluation
# Each skill gets: SKILL.md + scripts/

# Phase 5: Test end-to-end
# - Syntax check all Python files (py_compile)
# - Run mock-mode pipeline (no API key)
# - Verify metadata output
```

**Example structure (from PaperBanana session):**
```
~/.hermes/skills/paperbanana/
├── shared-references/
│   ├── SKILL.md
│   └── references/
│       ├── prompts/
│       │   ├── context-enricher.md
│       │   ├── caption-sharpener.md
│       │   ├── planner.md
│       │   ├── stylist.md
│       │   ├── visualizer.md
│       │   ├── critic.md
│       │   ├── plot-planner.md
│       │   └── evaluator.md
│       └── venue-checklists.md
├── shared-scripts/
│   └── paperbanana_utils.py
├── diagram/
│   ├── SKILL.md
│   └── scripts/
│       └── generate_diagram.py
├── plot/
│   ├── SKILL.md
│   └── scripts/
│       └── generate_plot.py
└── evaluate/
    ├── SKILL.md
    └── scripts/
        └── evaluate_figure.py
```

**Key decisions:**
- **Pure Hermes implementation preferred** when dependencies are missing — no need to install external packages
- **Shared prompts as markdown files** — easy to edit, version, and reference from multiple skills
- **Shared utilities as Python module** — centralized LLM calls, image generation, PDF parsing
- **Mock mode for testing** — pipeline runs without API keys for validation
- **4-dimension evaluation rubric** — faithfulness, readability, conciseness, aesthetics (reusable across domains)

**Pitfall: Don't install heavy dependencies unless necessary.** The PaperBanana session showed no openai, google-genai, uvx, or pipx installed. Instead of installing everything, we reimplemented with urllib (stdlib) + mock fallbacks. This makes skills portable across machines.

**Pitfall: Use stdlib first, requests second.** The shared utilities try `requests` then fall back to `urllib`. This avoids forcing users to install packages just to use skills.

**Pitfall: Handle missing matplotlib gracefully.** For plot generation, try matplotlib first (generates actual data-driven plots), but if not installed, fall back to image_gen API. Don't fail hard on optional dependencies.

## Pattern: Export Skills for Multi-Machine Use

When a user wants to use skills on multiple machines via GitHub:

```bash
# Option 1: Full backup (all skills)
cd ~/.hermes/skills
git init
git add .
git commit -m "Hermes skills collection: $(find . -name SKILL.md | wc -l) skills"
git remote add origin https://github.com/<user>/hermes-skills.git
git push -u origin main

# Option 2: Selective export by domain
cd ~/.hermes/skills
# Create separate repos for large domains
cp -r aris-research /tmp/hermes-skills-research/
cp -r paperbanana /tmp/hermes-skills-research/
cp -r research /tmp/hermes-skills-research/
# ... etc for mlops, creative, etc.

# Option 3: Archive for manual transfer
tar czf hermes-skills-$(date +%Y%m%d).tar.gz ~/.hermes/skills/
```

**On target machine:**
```bash
# Clone and merge
git clone https://github.com/<user>/hermes-skills.git /tmp/hermes-skills
rsync -av /tmp/hermes-skills/ ~/.hermes/skills/
# Or for selective merge:
rsync -av /tmp/hermes-skills/aris-research/ ~/.hermes/skills/aris-research/
```

**Critical: Don't overwrite machine-specific skills.** The target machine may have:
- Different API keys in auth.json
- Different cron jobs
- Machine-specific skills (e.g., macOS-only, WSL-specific)
Use `rsync --exclude` or manual merge for these.

**Manifest generation for documentation:**
```bash
# Generate inventory
cd ~/.hermes/skills
find . -name "SKILL.md" | sort > /tmp/skills-manifest.txt
# Count by category
for d in */; do echo "$(find "$d" -name SKILL.md | wc -l) ${d%/}"; done | sort -rn
```

## Verification

สร้าง skill เสร็จแล้วตรวจสอบ:
```bash
hermes skills list | grep <name>
skill_view(name='<name>')
```