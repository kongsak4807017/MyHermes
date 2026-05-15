---
name: omk-cli-maintenance
description: Audit, debug, extend, and build OMK CLI — covers maintenance against Hermes schema, building OMK v2.0 agent architecture, and the v2.1 multi-provider orchestrator platform
title: OMK CLI Maintenance & Agent Build-Out
version: 2.1.0
summary: Maintain, debug, and extend OMK (Operational Monitoring & Knowledge) CLI. Covers schema fixes, v2.0 agent core, and v2.1 multi-provider orchestrator with skills, MCP, and long-context support.
---

# OMK CLI Maintenance & Agent Build-Out

## Project Locations

**Current primary location:** `C:\Users\User\OneDrive\OMK\omk` (WSL: `/mnt/c/Users/User/OneDrive/OMK/omk/`)

**Legacy location (no longer used):** `~/.hermes/skills/openclaw-learnings/omk/`

Always use the OneDrive path for current development.

## OMK v2.1 Architecture Overview

OMK v2.1 evolves from a single-provider agent into a **multi-provider AI Agent Platform** with orchestration, subagents, skills, and MCP support.

### New File Structure (v2.1 additions)

```
omk/
├── bin/omk
├── pyproject.toml
├── omk/
│   ├── __init__.py              # v2.1.0 exports
│   ├── config.py
│   ├── llm.py                   # OpenAI-compatible client (fallback)
│   ├── session.py
│   ├── interactive.py           # REPL + slash commands (v2.1: /orchestrate, /provider, etc.)
│   ├── agent/
│   │   └── core.py              # v2.1: provider routing + orchestrator hook
│   ├── providers/               # NEW in v2.1 — CLI adapters for multi-provider
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract base + OpenRouter API provider
│   │   ├── codex.py             # Wraps `codex` CLI via subprocess
│   │   ├── kimi.py              # Wraps `kimi` CLI via subprocess
│   │   └── gemini.py            # Wraps `gemini` CLI via subprocess
│   ├── auth/                    # NEW in v2.1 — OAuth & token management
│   │   ├── __init__.py
│   │   └── manager.py           # Token storage in ~/.omk/auth.json
│   ├── orchestrator/            # NEW in v2.1 — Task decomposition
│   │   ├── __init__.py
│   │   └── engine.py            # Plan → split → delegate → aggregate
│   ├── subagent/                # NEW in v2.1 — Parallel child agents
│   │   ├── __init__.py
│   │   └── spawner.py           # Spawn via CLI or Python subprocess
│   ├── skills/                  # NEW in v2.1 — Skill discovery & execution
│   │   ├── __init__.py
│   │   └── manager.py           # Loads from ~/.omk/skills/<name>/SKILL.md
│   ├── mcp/                     # NEW in v2.1 — MCP client
│   │   ├── __init__.py
│   │   └── client.py            # JSON-RPC over stdio to MCP servers
│   ├── context/                 # NEW in v2.1 — Long context manager
│   │   ├── __init__.py
│   │   └── manager.py           # Sliding window, summarize, truncate
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   ├── terminal_tool.py
│   │   ├── file_tool.py
│   │   ├── web_tool.py
│   │   ├── code_tool.py
│   │   └── delegate_tool.py
│   ├── monitoring/
│   │   ├── cli.py               # v2.1: adds orchestrate, skill, mcp, auth, provider
│   │   ├── metrics.py
│   │   ├── dashboard.py
│   │   ├── monitor.py
│   │   ├── views.py
│   │   ├── analytics.py
│   │   └── ui/
│   └── ui/
```

### v2.1 Commands

| Command | Description |
|---------|-------------|
| `omk chat` | Interactive REPL |
| `omk run` | One-shot prompt |
| `omk agent` | Alias for chat |
| `omk orchestrate --task <task>` | Multi-agent task decomposition |
| `omk skill <name>` | Run with skill activated |
| `omk mcp list` | List MCP servers |
| `omk mcp add <name> <cmd>` | Add MCP server |
| `omk auth` | Show auth status |
| `omk auth --setup <provider>` | Configure provider |
| `omk provider` | List providers |

### v2.1 Interactive Slash Commands

| Command | Description |
|---------|-------------|
| `/provider <name>` | Switch provider (openrouter, codex, kimi, gemini) |
| `/orchestrate` | Toggle orchestrator on/off |
| `/skill <name>` | Activate skill |
| `/skills` | List available skills |
| `/mcp list` | List MCP servers |
| `/context` | Show context window stats |
| `/tokens` | Show token usage |
| `/auth` | Show auth status |
| `/sessions` | List sessions |
| `/resume <id>` | Resume session |

## OMK v2.0 Architecture Overview

OMK is now a full AI Agent CLI with two modes:
1. **Monitoring mode** — read-only dashboards (legacy)
2. **Agent mode** — interactive chat with tool calling (new in v2.0)

### File Structure

```
omk/
├── bin/omk                    # Launcher script (sets PYTHONPATH + venv)
├── pyproject.toml             # Package metadata
├── omk/
│   ├── __init__.py
│   ├── __main__.py            # python -m omk entry point
│   ├── config.py              # Config management, API key resolution
│   ├── llm.py                 # OpenAI-compatible LLM client
│   ├── session.py             # Session manager (SQLite, read/write)
│   ├── interactive.py         # prompt_toolkit REPL with slash commands
│   ├── agent/
│   │   ├── __init__.py
│   │   └── core.py            # Agent chat loop with tool calling
│   ├── tools/
│   │   ├── __init__.py        # Auto-imports all tools
│   │   ├── registry.py        # Central tool registry
│   │   ├── terminal_tool.py   # Shell command execution
│   │   ├── file_tool.py       # read_file, write_file, search_files, patch_file
│   │   ├── web_tool.py        # web_search, web_extract
│   │   ├── code_tool.py       # execute_code
│   │   └── delegate_tool.py   # Subagent delegation
│   ├── monitoring/            # Legacy monitoring code
│   │   ├── cli.py             # Main argparse entry point
│   │   ├── metrics.py
│   │   ├── dashboard.py
│   │   ├── monitor.py
│   │   ├── views.py
│   │   ├── analytics.py
│   │   └── ui/                # Rich widgets, colors, tables
│   └── ui/                    # Re-export wrappers for monitoring.ui
│       ├── __init__.py
│       ├── colors.py
│       ├── tables.py
│       └── widgets.py
```

### Commands

| Command | Mode | Description |
|---------|------|-------------|
| `omk status` | Monitoring | Dashboard snapshot |
| `omk monitor` | Monitoring | Live Rich dashboard |
| `omk health` | Monitoring | Health score + anomalies |
| `omk chat` | Agent | Interactive REPL with tool calling |
| `omk agent` | Agent | Alias for `chat` |
| `omk run` | Agent | Single prompt, print response, exit |
| `omk configure` | Setup | Interactive config + API key setup |

## Adding a New CLI Command

Edit `omk/monitoring/cli.py`:

1. **Add handler function:**
```python
def cmd_mycmd(args):
    """My new command."""
    print(f"Running with: {args.flag}")
    return 0
```

2. **Register in `main()`:**
```python
mycmd_parser = subparsers.add_parser("mycmd", help="Description")
mycmd_parser.add_argument("--flag", default="default")
mycmd_parser.set_defaults(func=cmd_mycmd)
```

3. **Sync to `omk/omk/monitoring/cli.py`** — see Duplicate Path Gotcha below.

## Provider System (v2.1)

### Adding a CLI Provider Adapter

Create `omk/providers/<name>.py`:

```python
from omk.providers.base import BaseProvider

class MyProvider(BaseProvider):
    def __init__(self, auth_manager, **kwargs):
        super().__init__(auth_manager)
        self.model = kwargs.get("model", "default-model")

    def chat(self, messages, tools=None, stream=False, **kwargs):
        # Wrap existing CLI tool via subprocess
        import subprocess, json
        # ... build prompt from messages ...
        result = subprocess.run(
            ["my-cli", "chat", "--json"],
            input=prompt, capture_output=True, text=True
        )
        return json.loads(result.stdout)
```

Register in `omk/providers/__init__.py`:
```python
from omk.providers.myprovider import MyProvider
_PROVIDERS["myprovider"] = MyProvider
```

### Provider Routing

```python
from omk.providers import get_provider

provider = get_provider("kimi", auth_manager, model="kimi-k2.6")
response = provider.chat(messages=[{"role": "user", "content": "Hello"}])
```

## Auth Manager (v2.1)

```python
from omk.auth.manager import get_auth_manager

auth = get_auth_manager()

# Store credentials
auth.set_credentials("openrouter", {"api_key": "sk-or-..."})
auth.set_credentials("kimi", {"token": "..."})

# Retrieve
 creds = auth.get_credentials("openrouter")

# Auto-refresh (for OAuth)
auth.refresh_if_needed("codex")
```

**Storage:** `~/.omk/auth.json` with file permissions 600. Format:
```json
{
  "openrouter": {"api_key": "sk-or-..."},
  "kimi": {"token": "...", "expires_at": 1714000000},
  "codex": {"token": "...", "refresh_token": "..."},
  "gemini": {"token": "..."}
}
```

## Orchestrator (v2.1)

Uses a **plan → split → delegate → aggregate** pipeline:

```python
from omk.orchestrator import Orchestrator

orch = Orchestrator(agent=agent, provider=provider)
result = orch.execute("Refactor all Python files in src/")
```

- **single** (< 7 complexity): direct execution
- **parallel** (7–12): split into subtasks, spawn concurrently (max 6 workers)
- **sequential** (> 12): chained dependencies, accumulate context

## Subagent Spawner (v2.1)

```python
from omk.subagent import SubagentSpawner

spawner = SubagentSpawner(auth_manager)
results = spawner.spawn_batch(
    prompts=["task1", "task2", "task3"],
    provider="codex",
    max_workers=3
)
```

- Prefers CLI spawn (`kimi`, `codex`, `gemini`) if available
- Falls back to Python subprocess with the same codebase

## Skills (v2.1)

Skills live in `~/.omk/skills/<skill-name>/SKILL.md`:

```markdown
---
category: devops
description: Deploy to production
---
# Deployment Skill

1. Run tests
2. Build Docker image
3. Push to registry
4. Restart service
```

```python
from omk.skills import get_skill_manager

sm = get_skill_manager()
sm.discover()                    # Scan ~/.omk/skills/
sm.list_skills()                 # List available
result = sm.execute("deploy", {"environment": "staging"})
```

## MCP Client (v2.1)

```python
from omk.mcp import MCPClient

mcp = MCPClient()
mcp.add_server("filesystem", "npx", ["-y", "@modelcontextprotocol/server-filesystem"])
mcp.list_servers()

# Discover tools from all MCP servers
tools = mcp.discover_tools()
```

Uses stdio JSON-RPC transport to MCP servers.

## Context Manager (v2.1)

Handles 1M+ tokens via multiple strategies:

```python
from omk.context import ContextManager

ctx = ContextManager(strategy="sliding_window", max_tokens=1000000)
ctx.add_message({"role": "user", "content": long_text})
messages = ctx.get_messages()  # Returns trimmed list within budget
```

Strategies:
- `sliding_window` — drop oldest messages (keeps system prompt)
- `summarize` — summarize dropped messages into a compact context
- `truncate` — hard cut at token limit

## Adding a New Tool

1. **Create `omk/tools/your_tool.py`:**
```python
import json
from omk.tools.registry import registry

def your_tool(param: str) -> str:
    return json.dumps({"result": f"got {param}"})

registry.register(
    name="your_tool",
    schema={
        "type": "function",
        "function": {
            "name": "your_tool",
            "description": "What it does",
            "parameters": {
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter description"}
                },
                "required": ["param"],
            },
        },
    },
    handler=lambda args, **kw: your_tool(args.get("param", "")),
    check_fn=lambda: True,
)
```

2. **Add import to `omk/tools/__init__.py`:**
```python
from omk.tools import your_tool
```

3. **Verify:**
```bash
./bin/omk chat
/tools
# Should list your_tool
```

## Adding a New CLI Command

Edit `omk/monitoring/cli.py`:

1. **Add handler function:**
```python
def cmd_mycmd(args):
    """My new command."""
    print(f"Running with: {args.flag}")
    return 0
```

2. **Register in `main()`:**
```python
mycmd_parser = subparsers.add_parser("mycmd", help="Description")
mycmd_parser.add_argument("--flag", default="default")
mycmd_parser.set_defaults(func=cmd_mycmd)
```

## Adding a Slash Command

Edit `omk/interactive.py`:

1. **Add to `SLASH_COMMANDS`:**
```python
"/mycmd": "Description of what it does",
```

2. **Handle in `_handle_command()`:**
```python
if canonical == "/mycmd":
    self.print("My command output", style="green")
    return True
```

## Common Root Cause: Schema Mismatches

The #1 source of OMK breakage is assuming `state.db` uses ISO string timestamps. **It uses REAL Unix timestamps.**

```python
# WRONG — will return empty results
cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
cursor.execute("SELECT ... WHERE started_at > ?", (cutoff,))

# WRONG — date() doesn't work on REAL
cursor.execute("SELECT date(started_at) as date ...")

# CORRECT — use numeric cutoff
cutoff = time.time() - (24 * 3600)
cursor.execute("SELECT ... WHERE started_at > ?", (cutoff,))

# CORRECT — use unixepoch modifier
cursor.execute("SELECT date(started_at, 'unixepoch') as date ...")
```

## Dual Entry Point Architecture (Node.js + Python)

OMK has **two separate entry points** — know which one you're invoking:

| Entry Point | Type | Use When | Platform |
|-------------|------|----------|----------|
| `dist/cli/omk.js` | Node.js ESM | `npm install -g`, `npx omk`, `omk` via npm | All (Windows, macOS, Linux) |
| `bin/omk` | Bash shell script | `python -m omk`, manual WSL launch | Unix/WSL only |

**`dist/cli/omk.js`** is the npm-distributed entry point. It imports `dist/cli/index.js` which implements the full TypeScript/React-Ink TUI, provider system, skills, and orchestration.

**`bin/omk`** is a bash launcher that sets `PYTHONPATH` and runs `python -m omk`. It only works where bash is available.

### npm `package.json` `bin` Field Gotcha (Windows)

**NEVER point `"bin"` to a shell script** in a cross-platform npm package. On Windows, npm generates `.cmd` wrappers that may spawn the file through Node.js, causing Node to try to parse bash as JavaScript:

```
file:///C:/.../omk/bin/omk:2
# OMK CLI launcher
^
SyntaxError: Invalid or unexpected token
```

**Correct `package.json`:**
```json
{
  "bin": {
    "omk": "./dist/cli/omk.js"
  }
}
```

**Wrong `package.json`:**
```json
{
  "bin": {
    "omk": "./bin/omk"
  }
}
```

If you need both entry points, use:
```json
{
  "bin": {
    "omk": "./dist/cli/omk.js",
    "omk-py": "./bin/omk"
  }
}
```

### Running on Windows PowerShell

PowerShell does **not** understand bash syntax (`source`, `2>/dev/null`, `||`):

```powershell
# WRONG — PowerShell errors
source venv/bin/activate
pip install -e . 2>/dev/null || true

# CORRECT — PowerShell syntax
.\venv\Scripts\Activate.ps1
pip install -e .
# Or use cmd fallback
venv\Scripts\activate.bat
```

**Recommended Windows workflow:**
```powershell
cd C:\Users\User\OneDrive\OMK\omk
# Option A: Run compiled Node entry directly
node dist/cli/omk.js

# Option B: Link for global `omk` command
npm link
omk --help

# Option C: Python path (requires WSL or Git Bash)
python -m omk
```

## Verification Steps (always run after changes)

```bash
cd /mnt/c/Users/User/OneDrive/OMK/omk
./bin/omk status --json
./bin/omk history --days 7
./bin/omk models --days 7
./bin/omk sessions --limit 10
./bin/omk tree
./bin/omk export -f json -o /tmp/omk_test.json

# Agent mode tests
./bin/omk chat
# Type: /help, /tools, /quit
```

## Verification Steps (always run after changes)

```bash
cd /mnt/c/Users/User/OneDrive/OMK/omk
./bin/omk status --json
./bin/omk history --days 7
./bin/omk models --days 7
./bin/omk sessions --limit 10
./bin/omk tree
./bin/omk export -f json -o /tmp/omk_test.json

# v2.1 specific tests
./bin/omk auth
./bin/omk provider
./bin/omk mcp list
./bin/omk skill example-skill --prompt "test"
./bin/omk orchestrate --task "list files" --dry-run

# Agent mode tests
./bin/omk chat
# Type: /help, /tools, /provider, /orchestrate, /quit
```

## Duplicate Path Gotcha (v2.1)

OMK has **two copies** of monitoring code:
- `omk/monitoring/cli.py` — source of truth
- `omk/omk/monitoring/cli.py` — duplicate for import resolution

**Always sync after editing:**
```bash
cp omk/monitoring/cli.py omk/omk/monitoring/cli.py
```

If `python -m omk` loads stale code, check which `monitoring/cli.py` is being imported:
```python
import omk.monitoring.cli
print(omk.monitoring.cli.__file__)
```

Same applies to `omk/ui/` re-export modules.

## Python Path / Import Gotchas

OMK was previously installed as an editable package pointing to `~/.hermes/skills/openclaw-learnings/omk/`. If you get `ModuleNotFoundError` for `omk.metrics` or `omk.ui.colors`:

1. Check for stale editable installs:
```bash
ls ~/.local/lib/python*/site-packages/ | grep omk
```

2. Remove them:
```bash
rm -f ~/.local/lib/python*/site-packages/__editable__*omk*
rm -rf ~/.local/lib/python*/site-packages/omk-*.dist-info
```

3. Use the launcher script which sets `PYTHONPATH`:
```bash
./bin/omk <command>
# NOT: python3 -m omk (unless PYTHONPATH is set manually)
```

4. The `omk/ui/` and top-level re-export modules (`omk/metrics.py`, `omk/dashboard.py`, etc.) exist specifically to bridge imports between the new top-level package and the legacy `monitoring/` subdirectory.

## Inspecting the Live Schema

```python
import sqlite3
conn = sqlite3.connect('/home/user/.hermes/state.db')
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

# Get columns for sessions table
cursor.execute("PRAGMA table_info(sessions)")

# Check actual data types
cursor.execute("SELECT started_at, model FROM sessions LIMIT 3")
for row in cursor.fetchall():
    print(type(row[0]), repr(row[0]))  # Usually <class 'float'>
conn.close()
```

## Known Schema Fields (as of April 2026)

`sessions` table columns:
- `id TEXT PRIMARY KEY`
- `source TEXT` — NOT `platform` (old code may reference this)
- `started_at REAL NOT NULL` — Unix timestamp
- `ended_at REAL`
- `model TEXT`
- `input_tokens INTEGER DEFAULT 0`
- `output_tokens INTEGER DEFAULT 0`
- `estimated_cost_usd REAL`
- `message_count INTEGER DEFAULT 0`
- `tool_call_count INTEGER DEFAULT 0`
- `api_call_count INTEGER DEFAULT 0`

## Session Manager API

```python
from omk.session import Session, list_sessions, search_sessions, delete_session

# Create + save
s = Session(model="openrouter/auto", title="My session")
s.add_message("user", "Hello")
s.add_message("assistant", "Hi there")
s.save()

# Load
s2 = Session.load(s.id)

# List recent
sessions = list_sessions(limit=20)

# Search
sessions = search_sessions("error handling")

# Delete
delete_session(s.id)
```

## LLM Client API

```python
from omk.llm import create_client

client = create_client()
response = client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    tools=registry.get_schemas(),
)
# response = {"content": "...", "tool_calls": [...], "usage": {...}}
```

## Fix Patterns

### Fixing date formatting in views
```python
# Old (broken):
dt = datetime.fromisoformat(started.replace("Z", "+00:00"))

# New (fixed):
dt = datetime.fromtimestamp(float(started))
```

### Fixing duration calculation
```python
# Old (broken):
start_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
end_dt = datetime.fromisoformat(ended.replace("Z", "+00:00"))
duration = int((end_dt - start_dt).total_seconds())

# New (fixed):
duration = int(float(ended) - float(started))
```

### Fixing token metrics scope bug
```python
# Old (broken — session_count only exists inside inner try/except):
try:
    cursor.execute("SELECT SUM(...) ...")
    ...
except Exception:
    cursor.execute("SELECT COUNT(*) ...")
    session_count = cursor.fetchone()[0]  # Only defined in except block!

# New (fixed — single query, no nested try/except):
cursor.execute("""
    SELECT COALESCE(SUM(input_tokens), 0),
           COALESCE(SUM(output_tokens), 0),
           COALESCE(SUM(estimated_cost_usd), 0.0),
           COUNT(*)
    FROM sessions WHERE started_at > ?
""", (cutoff,))
row = cursor.fetchone()
session_count = row[3] or 0
```

### Conditional prompt_toolkit imports
```python
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

# Define classes ONLY when available
if PROMPT_TOOLKIT_AVAILABLE:
    class MyCompleter(Completer):
        ...
else:
    MyCompleter = None
```

## TUI Development (Ink / React Terminal UI)

OMK v2.1 includes a full **Ink (React for terminals)** TUI at `src/tui/` built alongside the Python backend. The TUI is the primary entry point for `npm install -g omk` users.

### Architecture

```
src/tui/
├── app.tsx              # Main App component — state, useInput, useApp
├── components/
│   ├── Footer.tsx       # Bottom shortcut bar
│   ├── MessageList.tsx  # Scrollable chat history
│   └── Welcome.tsx      # Onboarding screen
└── utils/
    └── clipboard.ts     # OSC52 clipboard escape sequences
```

### OSC52 Clipboard (Cross-Platform Terminal Copy)

Terminal emulators (iTerm2, Windows Terminal, VS Code, tmux) support OSC52 escape sequences for clipboard access without external dependencies:

```typescript
// src/utils/clipboard.ts
export function copyToClipboard(text: string): void {
  const data = Buffer.from(text, 'utf8').toString('base64');
  const osc52 = `\x1b]52;c;${data}\x07`;
  process.stdout.write(osc52);
}
```

Usage in a slash command handler:
```typescript
if (canonical === '/copy') {
  const lastResponse = messages.filter(m => m.role === 'assistant').pop();
  if (lastResponse) {
    copyToClipboard(lastResponse.content);
    setStatusMessage('Copied to clipboard via OSC52');
  }
}
```

**Limitations:**
- Works in most modern terminals but not all (e.g., bare Linux console)
- tmux requires `set -g set-clipboard on` in `~/.tmux.conf`
- Windows Terminal supports it natively as of v1.20+
- Always provide `/save` as a fallback (write to file)

### Scrollable Message History (PgUp/PgDown)

Ink's `useInput` doesn't have built-in scroll. Implement scroll state manually:

```typescript
const [scrollOffset, setScrollOffset] = useState(0);

useInput((input, key) => {
  if (key.pageUp) {
    setScrollOffset(prev => Math.max(0, prev - 5));
  } else if (key.pageDown) {
    setScrollOffset(prev => Math.min(messages.length - 1, prev + 5));
  } else if (key.return && !key.meta) {
    // Reset scroll on new message
    setScrollOffset(0);
  }
});

// In render: slice messages based on scroll
const visibleMessages = scrollOffset === 0
  ? messages
  : messages.slice(Math.max(0, messages.length - VISIBLE_COUNT - scrollOffset), messages.length - scrollOffset);
```

Show a scroll indicator:
```typescript
{scrollOffset > 0 && (
  <Text dimColor>-- scrolled back {scrollOffset} messages --</Text>
)}
```

### Mouse Support in Ink

Enable terminal mouse tracking on mount, disable on unmount:

```typescript
import { useEffect } from 'react';

useEffect(() => {
  // Enable mouse tracking (X10 + SGR + any-event)
  process.stdout.write('\x1b[?1000h\x1b[?1006h\x1b[?1015h');
  return () => {
    // Disable on exit
    process.stdout.write('\x1b[?1000l\x1b[?1006l\x1b[?1015l');
  };
}, []);
```

Note: Ink doesn't expose mouse events through `useInput`. For full mouse handling you'd need raw stdin parsing, which is complex. The escape sequence above is mainly for terminal emulators that support mouse scrolling natively.

### Slash Commands in TUI

Handle locally in `useInput` before sending to backend:

```typescript
useInput((input, key) => {
  if (input.startsWith('/')) {
    const canonical = input.trim().toLowerCase();

    if (canonical === '/help') {
      setShowHelp(true);
      return;
    }
    if (canonical === '/copy') {
      // ... copy last response
      return;
    }
    if (canonical === '/save') {
      const transcript = messages.map(m => `${m.role}: ${m.content}`).join('\n');
      fs.writeFileSync(`omk-session-${Date.now()}.txt`, transcript);
      setStatusMessage('Saved to file');
      return;
    }
    if (canonical === '/quit' || canonical === '/exit') {
      exit();
      return;
    }
    // Fall through to backend for unknown commands
  }
});
```

### Welcome / Onboarding Message

Show once on first launch, then suppress via config flag:

```typescript
const [showWelcome, setShowWelcome] = useState(() => {
  return !config.get('has_seen_welcome');
});

const dismissWelcome = () => {
  setShowWelcome(false);
  config.set('has_seen_welcome', true);
};
```

Content should include:
- Quick start examples (`Ask a question`, `Run /help`)
- Copy methods (`/copy`, `/save`, or Shift+select in terminal)
- Key shortcuts (Tab accept, Ctrl+C exit, PgUp/PgDn scroll)

### Footer UX Patterns

Keep the footer concise but informative. Prioritize:
1. Most-used commands (`/help`, `/copy`, `/save`)
2. Mode indicators (`Ctrl+X mode`)
3. Navigation (`PgUp/PgDn scroll`)
4. Exit shortcut (`Ctrl+C`)

```typescript
// Footer.tsx
<Text dimColor>
  /help | /copy | /save | Ctrl+X mode | Shift+Tab agents | PgUp/PgDn scroll | Tab accept | Ctrl+C exit
</Text>
```

For copy methods, add a second line:
```typescript
<Text dimColor>
  Copy: /copy = clipboard, /save = file, or Shift+select in terminal
</Text>
```

### Building and Testing TUI Changes

```bash
cd /mnt/c/Users/User/OneDrive/OMK/omk
npm run build        # Compile TypeScript → dist/
npm start            # Run the TUI directly
node dist/cli/omk.js # Run compiled output
```

**Common build errors:**
- `SyntaxError: Invalid or unexpected token` on `bin/omk` — Node.js is trying to parse the bash script. Ensure `package.json` `"bin"` points to `dist/cli/omk.js` not `bin/omk`.
- `Cannot find module` — run `npm install` first if `node_modules/` is missing.

### npm `bin` Field Gotcha (Windows)

**NEVER point `"bin"` to a shell script** in a cross-platform npm package. On Windows, npm generates `.cmd` wrappers that may spawn the file through Node.js, causing Node to try to parse bash as JavaScript:

```
file:///C:/.../omk/bin/omk:2
# OMK CLI launcher
^
SyntaxError: Invalid or unexpected token
```

**Correct `package.json`:**
```json
{
  "bin": {
    "omk": "./dist/cli/omk.js"
  }
}
```

**Wrong `package.json`:**
```json
{
  "bin": {
    "omk": "./bin/omk"
  }
}
```

## Skin Integration

OMK's `ui/colors.py` tries to import from Hermes skin engine. Path is hardcoded to `/mnt/c/Users/User/hermes-agent`. If Hermes moves, update:
```python
sys.path.insert(0, "/path/to/hermes-agent")
from hermes_cli.skin_engine import get_active_skin
```

## Keyboard Control in Live Monitor

The live monitor uses `rich.Live`. For real keyboard input without textual:
```python
import termios, tty, select, sys, threading

def _set_raw_mode():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    return old

def _restore_mode(old):
    termios.tcsetattr(fd, termios.TCSADRAIN, old)
```

Always run keyboard listener in a daemon thread and restore terminal settings in a `finally` block.

## Production Hardening (v2.1 → v2.1.1)

When QA reveals the codebase is structurally complete but not production-ready (~81/100 score), run this hardening pipeline:

### Phase 1: Core Production Files

Create these 5 files to reach Hermes parity:

| File | Purpose | Hermes Equivalent |
|------|---------|-------------------|
| `omk/agent/prompt_caching.py` | Anthropic cache_control blocks + hit/miss stats | `agent/prompt_caching.py` |
| `omk/agent/context_compressor.py` | Auto-summarize old messages, preserve recent N | `agent/context_compressor.py` |
| `omk/agent/model_metadata.py` | Context length registry, token estimator | `agent/model_metadata.py` |
| `omk/tools/approval.py` | Dangerous command detection + approval flow | `tools/approval.py` |
| `omk/batch_runner.py` | ThreadPoolExecutor parallel batch processing | `batch_runner.py` |

Plus patch `omk/auth/manager.py` to implement `_refresh_token()` for OAuth providers (Gemini uses `https://oauth2.googleapis.com/token`).

### Phase 2: Resilience + UX

| File | Improvement |
|------|-------------|
| `omk/mcp/client.py` | Retry logic (3x with backoff), health checker thread (30s), auto-reconnect |
| `omk/subagent/spawner.py` | Retry failed subagents (2x), timeout handling (300s default), attempt tracking in prompt |
| `omk/agent/display.py` | KawaiiSpinner animated faces, Rich activity feed, tool preview formatting |

### Phase 3: Test Suite (53 tests target)

```bash
cd /mnt/c/Users/User/OneDrive/OMK/omk
venv/bin/pip install pytest pytest-xdist
PYTHONPATH=/mnt/c/Users/User/OneDrive/OMK/omk venv/bin/python -m pytest tests/ -v --tb=short
```

Test structure:
- `tests/conftest.py` — fixtures for tmp_omk_home, mock_auth
- `tests/test_config.py` — 5 tests
- `tests/test_session.py` — 5 tests
- `tests/test_tools_registry.py` — 8 tests
- `tests/test_agent.py` — 5 tests
- `tests/test_auth.py` — 5 tests
- `tests/test_providers.py` — 5 tests (handle BaseProvider as abstract)
- `tests/test_orchestrator.py` — 5 tests
- `tests/test_skills.py` — 5 tests
- `tests/test_context.py` — 5 tests
- `tests/test_interactive.py` — 5 tests

**Iterative fixing pattern:** First run will fail with AttributeError (API mismatch). Read actual source files to find correct method names (e.g., `session.id` not `session.session_id`, `cm.get_messages()` not `cm.get_context()`), then patch tests. Repeat until 100% pass.

### OAuth Discovery from Existing CLI Tools

Before asking user for API keys, check if CLI tools are already configured:

```bash
# Kimi CLI
 cat /mnt/c/Users/User/.kimi/config.toml | grep api_key

# Gemini CLI
 cat /mnt/c/Users/User/.gemini/oauth_creds.json

# Codex CLI
 cat /mnt/c/Users/User/.codex/config.toml | grep -i token

# Hermes (fallback)
 cat /mnt/c/Users/User/.hermes/.env | grep API_KEY
 cat /mnt/c/Users/User/.hermes/auth.json | python3 -m json.tool | grep access_token
```

Mirror discovered credentials into `~/.omk/auth.json`:
```json
{
  "providers": {
    "kimi": { "auth_type": "api_key", "api_key": "...", "configured": true },
    "gemini": { "auth_type": "oauth", "access_token": "...", "refresh_token": "...", "configured": true },
    "codex": { "auth_type": "cli", "configured": true }
  }
}
```

**Pitfall:** CLI configs often show masked keys (`sk-L6C...llE5`). These are NOT usable. Get real keys from `~/.hermes/auth.json` credential_pool or ask user. The `.kimi/config.toml` file may contain the real key though — check carefully.

### Provider Routing Fix (v2.1 critical)

When `OMKAgent` is constructed with `provider=` or `model=` args (e.g. from CLI `--provider kimi --model moonshot-v1-8k`), `_init_provider()` must forward those overrides into `create_client()`. If you pass `self.config` directly, the on-disk config's provider/model will silently override the CLI args.

```python
# WRONG — ignores CLI overrides
self.client = create_client(self.config)
self.client.model = self.model

# CORRECT — pass overrides into client config
client_config = {
    **self.config,
    "provider": self.provider,
    "model": self.model,
}
# Also prevent api_base leak: if provider doesn't match config default,
# pop api_base so LLMClient falls back to _default_base()
if self.provider != self.config.get("provider", "openrouter"):
    client_config.pop("api_base", None)
self.client = create_client(client_config)
```

**File:** `omk/agent/core.py` — `_init_provider()`

### Auth Manager Dual-Format Support (v2.1 critical)

`~/.omk/auth.json` may contain either:
- **Legacy format:** `{"tokens": {"openrouter": {"access_token": "..."}}}`
- **Hermes-synced format:** `{"providers": {"openrouter": {"auth_type": "api_key", "api_key": "..."}}}`

`AuthManager._load()` must read **both** or credentials will be silently invisible.

```python
def _load(self) -> None:
    ...
    data = json.load(f)
    # Legacy format
    for provider, token_data in data.get("tokens", {}).items():
        self._tokens[provider] = AuthToken(**token_data)
    # New Hermes-synced format
    for provider, prov_data in data.get("providers", {}).items():
        if prov_data.get("auth_type") == "api_key":
            self._tokens[provider] = AuthToken(
                provider=provider,
                access_token=prov_data.get("api_key", ""),
            )
        elif prov_data.get("auth_type") == "oauth":
            self._tokens[provider] = AuthToken(
                provider=provider,
                access_token=prov_data.get("access_token", ""),
                refresh_token=prov_data.get("refresh_token"),
            )
```

**File:** `omk/auth/manager.py` — `_load()`

### `.env` Auto-Loading (v2.1 critical)

OMK does **not** load `~/.omk/.env` by default. You must add `_load_dotenv()` and call it from `load_config()`, or env vars like `OPENROUTER_API_KEY` won't be available and the LLM client will get `None` for `api_key`.

```python
def _load_dotenv() -> None:
    """Load environment variables from ~/.omk/.env if it exists."""
    env_file = get_omk_home() / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value

def load_config() -> Dict[str, Any]:
    _load_dotenv()  # MUST call before returning config
    ...
```

**File:** `omk/config.py`

### LLM Client Auth Fallback (v2.1 critical)

`LLMClient.__init__()` calls `omk.config.get_api_key()` which only checks env vars. It must **also** fall back to `AuthManager.get_api_key()` which reads `~/.omk/auth.json`.

```python
if not self.api_key:
    from omk.config import get_api_key
    self.api_key = get_api_key(provider)
    if not self.api_key:
        try:
            from omk.auth.manager import get_auth_manager
            self.api_key = get_auth_manager().get_api_key(provider)
        except Exception:
            pass
```

**File:** `omk/llm.py` — `LLMClient.__init__()`

### Hyphenated Provider Env Vars

`get_api_key("kimi-code")` would generate `KIMI-CODE_API_KEY` (invalid env var name). Use an explicit key_map plus `replace('-', '_')` fallback.

```python
key_map = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "moonshot": "MOONSHOT_API_KEY",
    "kimi": "KIMI_API_KEY",
    "kimi-code": "KIMI_CODE_API_KEY",
    "gemini": "GEMINI_API_KEY",
}
env_var = key_map.get(provider, f"{provider.upper().replace('-', '_')}_API_KEY")
```

**Files:** `omk/config.py`, `omk/auth/manager.py`

### HuggingFace Pro Integration ($2/day Serverless)

HF Pro ($9/month) gives $2/day in Serverless Inference API credits. Integration pattern:

```python
# config.py — add HF provider
PROVIDERS = {
    "huggingface": {
        "base_url": "https://api-inference.huggingface.co/v1",
        "env_var": "HF_TOKEN",
        "models": [
            "meta-llama/Llama-3.1-8B-Instruct",
            "meta-llama/Llama-3.2-3B-Instruct",
            "microsoft/Phi-4-mini-instruct",
        ],
    },
}

# auth/manager.py — HF token validation
def validate_hf_token(token: str) -> bool:
    """Check if HF token has inference.serverless.write permission."""
    resp = requests.get(
        "https://huggingface.co/api/whoami-v2",
        headers={"Authorization": f"Bearer {token}"}
    )
    data = resp.json()
    # Check isPro and inference permissions
    return data.get("isPro", False) and "inference.serverless.write" in str(data)
```

**Pitfall:** HF has multiple endpoints:
- `api-inference.huggingface.co` — Serverless (Pro)
- `router.huggingface.co` — Router (multi-provider, not HF-specific)
- Direct model endpoint — `https://api-inference.huggingface.co/models/<model-id>`

For chat completions format, use the v1 endpoint with OpenAI-compatible format:
```python
response = requests.post(
    "https://api-inference.huggingface.co/v1/chat/completions",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [{"role": "user", "content": "Hello"}],
    }
)
```

**HF Pro Quota Tracking:**
```python
# After each call, track usage against $2/day limit
HF_PRO_DAILY_LIMIT = 2.0  # USD
usage_today = auth_manager.get_daily_usage("huggingface")
remaining = HF_PRO_DAILY_LIMIT - usage_today
if remaining < 0.1:
    logger.warning("HF Pro quota nearly exhausted, switching to fallback")
```

### Kimi Temperature Restriction

Kimi/Moonshot API rejects `temperature` values other than `1.0` for most models. Always force it:

```python
kwargs = {
    "model": self.model,
    "messages": messages,
    "temperature": self.temperature,
    "stream": stream,
}
if self.provider in ("kimi", "kimi-code", "moonshot"):
    kwargs["temperature"] = 1.0
```

**File:** `omk/llm.py` — `LLMClient.chat()`

### `OMK_HOME` Must Be Set

Without `OMK_HOME`, `get_omk_home()` falls back to `Path.home() / ".omk"` which in WSL is `/home/user/.omk` — **not** the Windows path where auth.json lives. Set it explicitly:

```bash
export OMK_HOME=/mnt/c/Users/User/.omk
```

Add to `~/.bashrc` or `~/.profile` for persistence.

### Moonshot Base URL Fix

If Kimi returns 401 AuthenticationError, the base URL may be wrong:
```python
# WRONG (old CN endpoint)
"kimi": "https://api.moonshot.cn/v1"

# CORRECT (global endpoint)
"kimi": "https://api.moonshot.ai/v1"
"kimi-code": "https://api.kimi.com/coding/v1"
```

### QA Verification Checklist (real API keys)

After applying all fixes above, verify with real providers:

```bash
export OMK_HOME=/mnt/c/Users/User/.omk

cd /mnt/c/Users/User/OneDrive/OMK/omk

# OpenRouter (default)
./bin/omk run --prompt "Say hi in Thai, one word"
# Expected: สวัสดี

# Kimi / Moonshot
./bin/omk run --provider kimi --model moonshot-v1-8k --prompt "Say hi in Thai, one word"
# Expected: สวัสดี

# Full test suite
venv/bin/pytest tests/ -q
# Expected: 53 passed
```

If any step fails:
1. Check `OMK_HOME` is exported
2. Check `~/.omk/auth.json` exists and has real (not masked) keys
3. Check `~/.omk/.env` has `OPENROUTER_API_KEY` or `KIMI_API_KEY`
4. Add `print()` debug to `LLMClient.__init__()` to verify `self.api_key` is not None
5. Add `print()` debug to `AuthManager._load()` to verify tokens dict is populated

### Production Readiness Scorecard

| Score | Status | Action |
|-------|--------|--------|
| < 70 | Alpha | Add missing core modules |
| 70–85 | Beta | Run hardening pipeline above |
| 85–95 | Production-ready | Setup real API keys, test end-to-end |
| > 95 | Polished | Add gateway, skin engine, advanced features |

## Token Optimization Audit & External Tool Integration

OMK's context manager (`omk/context/manager.py`) is basic compared to Hermes' `ContextCompressor` (1,276 lines). Here's the gap analysis and integration roadmap.

### Hermes Token Features (April 2026)

Hermes Agent now has these token optimization features (implemented April 2026):

#### CJK Token Estimation (`agent/token_utils.py`)
- English: ~4 chars/token
- Thai/CJK: ~2 chars/token
- Messages overhead: +4 tokens
- Functions: `estimate_tokens()`, `get_script_breakdown()`

#### Token Dashboard (`agent/token_dashboard.py`)
- Tracks per-session: input, output, tool, context tokens
- Tracks compression savings
- Tracks cost estimation
- Methods: `add_turn()`, `get_aggregate_stats()`, `export_json()`

#### Caveman Skill (`~/.hermes/skills/caveman/SKILL.md`)
- Terse output mode
- Pattern: `[thing] [action] [reason]. [next step].`
- Saves ~25-73% tokens per response
- Load with: `/skill caveman`

#### /tokens Command
- Slash command in Hermes CLI
- Shows full token dashboard
- Flags: `--history` for turn breakdown
- Shows CJK breakdown of last message

#### Integration Points
- `run_agent.py`: `_token_dashboard` initialized in `__init__`
- Every API call: `dashboard.add_turn(...)`
- Compression: tracks savings automatically
- CLI: `_show_tokens()` handler

### What OMK Has Now

| Feature | OMK | Hermes |
|---------|-----|--------|
| Context compression | Sliding window (naive) | LLM-based structured summarization |
| Tool output pruning | ❌ | ✅ Per-tool 1-line summaries |
| Deduplication | ❌ | ✅ Hash-based |
| Head/tail protection | ❌ Fixed count | ✅ Token-budget |
| Anti-thrashing | ❌ | ✅ Cooldown + savings tracking |
| Prompt caching | ❌ | ✅ Anthropic cache_control |
| Model context registry | ❌ | ✅ Dynamic probing |
| Token estimation | chars/4 (wrong for CJK) | Provider-specific |
| Token dashboard | ✅ | ✅ (parity) |
| CJK estimation | ✅ | ✅ (parity) |
| Caveman skill | ✅ | ✅ (parity) |

### External Tools Researched

| Tool | Core Idea | Impact | Effort for OMK |
|------|-----------|--------|----------------|
| **caveman** | Terse output style (caveman speak) | ~75% output tokens | ⭐ Skill only |
| **context-mode** | Sandbox tool output outside context | 315KB→5.4KB (98%) | ⭐⭐⭐⭐ MCP-like |
| **claude-token-optimizer** | Essential docs only at session start | 11K→1.3K (90%) | ⭐⭐⭐ Docs structure |
| **token-savior** | Symbol-based code navigation | 97% fewer chars | ⭐⭐⭐⭐⭐ AST+index |
| **token-optimizer** | Live dashboard for token/cost | Measurement | ⭐⭐⭐ Extend metrics |

### Quick Win: caveman Skill

Create `~/.omk/skills/caveman/SKILL.md`:
```markdown
---
name: caveman
description: Ultra-compressed communication mode
---
Respond terse like smart caveman. All technical substance stay. Only fluff die.
Drop: articles, filler, pleasantries, hedging.
Pattern: [thing] [action] [reason]. [next step].
```
Activate: `omk chat` then `/skill caveman` or `omk run --skill caveman --prompt "..."`

### Integration Priority (Implemented)

All 7 items below are implemented, integrated into agent core, and tested (53 tests pass):

| # | Feature | File | Status |
|---|---------|------|--------|
| 1 | caveman skill | `~/.omk/skills/caveman/SKILL.md` | ✅ Done |
| 2 | CJK-aware token estimation | `omk/token_utils.py` | ✅ Done |
| 3 | Tool output pruning | `omk/context/compressor.py` | ✅ Done |
| 4 | ContextCompressor | `omk/context/compressor.py` | ✅ Done |
| 5 | Model metadata registry | `omk/agent/model_metadata.py` | ✅ Done |
| 6 | Prompt caching | `omk/prompt_caching.py` | ✅ Done |
| 7 | Token dashboard | `omk/token_dashboard.py` | ✅ Done |
| 8 | Agent core integration | `omk/agent/core.py` | ✅ Done |

### Agent Core Integration Pattern

The `OMKAgent._run_direct()` loop rebuilds messages **every iteration** so compression and cache control stay current as context grows:

```python
def _run_direct(self, user_message: str) -> str:
    # ... add user msg ...
    while self.iteration_count < self.max_iterations:
        self.iteration_count += 1

        tokens_before = self.context_manager.get_token_count()

        # Build messages (auto-compress + cache control)
        messages = self._build_messages()

        compression_happened = self.context_manager.get_token_count() < tokens_before

        # Call LLM ...
        response = self.client.chat(messages=messages, tools=tools)

        # Track on dashboard
        self.token_dashboard.add_turn(
            input_tokens=response["usage"]["prompt_tokens"],
            output_tokens=response["usage"]["completion_tokens"],
            tool_calls=len(response.get("tool_calls", [])),
            compression=compression_happened,
        )
        # ... rest of loop ...
```

`_build_messages()` delegates to `ContextManager`:
```python
def _build_messages(self) -> List[Dict[str, str]]:
    messages = [{"role": "system", "content": self.system_prompt}]

    # Skill prompts
    for skill_name in getattr(self, '_active_skills', []):
        skill = self.skill_manager.get_skill(skill_name)
        if skill:
            messages.append({"role": "system", "content": skill.get_prompt()})

    # Context with auto-compression
    ctx_messages = self.context_manager.get_messages(compress=True)

    # Anthropic cache_control for Claude models only
    if "claude" in self.model.lower():
        from omk.prompt_caching import apply_anthropic_cache_control
        ctx_messages = apply_anthropic_cache_control(ctx_messages)

    messages.extend(ctx_messages)
    return messages
```

**Key methods added to OMKAgent:**
- `get_token_summary()` → human-readable string from dashboard
- `end_session()` → save + return dashboard summary
- `get_stats()` → now includes `"dashboard"` key

### Context Compression Pipeline Architecture

The `ContextCompressor` in `omk/context/compressor.py` uses a **two-phase** approach:

```
messages → Phase 1: Tool Pruning (cheap, no LLM) → Phase 2: LLM Summarize (if still over budget)
```

**Phase 1 — Tool Pruning:**
- Only fires when `len(messages) > protect_first_n + protect_last_n` (default: 3 + 6 = 9)
- Replaces old tool results with per-tool 1-line summaries
- Protects first N and last N messages from pruning

**Phase 2 — LLM Summarization:**
- Splits messages into head, middle, tail
- Attempts LLM-based summary of middle messages (falls back to naive concat if no client)
- Wraps summary with `SUMMARY_PREFIX` to prevent model from treating it as active instructions

**Anti-thrashing:**
- Tracks savings percentage per compression
- If last 2 compressions saved <10% each, skips compression for a cooldown period
- Prevents infinite compress→expand loops

**Integration into ContextManager:**
```python
from omk.context.manager import ContextManager

ctx = ContextManager(max_tokens=100000, model="gpt-4o")
ctx.add_message("system", "You are helpful.")
# ... add many messages ...

# Auto-compress when getting messages for LLM
messages = ctx.get_messages(compress=True)

# Or force compress
compressed = ctx.compress()

# Apply Anthropic cache_control (only for Claude models)
cached = ctx.apply_cache_control(provider="anthropic")
```

### CJK-Aware Token Estimation

`omk/token_utils.py` implements heuristic-based estimation without requiring tiktoken:

```python
from omk.token_utils import estimate_tokens, estimate_messages_tokens

# English: ~4 chars/token
estimate_tokens("Hello world")  # ~3 tokens

# Thai/CJK: ~2 chars/token
estimate_tokens("สวัสดีครับ")  # ~7 tokens (not 4!)

# Mixed: weighted average
estimate_tokens("Hello สวัสดี")  # ~5 tokens

# Full messages with overhead
msgs = [{"role": "user", "content": "Hello"}]
estimate_messages_tokens(msgs, model="gpt-4o")  # ~7 tokens (includes fmt overhead)
```

**Key heuristic:**
- ASCII/English: 1 token per 4 chars
- Thai, CJK, emoji: 1 token per 1.5-2 chars
- Mixed: weighted by character class ratio
- Messages overhead: +4 tokens per message for format/role

### Prompt Caching (Anthropic-only)

`omk/prompt_caching.py` adds `cache_control` breakpoints:

```python
from omk.prompt_caching import apply_anthropic_cache_control

messages = [
    {"role": "system", "content": "Long system prompt..."},
    {"role": "user", "content": "Q1"},
    {"role": "assistant", "content": "A1"},
    # ... many turns ...
    {"role": "user", "content": "Q10"},
]

cached = apply_anthropic_cache_control(messages)
# System prompt gets cache_control: {"type": "ephemeral"}
# Last 3 non-system messages also get cache_control
```

**Important:** Only applies when `model` contains "claude" or provider is "anthropic". Other models skip silently.

### Token Dashboard

`omk/token_dashboard.py` tracks usage per session:

```python
from omk.token_dashboard import get_dashboard

d = get_dashboard()
d.start_session("sess-123", "gpt-4o", "openai")
d.add_turn(input_tokens=1000, output_tokens=500, tool_calls=2, compression=True)
print(d.display_current())
# Session: sess-123...
# Input:  1,000 tokens
# Output: 500 tokens
# Cost:   ~$0.0075

summary = d.end_session()
```

### Tool Summary Patterns

The compressor generates per-tool summaries:

| Tool | Summary Format |
|------|---------------|
| `terminal` | `[terminal] ran \`cmd\` -> exit N, L lines` |
| `read_file` | `[read_file] read path from line N (C chars)` |
| `write_file` | `[write_file] wrote path (C chars)` |
| `search_files` | `[search_files] 'pattern' -> L lines result` |
| `patch` | `[patch] path (C chars result)` |
| `web_search` | `[web_search] 'query' (C chars)` |
| `delegate_task` | `[delegate_task] 'goal...' (C chars)` |
| `execute_code` | `[execute_code] (L lines output)` |

### Gotcha: Tool Pruning Requires Enough Messages

Tool pruning in `_prune_tool_results()` has this guard:
```python
if len(messages) <= self.protect_first_n + self.protect_last_n:
    return messages  # No pruning — not enough messages
```

**If your test has only 5-7 messages, pruning won't fire.** Use 10+ messages in tests.

### Gotcha: Cache Control Test Needs Claude Model

`ctx.apply_cache_control(provider="anthropic")` checks the **model name** too:
```python
if self.model and "claude" not in self.model.lower():
    return list(self.messages)  # Skip — not a Claude model
```

Use `model="claude-sonnet-4"` in tests, not `model="gpt-4o"`.

### Gotcha: Token Dashboard 'total_tokens'

`end_session()` returns the session dict. `total_tokens` is **not** a field — compute it:
```python
summary = d.end_session()
total = summary['input_tokens'] + summary['output_tokens']  # Compute manually
```

`get_aggregate_stats()` does include `total_tokens` pre-computed.

### Gotcha: ContextManager.get_messages(compress=True) Does NOT Mutate

`get_messages(compress=True)` returns a **new list** when compression fires, but `ContextManager.messages` remains unchanged. The agent's `_build_messages()` uses the compressed list for the LLM call only. On next iteration, `messages` is rebuilt from the original (uncompressed) `ContextManager.messages`, so tool results are still available for pruning again if needed.

### Gotcha: Anti-Thrashing Backoff

If the compressor saves <10% for 2 consecutive compressions, it skips compression for a cooldown period. This prevents infinite compress→expand loops but can surprise you in tests:
```python
c = ContextCompressor(model="gpt-4o", max_tokens=1000)
c.compress(small_messages)  # saves 5%
c.compress(small_messages)  # saves 3% → ineffective_count=2
c.compress(small_messages)  # SKIPPED even though over budget!
```

Reset by creating a new compressor instance, or set `max_tokens` much lower to force meaningful savings.

### Gotcha: CJK Token Estimation Assertions

`estimate_tokens()` returns integers with comma formatting in dashboard, but raw ints in code:
```python
# In code: raw int
assert stats["input_tokens"] == 3000

# In display string: with comma
assert "3,000" in summary
```

### Gotcha: `/model` Must Re-init Provider

Don't just set `self.agent.model = new_model` — the old client's base URL and auth may be wrong for the new model. Always call `switch_provider()`:
```python
# WRONG — client still points to old provider's API base
self.agent.model = "gpt-4o"

# CORRECT — re-creates client with new model + restarts dashboard
self.agent.switch_provider(self.agent.provider, "gpt-4o")
self.agent.token_dashboard.start_session(
    session_id=self.agent.session.id,
    model="gpt-4o",
    provider=self.agent.provider,
)
```

### Changing Default Provider/Model

To change OMK's default brain (e.g., switch from OpenRouter to Kimi):

1. **Update `omk/config.py` DEFAULT_CONFIG:**
```python
DEFAULT_CONFIG = {
    "provider": "kimi",
    "model": "moonshotai/kimi-k2.6",
    "api_base": "https://api.moonshot.ai/v1",
    "context_window": 1000000,
    # ...
}
```

2. **Update fallback defaults in `omk/agent/core.py`:**
```python
self.model = model or self.config.get("model", "moonshotai/kimi-k2.6")
self.provider = provider or self.config.get("provider", "kimi")
```

3. **Adjust tests in `tests/test_config.py`:**
```python
def test_config_model_default():
    cfg = load_config()
    assert cfg.get("model") == DEFAULT_CONFIG["model"]
    assert "kimi" in DEFAULT_CONFIG["model"]  # verify default changed

def test_config_provider_default():
    cfg = load_config()
    assert cfg.get("provider") == DEFAULT_CONFIG["provider"]
    assert DEFAULT_CONFIG["provider"] == "kimi"
```

4. **Remove stale user config** (critical — existing `~/.omk/config.json` overrides DEFAULT_CONFIG):
```bash
rm ~/.omk/config.json
```

5. **Verify:**
```bash
cd /mnt/c/Users/User/OneDrive/OMK/omk
python -m pytest tests/test_config.py -q
```

**Gotcha:** If tests fail with old values (`openrouter/auto` vs new `moonshotai/kimi-k2.6`), the user's `~/.omk/config.json` is overriding DEFAULT_CONFIG. Delete it and re-run.

### CLI Prompt Showing Provider/Model

Show current brain in the REPL prompt:

```python
def _prompt_text(self) -> str:
    if not self.agent:
        return "🦾 omk> "
    prov = self.agent.provider
    mdl = self.agent.model.split("/")[-1][:18]
    return f"🦾 {prov}/{mdl}> "
```

Result:
```
🦾 kimi/kimi-k2.6> hello
🦾 openrouter/claude-opus> write tests
🦾 codex/gpt-5> refactor
```

### CLI Integration Patterns

#### Token Summary After Each Turn

In `omk/interactive.py`, `_handle_chat()` calls `get_token_summary()` after every response:

```python
def _handle_chat(self, message: str) -> None:
    response = self.agent.chat(message)
    if response:
        self.print(response, markdown=True)

    # Show token summary after each turn
    summary = self.agent.get_token_summary()
    if summary and "No active session" not in summary:
        if self.console:
            from rich.panel import Panel
            self.console.print(Panel(summary, title="📊 Tokens", border_style="dim"))
        else:
            self.print(f"\n{summary}")
```

#### `/route` Quick-Switch Command

Add preset provider+model combinations for one-command switching:

#### Token Summary After Each Turn

In `omk/interactive.py`, `_handle_chat()` calls `get_token_summary()` after every response:

```python
def _handle_chat(self, message: str) -> None:
    response = self.agent.chat(message)
    if response:
        self.print(response, markdown=True)

    # Show token summary after each turn
    summary = self.agent.get_token_summary()
    if summary and "No active session" not in summary:
        if self.console:
            from rich.panel import Panel
            self.console.print(Panel(summary, title="📊 Tokens", border_style="dim"))
        else:
            self.print(f"\n{summary}")
```

#### `/route` Quick-Switch Command

Add a `/route` slash command for one-command provider+model switching:

```python
PRESETS = {
    "kimi":       ("kimi",       "moonshotai/kimi-k2.6"),
    "kimi-lite":  ("kimi",       "moonshotai/kimi-k2.5"),
    "kimi-code":  ("kimi",       "kimi-code/kimi-for-coding"),
    "codex":      ("codex",      "gpt-5"),
    "gemini":     ("gemini",     "gemini-2.5-pro"),
    "claude":     ("openrouter", "anthropic/claude-sonnet-4"),
    "opus":       ("openrouter", "anthropic/claude-opus-4.6"),
    "gpt4o":      ("openrouter", "openai/gpt-4o"),
    "gpt4o-mini": ("openrouter", "openai/gpt-4o-mini"),
    "deepseek":   ("openrouter", "deepseek/deepseek-chat"),
    "auto":       ("openrouter", "openrouter/auto"),
    "openrouter": ("openrouter", "openrouter/auto"),
    "moonshot":   ("kimi",       "moonshotai/kimi-k2.6"),
}

if len(parts) > 1:
    preset = parts[1].lower()
    if preset in PRESETS:
        provider, model = PRESETS[preset]
        self.agent.switch_provider(provider, model)
        self.agent.token_dashboard.start_session(
            session_id=self.agent.session.id,
            model=model,
            provider=provider,
        )
        self.print(f"Routed to: {provider} / {model}", style="green")
else:
    self.print("Presets:", style="cyan")
    for name, (prov, mdl) in PRESETS.items():
        marker = " ★" if name == "kimi" else ""  # mark default
        self.print(f"  {name:15} → {prov:12} / {mdl}{marker}")
```

Usage in CLI:
```
🦾 kimi/kimi-k2.6> /route opus       ← switch to Claude Opus
🦾 openrouter/claude-opus> /route    ← show all presets
```

#### `/provider` and `/model` Must Restart Dashboard

When switching provider or model, restart the token dashboard so tracking stays accurate:

```python
if canonical == "/provider":
    provider = parts[1]
    model = parts[2] if len(parts) > 2 else None
    self.agent.switch_provider(provider, model)
    self.agent.token_dashboard.start_session(
        session_id=self.agent.session.id,
        model=self.agent.model,
        provider=provider,
    )
```

Same for `/model`:
```python
self.agent.switch_provider(self.agent.provider, model)
self.agent.token_dashboard.start_session(
    session_id=self.agent.session.id,
    model=model,
    provider=self.agent.provider,
)
```

#### `/tokens` Dashboard Display

Use the dashboard's formatted display instead of raw stats:

```python
if canonical == "/tokens":
    summary = self.agent.get_token_summary()
    if self.console:
        from rich.panel import Panel
        self.console.print(Panel(summary, title="📊 Token Usage", border_style="cyan"))
    else:
        self.print(summary)

    # Show aggregate across all sessions
    agg = self.agent.token_dashboard.get_aggregate_stats()
    if agg.get("sessions", 0) > 1:
        self.print(f"All sessions: {agg['total_tokens']:,} tokens, ~${agg['total_cost_usd']:.4f}", style="dim")
```

After implementing context features, verify with this script:

```python
from omk.agent.core import OMKAgent

# 1. Dashboard init
agent = OMKAgent(model="gpt-4o", provider="openrouter", max_context=2000, use_orchestrator=False)
assert agent.token_dashboard.get_current_stats()["model"] == "gpt-4o"

# 2. Claude cache control
agent2 = OMKAgent(model="claude-sonnet-4", provider="anthropic", max_context=2000, use_orchestrator=False)
for i in range(4):
    agent2.context_manager.add_message("user", f"Q{i}")
    agent2.context_manager.add_message("assistant", f"A{i}")
msgs = agent2._build_messages()
assert any("cache_control" in str(m) for m in msgs)

# 3. Tool pruning (needs 10+ messages)
from omk.context.compressor import ContextCompressor
c = ContextCompressor(model="gpt-4o", max_tokens=1000)
big = []
for i in range(20):
    big.append({"role": "user", "content": f"Q{i}: " + "word " * 200})
    big.append({"role": "assistant", "content": f"A{i}: " + "ok " * 200})
compressed = c.compress(big)
assert any("[CONTEXT COMPACTION" in str(m.get("content","")) for m in compressed)

# 4. CJK token estimation
from omk.token_utils import estimate_tokens
assert estimate_tokens("Hello world") < estimate_tokens("สวัสดีครับ")  # Thai costs more
```

### Key Insight from context-mode

> "Stop treating the LLM as a data processor, treat it as a code generator."

Instead of reading 50 files into context to count functions, have the agent write a script that counts and logs only the result. One script replaces ten tool calls.

### Full Stack Vision

```
[User Input]
    ↓
Session Start Optimization (essential docs only)
    ↓
[Agent Loop]
    ↓
Tool Output → Sandbox / Pruning
    ↓
Context Compression (Hermes-style)
    ↓
Prompt Caching (Anthropic)
    ↓
LLM Response → caveman style (if enabled)
    ↓
Token Dashboard
```

### Reference Files in OMK Repo

After running this audit, save these reports in the repo:
- `QA_REPORT_v2.1.md` — provider routing, auth, API key fixes
- `TOKEN_OPTIMIZATION_AUDIT.md` — gap analysis + integration roadmap
- `CODING.md` — behavioral guidelines (Karpathy-inspired)

## Cron Jobs with Local Models (ollama-local, llama.cpp, etc.)

When using slow local models (~3 min/response) for overnight batch processing:

### Pattern: Nightly Batch Narrative Generation

```python
# /home/user/.hermes/scripts/nightly_batch.py
import sys
from pathlib import Path

# Hermes Agent lives on Windows drive, venv is Windows Python (.exe)
# Must create temp Linux venv with dependencies
HERMES_AGENT = Path("/mnt/c/Users/User/hermes-agent")
sys.path.insert(0, str(HERMES_AGENT))

from run_agent import AIAgent

def generate_narrative(agent, prompt_template, news_context, style_name):
    prompt = prompt_template.format(news_content=news_context)
    return agent.chat(prompt)

# Agent config for slow local models
agent = AIAgent(
    provider="ollama-local",
    model="gemma4:e4b",  # or any local model
    max_iterations=2,    # limit to prevent overnight runaway
    quiet_mode=True,   # no interactive output
)
```

### Critical Setup Steps

1. **Create temp Linux venv** (Hermes venv is Windows Python .exe):
```bash
python3 -m venv /tmp/hermes-run-venv
/tmp/hermes-run-venv/bin/pip install python-dotenv openai anthropic \
    httpx rich tenacity pyyaml requests jinja2 pydantic prompt_toolkit
```

2. **Verify ollama-local responds** before scheduling:
```bash
curl -s http://localhost:11434/api/tags | python3 -m json.tool
```

3. **Use background process with notify** for long runs:
```bash
cd /mnt/c/Users/User/hermes-agent && \
  /tmp/hermes-run-venv/bin/python /home/user/.hermes/scripts/nightly_batch.py \
  > /tmp/nightly_batch.log 2>&1
```

### WSL Venv Detection Gotcha

Hermes Agent's venv at `/mnt/c/Users/User/hermes-agent/venv/` contains **Windows Python** (`Scripts/python.exe`). This cannot be executed from WSL directly — it tries to open Windows paths:

```
python.exe: can't open file 'C:\home\user\.hermes\scripts\...': [Errno 2]
```

**Detection logic:**
```python
VENV_PYTHON = HERMES_AGENT / "venv" / "Scripts" / "python.exe"
if VENV_PYTHON.exists():
    # This is Windows Python — DON'T use from WSL
    # Create /tmp/hermes-run-venv instead
```

**Correct approach:** Always create a separate WSL venv for cron scripts that import Hermes modules. Don't try to reuse the Windows venv.

**PEP 668 note:** WSL Ubuntu 24.04 has `externally-managed-environment` enabled. `pip install` without venv will fail. Always use `python3 -m venv`.

### Cron Job Script Wrapper Pattern

Hermes cron jobs expect scripts in `~/.hermes/scripts/` but the script needs a specific Python interpreter. Create a bash wrapper:

```bash
#!/bin/bash
# ~/.hermes/scripts/run_nightly_batch.sh
VENV_PYTHON="/tmp/hermes-run-venv/bin/python"
SCRIPT="/home/user/.hermes/scripts/nightly_batch.py"

cd /mnt/c/Users/User/hermes-agent || exit 1
exec "$VENV_PYTHON" "$SCRIPT" "$@"
```

Then register the wrapper as the cron job script:
```bash
hermes cron create "nightly-news" \
  --schedule "0 2 * * *" \
  --script "run_nightly_batch.sh"
```

The `script` field must be a filename relative to `~/.hermes/scripts/`, not an absolute path.

### Gemma 4 via Ollama-Local for Thai Content

**Verified working configuration (May 2026):**
- Model: `gemma4:e4b` via ollama-local provider
- Context: 131,072 tokens — useful for long-form Thai narrative generation
- Speed: ~4 minutes per ~2,500-2,700 char response
- Quality: Good for all 3 styles (Standard News, Friend-to-Friend, Expert Deep Dive)

**Prompt constraints for TTS-ready output:**
```
CRITICAL RULES:
1. ห้ามมีคำนำหรือคำลงท้าย: เริ่มรันเนื้อหา [SCRIPT] ทันที
2. บทพูดภาษาพูดล้วนๆ (PURE SPOKEN LANGUAGE)
3. ห้ามใส่วงเล็บและเลขอ้างอิง
4. ห้ามใส่คำแนะนำสำหรับคนพากย์ ห้ามใส่ Sound Effect
```

**Post-process to clean remaining artifacts:**
```python
import re

def clean_for_tts(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'#{1,6}\s*คำแนะนำ.*?(?=---|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'\*\*💡.*?(?=---|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'\[SCRIPT\]\s*', '', text)
    return text.strip()
```

### Cron Job Registration (Hermes)

```bash
hermes cron create "nightly-news" \
  --schedule "0 2 * * *" \
  --script "run_nightly_batch.sh"
```

**Important:** The `script` field must be a filename relative to `~/.hermes/scripts/`, not an absolute path. The script can be a bash wrapper that calls the actual Python script with the correct interpreter.

**See also:** `references/nightly-news-narrative-session.md` for a complete worked example with gemma4:e4b generating Thai TTS-ready narratives.

### Prompt Engineering for TTS-Ready Output

When generating spoken content from local models, add these constraints:
- `PURE SPOKEN LANGUAGE` — no stage directions
- `ห้ามใส่วงเล็บ` — prevents bracket reading in TTS
- `ห้ามมีคำนำหรือคำลงท้าย` — no meta-commentary
- Post-process with regex to strip any remaining `[text]` or `(text)`

**Post-processing for Thai content (gemma4:e4b):**
```python
import re

def clean_for_tts(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'#{1,6}\s*คำแนะนำ.*?(?=---|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'\*\*💡.*?(?=---|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'\[SCRIPT\]\s*', '', text)
    return text.strip()
```

Gemma 4 still produces meta-sections like "คำแนะนำในการนำไปใช้" and "💡 ข้อแนะนำเพิ่มเติม" despite prompt constraints. Always run post-processing.

### Timeout Considerations

| Model Speed | 1 Response | 3 Styles | With Retry |
|-------------|-----------|----------|------------|
| 30 sec | 30 sec | 1.5 min | 2 min |
| 3 min | 3 min | 9 min | 12 min |
| 10 min | 10 min | 30 min | 40 min |

Set cron schedule with buffer: if generation takes ~15 min, schedule at 02:00 to finish by 02:30.

### Post-Generation Processing

```python
import re

def clean_for_tts(text):
    # Remove stage directions
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    # Remove meta sections
    text = re.sub(r'#{1,6}\s*คำแนะนำ.*?(?=---|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'\*\*💡.*?(?=---|$)', '', text, flags=re.DOTALL)
    return text.strip()
```

## Pitfalls

1. **Don't assume ISO timestamps** — Hermes state.db uses REAL Unix timestamps.
2. **Don't reference `platform` column** — it's `source` in the actual schema.
3. **Don't nest try/except for SQL fallback** — it creates scope bugs.
4. **Always verify with real data** — run the actual CLI commands, don't just check syntax.
5. **Live monitor keyboard** — raw terminal mode only works on Unix TTY. On non-TTY, it degrades gracefully (sleep loop only).
6. **Stale editable installs** — old `pip install -e` from `~/.hermes/skills/` will shadow the OneDrive code. Clean them out.
7. **Import bridges** — `omk/metrics.py`, `omk/dashboard.py`, etc. are thin re-exports. Don't put logic there; edit `omk/monitoring/*.py` instead.
8. **Tool handlers must return JSON strings** — the LLM expects string content in tool results.
9. **Duplicate paths (v2.1)** — `monitoring/cli.py` and `omk/monitoring/cli.py` must stay in sync. `python -m omk` imports from `omk/omk/monitoring/`.
10. **Provider fallback (v2.1)** — when no API key is set, `omk skill` and `omk run` will error unless a CLI provider is configured. Use `./bin/omk auth --setup <provider>` first.
11. **CLI provider availability (v2.1)** — `kimi`, `codex`, `gemini` adapters expect those CLI tools to be installed and authenticated independently. Check with `which kimi`, `which codex`, `which gemini`.
12. **Auth.json permissions (v2.1)** — `~/.omk/auth.json` should be 600. Never commit it.
13. **Masked keys in CLI configs** — `.kimi/config.toml` may show `sk-L6C...llE5` which is a masked placeholder. Verify it's a real key before storing.
14. **Test API shape first** — always run `registry.get_schemas()` to check actual schema structure (OpenAI uses `{"type": "function", "function": {...}}` not `{"name": ...}`) before writing tests.
15. **MCP health checker import** — `_start_health_checker()` needs `import time` inside the nested function scope or at module top level.
16. **Tool loop warning** — when the same tool fails 3+ times in one turn, the system emits a loop warning. Switch to a different tool or approach immediately.
17. **Cron job script path** — `hermes cron create --script` requires a filename relative to `~/.hermes/scripts/`, not an absolute path. Use a bash wrapper if the script needs a specific interpreter.
18. **Background process hang** — if a background process has no output for several minutes, it may be stuck on network I/O or model loading. Use `process(action="kill")` to stop it (exit code -15 = SIGTERM).