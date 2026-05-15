# Multi-Provider Delegation & Subagent Configuration

Session-specific knowledge from 2026-05-04: configuring Hermes to auto-delegate tasks to subagents using different providers (OpenRouter, HuggingFace) to distribute token usage and avoid rate limits.

## Pattern: Adding Tool Guidance to System Prompts

When you want Hermes to automatically use a tool (like MemPalace or delegate_task) without the user explicitly asking, inject guidance into the system prompt via the `_build_system_prompt()` hook chain.

### Files to modify:

**1. `agent/prompt_builder.py`** — Add the guidance constant:

```python
DELEGATION_GUIDANCE = (
    "You have access to delegate_task — spawn parallel subagents to offload work. "
    "Use it automatically when:\n"
    "- The task has 2+ independent parts that can run in parallel\n"
    "- A subtask is reasoning-heavy and would flood your context with intermediate data\n"
    "- You need to research multiple topics simultaneously\n"
    "- You need to verify your own work by having another agent review it\n"
    "- The task involves file operations across multiple directories\n"
    "Do NOT delegate for: single-step work, trivial tasks, or re-delegating your entire goal.\n"
    "When delegating, pass clear goals and relevant context. Subagents use OpenRouter/Gemini by default."
)
```

**2. `run_agent.py`** — Import the constant (around line 134):

```python
from agent.prompt_builder import (
    DEFAULT_AGENT_IDENTITY, PLATFORM_HINTS,
    MEMORY_GUIDANCE, SESSION_SEARCH_GUIDANCE, SKILLS_GUIDANCE,
    HERMES_AGENT_HELP_GUIDANCE,
    KANBAN_GUIDANCE, MEMPALACE_GUIDANCE, DELEGATION_GUIDANCE,  # <-- add here
    build_nous_subscription_prompt,
)
```

**3. `run_agent.py` `_build_system_prompt()`** — Hook at line ~4909:

```python
        if "delegate_task" in self.valid_tool_names:
            tool_guidance.append(DELEGATION_GUIDANCE)
```

The pattern checks `self.valid_tool_names` (a set of loaded tool names) and appends guidance only when the tool is actually available. This keeps the system prompt minimal when tools aren't loaded.

## Delegation Config with Fallback Providers

```yaml
# ~/.hermes/config.yaml
delegation:
  model: google/gemini-2.5-flash-preview:free
  provider: openrouter
  base_url: ''
  api_key: ''
  inherit_mcp_toolsets: true
  max_iterations: 50
  child_timeout_seconds: 600
  reasoning_effort: none
  max_concurrent_children: 3
  max_spawn_depth: 1
  orchestrator_enabled: true
  subagent_auto_approve: false
  auto_verify:
    enabled: true
    max_iterations: 8
    append_summary: true
  fallback_providers:
    - provider: huggingface
      model: meta-llama/Llama-3.2-3B-Instruct
      base_url: https://router.huggingface.co/v1
      api_key: ${HF_TOKEN}
```

## HuggingFace Provider Config

```yaml
providers:
  huggingface:
    name: HuggingFace Inference
    base_url: https://router.huggingface.co/v1
    transport: openai_chat
    key_env: HF_TOKEN
    api: https://router.huggingface.co/v1
    model: meta-llama/Llama-3.2-3B-Instruct
    skip_model_validation: true
    custom_model: true
    models:
    - meta-llama/Llama-3.2-3B-Instruct
    - meta-llama/Llama-3.1-8B-Instruct
    - microsoft/Phi-4-mini-instruct
    default_model: meta-llama/Llama-3.2-3B-Instruct
    api_key: ${HF_TOKEN}
```

## Key Points

- `fallback_providers` under `delegation` is NOT a standard config key in vanilla Hermes — it was added in this session as a custom extension pattern. The actual fallback logic would need to be implemented in `tools/delegate_tool.py` or handled by the provider router.
- HuggingFace Inference API is **free for public models** but has rate limits (typically 20-40 req/min for small models).
- `skip_model_validation: true` is required for HF because the model list isn't in Hermes' built-in catalog.
- `${HF_TOKEN}` env var interpolation works in config.yaml via the config loader.
- The `mcp_mempalace_*` prefix check pattern: `any(name.startswith("mcp_mempalace_") for name in self.valid_tool_names)` — this is how you detect MCP tools in the loaded toolset.
