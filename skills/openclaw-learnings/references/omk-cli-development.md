---
title: OMK CLI Development Patterns
description: Lessons from building Rich-based TUI CLI with live monitoring
---

# OMK CLI Development Patterns

From building OMK (Operational Monitoring Kit) CLI for Hermes Agent - a 4-phase implementation using Rich library.

## Phase Breakdown

| Phase | Feature | Key Components |
|-------|---------|----------------|
| P1 | Dashboard (`omk status`) | metrics.py + dashboard.py + Rich panels |
| P2 | Live Monitor (`omk monitor`) | Live refresh with keyboard controls |
| P3 | Views (`tree`, `history`, `models`, `sessions`) | Process tree, trend tables |
| P4 | Hermes Integration (`/omk`) | Slash command dispatch |

## Architecture Pattern

```
omk/
├── __init__.py              # Package exports
├── cli.py                   # CLI entry (argparse + subcommands)
├── metrics.py               # Data layer (SQLite queries)
├── dashboard.py             # Static dashboard rendering
├── monitor.py               # Live TUI with refresh
├── views.py                 # Detailed views (tree, tables)
└── ui/                      # UI components
    ├── colors.py
    ├── tables.py
    └── widgets.py
```

## Rich TUI Best Practices

### 1. Live Dashboard
```python
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout

# Use transient=True for clean exit
# Use screen=False to avoid cursor positioning issues
with Live(layout, refresh_per_second=4, transient=True, screen=False) as live:
    while running:
        update_layout(layout)
        time.sleep(refresh_interval)
```

### 2. Fixing Cursor Position Issues
**Problem:** Cursor appears shifted ~1 tab space after exiting Live mode.

**Solutions tried:**
- ❌ `screen=True` - Uses alternate screen buffer but keyboard handling complex
- ❌ `console.screen()` - Direct screen management too low-level
- ✅ **Winner:** `transient=True, screen=False` - Clean exit, no cursor issues

**Key fix:** Always use `transient=True` to clear display on exit:
```python
with Live(layout, transient=True, screen=False) as live:
    ...
# After exit, cursor returns to normal position
```

### 3. Process Tree with Rich
```python
from rich.tree import Tree

tree = Tree("🦾 Hermes Processes")
# Build parent-child hierarchy
for proc in processes:
    node = tree.add(f"[{pid}] {name}")
    for child in children[pid]:
        node.add(f"  → {child.name}")

Panel(tree, title="Process Tree")
```

### 4. Sparklines (ASCII Mini Charts)
```python
def mini_sparkline(values: List[int]) -> str:
    if not values:
        return "─" * 10
    
    min_val, max_val = min(values), max(values)
    if max_val == min_val:
        return "─" * 10
    
    bars = " ▁▂▃▄▅▆▇█"
    result = ""
    for v in values[-20:]:  # Last 20 points
        idx = int((v - min_val) / (max_val - min_val) * 8)
        result += bars[min(idx, 8)]
    return result
```

### 5. Hermes State DB Schema
Key tables for monitoring:
```sql
-- Session metrics
SELECT COUNT(*), model, started_at
FROM sessions
GROUP BY model
ORDER BY started_at DESC;

-- Token aggregation (fallback if columns don't exist)
SELECT 
    COALESCE(SUM(input_tokens), 0),
    COALESCE(SUM(output_tokens), 0),
    COALESCE(SUM(estimated_cost_usd), 0.0)
FROM sessions
WHERE started_at > ?;
```

## CLI Integration with Hermes

### 1. Add to Command Registry
```python
# hermes_cli/commands.py
CommandDef("omk", "OMK CLI for monitoring", "Info",
           cli_only=True, 
           args_hint="[status|monitor|tree|history|models|sessions]")
```

### 2. Add Handler
```python
# cli.py - process_command()
elif canonical == "omk":
    self._handle_omk_command(cmd_original)

# Handler implementation
def _handle_omk_command(self, command: str):
    import subprocess
    parts = command.strip().split(maxsplit, 1)
    subcommand = parts[1] if len(parts) > 1 else "status"
    
    subprocess.run([sys.executable, "-m", "omk", subcommand])
```

## Known Issues from Live Testing

### 1. REAL Timestamp Schema Mismatch (Critical)
**Finding:** Hermes `state.db` stores `started_at` as `REAL` (Unix timestamp), not ISO strings.
**Impact:** Breaks `omk history`, `omk models`, `omk sessions` — all return empty/wrong data.

**Broken patterns:**
```python
# ❌ Broken - date() doesn't work with REAL
cursor.execute("SELECT date(started_at) ...")  # Returns nothing

# ❌ Broken - fromisoformat on Unix timestamp raises ValueError
datetime.fromisoformat(started_at)  # Crash on float like 1776538835.26
```

**Fix:** Convert REAL to datetime in SQL, or use Unix epoch parsing:
```python
# ✅ Fix for SQL queries
cursor.execute("""
    SELECT date(started_at, 'unixepoch') as date, COUNT(*)
    FROM sessions
    WHERE started_at > ?
    GROUP BY date(started_at, 'unixepoch')
""", (cutoff_timestamp,))  # cutoff must also be REAL/Unix timestamp

# ✅ Fix for Python parsing
def _parse_timestamp(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(val)
    # Fallback for ISO strings
    return datetime.fromisoformat(val.replace("Z", "+00:00"))
```

### 2. Token/Cost Metrics Scope Bug
**Finding:** `get_token_usage()` in metrics.py references `session_count` outside its `try` block.
**Impact:** If the first query succeeds, `session_count` is undefined in the fallback path.

**Fix:** Initialize `session_count = 0` before the try block.

### 3. Live Monitor Keyboard Controls Don't Work
**Finding:** The monitor uses a plain `while running: sleep()` loop. Keys q/p/r/s are documented but not actually handled.
**Impact:** User must Ctrl+C to exit; pause/refresh/speed keys do nothing.

**Fix options:**
- Use `threading.Thread` with `sys.stdin.read(1)` for non-blocking input
- Or migrate to `textual` framework for proper keyboard handling

## Common Pitfalls

### 1. Database Path Resolution
```python
# Get Hermes home (respects HERMES_HOME env)
def get_hermes_home() -> Path:
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env)
    return Path.home() / ".hermes"

# Use it for all DB access
db_path = get_hermes_home() / "state.db"
```

### 2. Import Errors in Subcommands
Handle both dev and installed modes:
```python
try:
    from omk.metrics import collect_full_snapshot
except ImportError:
    from metrics import collect_full_snapshot
```

### 3. Raw Model IDs
Strip provider prefix for cleaner display:
```python
model_name = full_model_id.split("/")[-1]
# "openrouter/free" → "free"
# "moonshot/kimi-k2.6" → "kimi-k2.6"
```

## Metrics to Track

### System Level
- Memory usage (psutil or /proc)
- Disk usage (Hermes home)
- Process count (Hermes + children)

### Session Level
- Total sessions
- 24h active sessions
- Top models used
- Compression ratio (if available)

### Token/Cost Level
- Input/output tokens (today, 7d, 30d)
- Cost estimate (if column exists)
- Fallback to session count × avg tokens

### Error Level
- Recent errors (24h, 7d)
- Warnings count
- Failed cron jobs

## Testing TUI

```bash
# Test each phase
omk status              # Static display
omk monitor             # Interactive (timeout 3s)
omk tree                # Process hierarchy
omk history             # 7-day trend
omk models              # Model breakdown
omk sessions            # Recent sessions

# After exit, cursor should be at normal position
```

## Key Libraries
```toml
dependencies = [
    "rich>=13.0.0",      # Panels, tables, live, trees
    "psutil>=5.9.0",     # Process and system metrics
]
```

## Performance Tips

1. **Refresh rate** - Start with 2s, allow user to change (2/5/10s)
2. **Data caching** - Don't query DB every refresh, use last-snapshot pattern
3. **Lazy loading** - Only collect expensive metrics (process tree) on demand
4. **History limit** - Keep only last 60 data points for sparklines

## Future Enhancements

- Keyboard navigation (↑↓ to select panels)
- Click-to-drill on sessions
- Export to Prometheus/Grafana
- Alert on threshold (memory, errors)

---
File: references/omk-cli-development.md
