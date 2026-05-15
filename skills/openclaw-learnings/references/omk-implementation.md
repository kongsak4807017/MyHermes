---
title: OMK CLI Implementation - Rich TUI Dashboard Pattern
description: Complete implementation guide for building Rich-based operational monitoring CLI with proper terminal handling
---

# OMK CLI Implementation Guide

Complete implementation of Operational Monitoring Kit (OMK) CLI using Rich library.

## Project Structure

```
omk/
├── __init__.py
├── cli.py          # Entry point with subcommands
├── metrics.py      # Data extraction from Hermes state.db
├── dashboard.py    # Rich panel layout for status view
├── monitor.py      # Live TUI with auto-refresh
├── views.py        # Process tree, history, models views
└── subagent.py     # Hermes delegate_task integration
```

## Key Implementation Lessons

### 1. Rich Live Display - Cursor Positioning

**Problem:** Cursor appears offset from typed text when using `Live` display.

**Solution:** Use `screen=False` with `transient=True`:

```python
from rich.live import Live
from rich.console import Console

console = Console(force_terminal=True)

# ❌ Bad - causes cursor offset issues
with Live(layout, screen=True) as live:
    ...

# ✅ Good - cursor stays at correct position
with Live(
    layout,
    console=console,
    refresh_per_second=4,
    transient=True,  # Cleans up on exit
    screen=False     # Keeps cursor in main terminal
) as live:
    while self.running:
        self._update(layout)
        time.sleep(refresh_rate)

# Print newline after for clean prompt
console.print()
```

### 2. Database Schema Mismatches

**Problem:** SQLite schema differs between `sessions.db` and `state.db`.

**Solution:** Always check for column existence:

```python
def get_session_stats() -> Dict[str, Any]:
    db_path = get_hermes_home() / "state.db"
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check column existence with try/except
        try:
            cursor.execute("SELECT started_at FROM sessions LIMIT 1")
        except sqlite3.OperationalError:
            # Fallback to older schema
            cursor.execute("SELECT created_at FROM sessions LIMIT 1")
        
        # Use COALESCE for optional columns
        cursor.execute("""
            SELECT 
                COALESCE(SUM(input_tokens), 0),
                COALESCE(SUM(output_tokens), 0)
            FROM sessions
            WHERE started_at > ?
        """, (cutoff,))
        
    except Exception as e:
        return {"error": str(e), "total": 0}
```

### 3. Process Tree with Rich

```python
from rich.tree import Tree
from collections import defaultdict

def build_process_tree(processes: List[Dict]) -> Tree:
    """Build hierarchical process tree."""
    pids = {p.get("pid") for p in processes}
    roots = []
    children = defaultdict(list)
    
    # Find roots and group children
    for proc in processes:
        ppid = proc.get("ppid")
        if ppid and ppid in pids:
            children[ppid].append(proc)
        else:
            roots.append(proc)
    
    tree = Tree("🦾 Hermes Processes")
    
    def add_process(node, proc: Dict):
        pid = proc.get("pid", 0)
        name = proc.get("name", "unknown")
        mem = proc.get("memory_mb", 0)
        
        status_icon = "🟢" if proc.get("is_child") else "🟡"
        label = f"{status_icon} [{pid}] {name} | {mem:.1f}MB"
        
        child_node = node.add(label)
        for child in children.get(pid, []):
            add_process(child_node, child)
    
    for root in sorted(roots, key=lambda x: x.get("memory_mb", 0), reverse=True):
        add_process(tree, root)
    
    return tree
```

### 4. Sparkline in Terminal

```python
def make_sparkline(self, values: List[int]) -> str:
    """Create ASCII sparkline from values."""
    if not values or len(values) < 2:
        return "─" * 10
    
    min_val, max_val = min(values), max(values)
    if max_val == min_val:
        return "─" * min(len(values), 20)
    
    bars = " ▁▂▃▄▅▆▇█"
    result = ""
    for v in values[-20:]:  # Last 20 points
        idx = int((v - min_val) / (max_val - min_val) * 8)
        result += bars[min(idx, 8)]
    return result
```

### 5. Hermes CLI Integration

Adding `/omk` command to Hermes:

**Step 1:** Add CommandDef in `hermes_cli/commands.py`:
```python
CommandDef("omk", "OpenClaw-style Operational Monitoring Kit (OMK)", "Info",
           cli_only=True, args_hint="[status|monitor|tree|history|models|sessions]")
```

**Step 2:** Add handler in `cli.py`:
```python
# In process_command method
elif canonical == "omk":
    self._handle_omk_command(cmd_original)
```

**Step 3:** Implement handler:
```python
def _handle_omk_command(self, command: str):
    import subprocess
    import sys
    
    parts = command.strip().split(maxsplit=1)
    subcommand = parts[1].lower().strip() if len(parts) > 1 else "status"
    
    valid = ["status", "monitor", "tree", "history", "models", "sessions"]
    if subcommand not in valid:
        _cprint(f"Usage: /omk [{'|'.join(valid)}]")
        return
    
    try:
        subprocess.run(
            [sys.executable, "-m", "omk", subcommand],
            capture_output=False,
            text=True,
            timeout=300 if subcommand == "monitor" else 30
        )
    except Exception as e:
        _cprint(f"OMK error: {e}")
```

## Common Pitfalls

### Patch Loops and Syntax Errors
When multiple patch() calls fail:
1. Always verify file state before patching
2. Use execute_code with ast.parse() to check syntax
3. Consider rewriting entire file if corrupted

### Import Paths
For CLI tool installed via pip:
```python
# Handle both module and direct execution
try:
    from omk.metrics import collect_full_snapshot
except ImportError:
    from metrics import collect_full_snapshot
```

### Terminal Environment Detection
```python
# Check if running in proper terminal
import sys
if not sys.stdout.isatty():
    # Fallback to non-interactive mode
    print("Running in non-interactive mode")
```

## Testing Commands

```bash
# Test individual components
omk status              # Static dashboard
omk monitor             # Live TUI (q to quit)
omk tree                # Process hierarchy
omk history --days 7    # 7-day trend
omk models              # Model breakdown
omk sessions --limit 20 # Recent sessions

# Test Hermes integration
hermes
/omk                    # Default status
/omk monitor           # Live mode
/omk tree              # Process tree
```

## References
- Rich Live: https://rich.readthedocs.io/en/stable/live.html
- Rich Layout: https://rich.readthedocs.io/en/stable/layout.html
- Rich Tree: https://rich.readthedocs.io/en/stable/tree.html
