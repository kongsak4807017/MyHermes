# MemPalace System Prompt Injection Patches

Exact code changes needed to make Hermes auto-trigger MemPalace tools via system prompt guidance.

## Files Modified

### 1. `agent/prompt_builder.py`

Add MEMPALACE_GUIDANCE constant after SKILLS_GUIDANCE:

```python
MEMPALACE_GUIDANCE = (
    "You have access to MemPalace — a semantic memory palace with 33 MCP tools. "
    "Before answering questions about past work, decisions, projects, or anything "
    "that might be stored in memory, ALWAYS call mcp_mempalace_search first. "
    "After significant sessions (fixing bugs, discovering workarounds, making decisions), "
    "call mcp_mempalace_diary_write to record a summary. "
    "Use mcp_mempalace_mine for verbatim facts, mcp_mempalace_graph_query for connections."
)
```

### 2. `run_agent.py` — Import

Add `MEMPALACE_GUIDANCE` to the import from `agent.prompt_builder`:

```python
from agent.prompt_builder import (
    DEFAULT_AGENT_IDENTITY, PLATFORM_HINTS,
    MEMORY_GUIDANCE, SESSION_SEARCH_GUIDANCE, SKILLS_GUIDANCE,
    HERMES_AGENT_HELP_GUIDANCE,
    KANBAN_GUIDANCE, MEMPALACE_GUIDANCE,  # <-- added MEMPALACE_GUIDANCE
    build_nous_subscription_prompt,
)
```

### 3. `run_agent.py` — Injection Logic

In `_build_system_prompt()`, around line 4907, add after the kanban check:

```python
        if "kanban_show" in self.valid_tool_names:
            tool_guidance.append(KANBAN_GUIDANCE)
        if any(name.startswith("mcp_mempalace_") for name in self.valid_tool_names):
            tool_guidance.append(MEMPALACE_GUIDANCE)
        if tool_guidance:
            prompt_parts.append(" ".join(tool_guidance))
```

## Key Insight

MCP tools register with prefix `mcp_<server>_<tool>`. Check `any(name.startswith("mcp_mempalace_") for name in self.valid_tool_names)` to detect if MemPalace is active. This pattern works for any MCP server — just change the prefix.

## Verification

After restart, check that system prompt contains MemPalace guidance:
```python
# In a test or debug context:
agent = AIAgent(...)
prompt = agent._build_system_prompt()
assert "MemPalace" in prompt
```

## Related: Generic MCP Auto-Trigger Pattern

This same pattern applies to any MCP server:
1. Add `*_GUIDANCE` constant in `prompt_builder.py`
2. Import it in `run_agent.py`
3. Check `any(name.startswith("mcp_<server>_") ...)` in `_build_system_prompt()`
4. Append guidance to `tool_guidance`
