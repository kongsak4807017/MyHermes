# Vercel Labs GitHub Analysis Workflow

Pattern for analyzing GitHub organization repositories and extracting reusable knowledge for Hermes skills.

## Workflow

```
1. FETCH repos list via GitHub API
2. GROUP by domain (ai-sdk, mcp, chatbot, nextjs, edge, etc.)
3. FETCH README for each repo
4. ANALYZE patterns & extract code
5. CREATE skills under ~/.hermes/skills/<category>/
```

## Step 1: Fetch Repository List

```python
import subprocess, json

result = subprocess.run(
    ["curl", "-s", "https://api.github.com/orgs/vercel-labs/repos?per_page=100"],
    capture_output=True, text=True
)
repos = json.loads(result.stdout)
repos_sorted = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)
```

## Step 2: Group by Domain

```python
groups = {
    "ai-sdk": [],
    "mcp": [],
    "chatbot": [],
    "nextjs-patterns": [],
    "deployment-edge": [],
    "other": []
}

for r in repos:
    name = r.get("name", "").lower()
    if "ai-sdk" in name:
        groups["ai-sdk"].append(r)
    elif "mcp" in name:
        groups["mcp"].append(r)
    # ... etc
```

## Step 3: Fetch READMEs

```python
for repo in repos:
    url = f"https://raw.githubusercontent.com/vercel-labs/{repo}/main/README.md"
    r = subprocess.run(["curl", "-sL", "--max-time", "10", url], ...)
    if r.returncode == 0 and len(r.stdout) > 100:
        results[repo] = r.stdout[:5000]  # First 5KB
```

## Step 4: Analyze Patterns

Extract per repo:
- Tech stack (Next.js, React, AI SDK, etc.)
- Code architecture
- Key patterns
- Integration methods

## Step 5: Create Skills

Skill structure:
```
~/.hermes/skills/vercel-labs/
├── vercel-ai-sdk-patterns/
├── vercel-mcp-integration/
├── vercel-ai-agents/
├── vercel-nextjs-patterns/
├── vercel-edge-deployment/
├── vercel-chatbot-patterns/
└── vercel-web-interface-guidelines/
```

Each SKILL.md includes:
- YAML frontmatter with name, description, tags
- When to use section
- Architecture diagrams
- Quick start with real commands
- 5-20 patterns with code examples
- Deployment instructions

## Lessons Learned

| Issue | Solution |
|-------|----------|
| README 404 on main branch | Fallback to master branch |
| Truncated README | Limit to first 5KB, use offset for continuation |
| Missing descriptions | Use repo name + topic tags as fallback |
| Overlapping patterns | Create umbrella skill + sub-skills |

## References

- GitHub API: https://docs.github.com/en/rest/repos/repos#list-organization-repositories
- This session analyzed 65/67 vercel-labs repos
