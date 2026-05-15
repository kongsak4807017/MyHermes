---
name: github-org-to-skills
description: "Bulk analyze GitHub organization repos and synthesize into Hermes Agent skills. Fetch READMEs, extract patterns, group by domain, create class-level skills."
version: 1.0.0
author: Hermes Agent
license: MIT
dependencies: [curl, python]
metadata:
  hermes:
    tags: [GitHub, Skills, Analysis, Bulk, Organization, Patterns]
---

# GitHub Org to Skills

Bulk analyze all repositories in a GitHub organization and synthesize them into class-level Hermes Agent skills.

## When to use

**Use when:**
- User asks to "study all repos in [org] and make skills"
- Need to extract reusable patterns from a GitHub organization's repositories
- Want to convert open-source examples into internal knowledge
- Building a skill library from a vendor's example repos (Vercel Labs, Vercel AI SDK examples, etc.)

## Trigger conditions

- User provides a GitHub org URL like `https://github.com/[org-name]`
- User says "study", "analyze", "convert to skills", "make skills from" + GitHub org
- User wants patterns from a vendor's example repo collection

## Workflow

### Phase 1: Discovery (fetch repo list)

```python
import subprocess, json

# Fetch all repos from GitHub API (max 100 per page, handle pagination if >100)
result = subprocess.run(
    ["curl", "-s", f"https://api.github.com/orgs/{ORG}/repos?per_page=100"],
    capture_output=True, text=True
)
repos = json.loads(result.stdout)

# Sort by stars descending for prioritization
repos_sorted = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)

# Print summary
for r in repos_sorted:
    print(f"  {r['name']:<30} {r['stargazers_count']:>6} ⭐  {r.get('description', '')[:60]}")
```

**Pitfall**: Some orgs have >100 repos. Check `len(repos)` — if exactly 100, there may be more pages. Use `page=2`, `page=3`, etc.

**Pitfall**: Private repos won't appear without authentication. If user expects private repos, use `curl -H "Authorization: token $GITHUB_TOKEN"`.

### Phase 2: Fetch READMEs (bulk)

```python
repos_to_fetch = [...]  # Prioritized list (top ~60 by stars, or all if <60)
results = {}

for repo in repos_to_fetch:
    # Try main branch first, then master
    for branch in ["main", "master"]:
        url = f"https://raw.githubusercontent.com/{ORG}/{repo}/{branch}/README.md"
        r = subprocess.run(["curl", "-sL", "--max-time", "10", url], capture_output=True, text=True)
        if r.returncode == 0 and len(r.stdout) > 100 and "404" not in r.stdout[:50]:
            results[repo] = r.stdout[:5000]  # First 5KB is usually enough
            break
```

**Pitfall**: README might be in subdirectory (e.g., `packages/foo/README.md`). If main README is empty/short, try fetching repo tree via API to find other READMEs.

**Pitfall**: Rate limiting — if fetching many repos, add `sleep(0.5)` between requests or use `GITHUB_TOKEN`.

### Phase 3: Analyze patterns programmatically

```python
import re

analysis = {}
for repo, readme in results.items():
    # Extract tech stack mentions
    tech_patterns = {
        'nextjs': bool(re.search(r'next\.js|Next\.js|nextjs', readme, re.I)),
        'react': bool(re.search(r'react', readme, re.I)),
        'ai_sdk': bool(re.search(r'ai sdk|AI SDK|@ai-sdk', readme, re.I)),
        'vercel': bool(re.search(r'vercel', readme, re.I)),
        'mcp': bool(re.search(r'mcp|MCP|model.context.protocol', readme, re.I)),
        'postgres': bool(re.search(r'postgres|postgresql', readme, re.I)),
        'streaming': bool(re.search(r'stream|streamText|streamUI', readme, re.I)),
        'rag': bool(re.search(r'rag|retriev|vector', readme, re.I)),
        'auth': bool(re.search(r'auth|Auth|next-auth|clerk', readme, re.I)),
        'tailwind': bool(re.search(r'tailwind|shadcn', readme, re.I)),
    }
    
    # Count code blocks
    code_blocks = len(re.findall(r'```[\w]*\n(.*?)```', readme, re.DOTALL))
    
    analysis[repo] = {
        'tech_stack': {k:v for k,v in tech_patterns.items() if v},
        'code_blocks': code_blocks,
        'readme_length': len(readme)
    }
```

### Phase 4: Group by domain (class-level clustering)

Group repos into 5-8 class-level categories. Common patterns:

| Domain | Keywords |
|--------|----------|
| AI SDK / LLM | `ai-sdk`, `chat`, `stream`, `generate` |
| MCP | `mcp`, `model-context-protocol` |
| Chatbot | `chatbot`, `chat`, `conversation` |
| Framework | `nextjs`, `react`, `remix` |
| Edge/Deploy | `edge`, `deploy`, `vercel` |
| Agents | `agent`, `coding`, `research`, `workflow` |
| UI/UX | `ui`, `interface`, `design`, `component` |

```python
skill_groups = {}
for repo, info in analysis.items():
    tech = info['tech_stack']
    # Assign to group based on tech stack + repo name
    if 'mcp' in tech or repo.startswith('mcp-'):
        skill_groups.setdefault('mcp', []).append(repo)
    elif 'ai_sdk' in tech or repo.startswith('ai-sdk'):
        skill_groups.setdefault('ai-sdk', []).append(repo)
    # ... etc
```

**Key principle**: Groups should be CLASS-LEVEL, not repo-level. 100 repos → 5-8 skills, not 100 skills.

### Phase 5: Synthesize skills

For each group:
1. Read all READMEs in the group
2. Extract the top 5-10 most distinct patterns
3. Write code examples (TypeScript/Python) showing the pattern
4. Include architecture diagrams
5. Add deployment notes

**Skill naming convention**: `{org-short}-{domain}-patterns` or `{org-short}-{domain}`

Examples:
- `vercel-ai-sdk-patterns`
- `vercel-mcp-integration`
- `vercel-chatbot-patterns`

### Phase 6: Create skills in filesystem

```bash
mkdir -p ~/.hermes/skills/{org-short}/{skill-name}/
# Write SKILL.md
# Add references/ if needed for detailed examples
```

## Output format

Each skill should have:
- YAML frontmatter with name, description, dependencies, tags
- `# When to use` section with trigger conditions
- Architecture diagram (ASCII)
- `## Quick Start` with installation
- `## Patterns` with numbered patterns, each with code example
- `## Deployment` section
- `## References` linking back to source repos

## References
- https://docs.github.com/en/rest/repos/repos#list-organization-repositories
