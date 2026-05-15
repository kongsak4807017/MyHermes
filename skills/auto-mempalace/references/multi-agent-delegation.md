# Multi-Agent Delegation with Provider Override

Hermes `delegate_task` supports spawning subagents with different providers/models. This is the definitive reference for the capability.

## Core Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `provider` | Override provider for child | `"openrouter"`, `"gemini"`, `"anthropic"` |
| `model` | Override model for child | `"gemini-2.5-pro"`, `"claude-sonnet-4"` |
| `base_url` | Custom endpoint | `"https://api.gemini.com/v1"` |
| `api_key` | Override API key | (rarely needed, inherits from parent) |
| `acp_command` | ACP CLI transport | `"claude"`, `"codex"` |
| `acp_args` | ACP CLI args | `["--acp", "--stdio"]` |
| `toolsets` | Limit child tools | `["web", "terminal", "file"]` |
| `role` | `"leaf"` (default) or `"orchestrator"` | `"orchestrator"` can spawn grandchildren |
| `max_iterations` | Child iteration cap | Default 50 (configurable) |

## Provider Override Pattern

```python
delegate_task(
    goal="Research security vulnerabilities in this codebase",
    provider="openrouter",
    model="anthropic/claude-sonnet-4",
    toolsets=["terminal", "file", "web"],
    role="leaf"
)
```

## ACP CLI Transport Pattern

For Claude Code, Codex CLI, OpenCode CLI:

```python
delegate_task(
    goal="Refactor this function to use async/await",
    acp_command="claude",
    acp_args=["--acp", "--stdio"],
    provider="copilot-acp",
    toolsets=["terminal", "file"]
)
```

## Credential Inheritance

Subagents inherit credentials from parent unless overridden:
- `parent_api_key` → `effective_api_key` (line 985 in delegate_tool.py)
- `parent.base_url` → `effective_base_url`
- `parent.provider` → `effective_provider` (unless override_provider set)

## Config in `~/.hermes/config.yaml`

```yaml
delegation:
  max_concurrent_children: 3      # Parallel subagents
  max_iterations: 50                # Per-subagent iteration cap
  max_spawn_depth: 2                # Tree depth (parent → child → grandchild)
  orchestrator_enabled: true        # Allow children to spawn children
  subagent_auto_approve: false      # Auto-approve dangerous commands
  provider: null                    # Default provider for subagents
  model: null                       # Default model for subagents
  reasoning_effort: null              # Reasoning config for subagents
```

## Depth and Role Rules

- `child_depth = parent._delegate_depth + 1`
- Orchestrator only allowed if `child_depth < max_spawn_depth`
- Grandchildren of orchestrators MUST be leaves (cannot delegate further)
- Kill switch `_get_orchestrator_enabled()` can globally disable orchestration

## Pitfalls

- **Override provider + ACP conflict**: If `override_provider` is set without `override_acp_command`, ACP is cleared to prevent credential bypass (issue #16816)
- **Forced ACP = forced provider**: Setting `override_acp_command` forces `provider="copilot-acp"` and `api_mode="chat_completions"`
- **Toolset intersection**: Child toolsets are intersected with parent's — child cannot gain tools parent lacks
- **MCP toolsets inheritance**: Set `inherit_mcp_toolsets: true` (default) to preserve parent's MCP tools
- **Blocked tools**: `delegate_task` itself is blocked in children (no recursive delegation)
- **0-API-call timeout**: If subagent times out without any API calls, a diagnostic is written to logs

## Available Providers in This Environment

From `~/.hermes/auth.json` credential pool:
- `openrouter` — 3 keys, models from multiple providers
- `kimi-coding` — Kimi coding model (current parent provider)
- `nous` — Nous Portal OAuth
- `huggingface` — HF inference
- `custom:local-qwen-(ngrok)` — Local model via ngrok

## Verification

Test subagent with different provider:
```python
# In Hermes chat:
/delegate "List files in current directory" provider=openrouter model=google/gemini-2.5-pro
```

Or programmatically:
```python
from tools.delegate_tool import delegate_task
result = delegate_task(
    goal="Say hello",
    provider="openrouter",
    model="google/gemini-2.5-pro",
    toolsets=[]
)
```
