# OMK CLI — Implementation Plan

## Project: OMK (Operational Monitoring & Knowledge) CLI
**Hermes Agent companion tool** สำหรับ monitoring, dashboard, subagent tracking, และ operational analytics

---

## Architecture

```
omk/                          # Python package
├── __init__.py               # Package init, version
├── __main__.py               # python -m omk entry point
├── cli.py                    # CLI entry (argparse) — omk status/monitor/history/etc
├── dashboard.py              # Phase 1: status dashboard
├── monitor.py                # Phase 2: live monitor mode
├── processes.py              # Phase 3: process tree / subagent tracking
├── history.py                # Phase 3: historical trends
├── logs.py                   # Phase 3: log viewer
├── metrics.py                # All phases: metrics extraction engine
├── state.py                  # All phases: OMK state persistence
├── notifier.py               # Phase 4: threshold alerts
├── hermes_integration.py     # Phase 4: /omk slash command, auto-detect
└── ui/
    ├── colors.py             # ANSI color constants + skin integration
    ├── tables.py             # Rich table layouts
    └── widgets.py            # Custom Rich widgets (gauge, badge, etc.)

omk-cli/                      # Executable wrapper
└── omk                       # #!/usr/bin/env python3 launcher

tests/                        # Test suite
├── test_metrics.py
├── test_dashboard.py
├── test_monitor.py
└── test_ui.py

setup.py                      # pip install -e .
pyproject.toml                # Modern Python packaging
```

---

## Phase 1: Core Dashboard (`omk status`)

### Goal
Dashboard snapshot ในหน้าเดียว — Rich panels, colored output, skin theming

### Metrics to collect
- Session stats (count, size, last active) — from `~/.hermes/sessions/`
- Token usage today — from session DB
- Active cron jobs — from cron state
- Errors (24h) — from `~/.hermes/logs/`
- Skills loaded — from `~/.hermes/skills/`
- Disk usage — from filesystem
- Active subagents — from process scan
- Memory usage — from `ps`

### Features
- Rich Panel layout
- Skin color integration (inherit from Hermes skin engine)
- Tables with colored borders
- Status badges (OK / WARN / ERROR)
- Progress bars (memory, disk)
- Single-run mode (snapshot)

### Install
```bash
pip install -e .
omk status
```

---

## Phase 2: Live Monitor (`omk monitor`)

### Goal
Real-time monitoring — Rich Live display, refresh ทุก 2-5 วินาที

### Features
- `Rich Live` full-screen display
- Auto-refresh interval (default 2s)
- Subagent activity feed (spinner per active task)
- Tool call activity feed (recent calls with status)
- Token usage live counter (parse logs/metrics)
- Gauge bars (memory, disk, session size)
- Uptime counter
- Error counter
- Ctrl+C graceful exit

### Commands
```bash
omk monitor                    # default refresh (2s)
omk monitor --interval 5       # refresh every 5s
omk monitor --filter delegate  # only show delegate activity
omk monitor --json             # output as JSON stream
```

---

## Phase 3: Advanced Features

### 3.1 Process Tree (`omk process-tree`)
- Scan process tree from Hermes PID
- Show subagents, child processes, cron jobs
- Rich Tree visualization
- Status indicators (running, sleeping, zombie)
- CPU/memory per process

### 3.2 History (`omk history`)
- Historical trends table (7, 14, 30 days)
- Sessions, tokens, cost, errors, tools used
- ASCII bar charts
- Export to CSV/JSON

### 3.3 Log Viewer (`omk logs`)
- Filtered log viewer
- Color-coded severity
- Search/pattern matching
- Pagination
- Export

### Commands
```bash
omk process-tree               # tree view
omk history --days 7           # 7-day trends
omk history --days 30 --export csv
omk logs --level error         # errors only
omk logs --grep "timeout"      # pattern match
omk logs --tail 20             # last 20 entries
```

---

## Phase 4: Hermes Integration

### 4.1 `/omk` Slash Command
- Register `/omk` command ที่ Hermes gateway
- Support subcommands: `status`, `monitor`, `logs`
- Display dashboard inline ใน chat

### 4.2 Auto-detect Subagent Spawning
- Hook into delegate_task execution
- Push notification to monitor when subagent spawns/completes
- Track subagent lifecycle

### 4.3 Threshold Alerts
- Configurable thresholds (memory, disk, errors, cost)
- Alert via callback / notification system
- Persistent alert log

### 4.4 Dashboard Skin Integration
- OMK uses same skin config as Hermes
- Colors, branding, tool_emojis synced
- Custom OMK skin section

### Config (`~/.hermes/config.yaml`)
```yaml
omk:
  enabled: true
  refresh_interval: 2
  dashboard_mode: full         # full, compact, minimal
  skin_sync: true              # use Hermes skin
  thresholds:
    max_memory_mb: 512
    max_disk_mb: 1000
    max_errors_per_day: 10
    max_cost_per_day: 1.0
    max_session_count: 100
  alerts:
    enabled: true
    webhook_url: ""            # optional webhook
```

---

## Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| UI library | Rich (already dependency of Hermes) | No new deps, consistent look |
| CLI parser | argparse (stdlib) | Simple, no deps |
| State storage | JSON in `~/.hermes/omk/` | Lightweight, no DB needed |
| Skin integration | Import Hermes skin_engine | Zero code duplication |
| Packaging | setuptools + pyproject.toml | Standard Python packaging |
| Metrics collection | Direct filesystem/SQLite reads | No API overhead |

## Dependencies

```
rich>=13.0.0        # Already in Hermes
psutil>=5.9.0       # Process/memory monitoring
```

## Installation

```bash
# From source
cd omk-cli/
pip install -e .

# Verify
omk --version
omk status
omk monitor
```

## Timeline

| Phase | Scope | Est. Time |
|-------|-------|-----------|
| Phase 1 | Dashboard | 1-2 sessions |
| Phase 2 | Live monitor | 1-2 sessions |
| Phase 3 | Advanced features | 2-3 sessions |
| Phase 4 | Hermes integration | 1-2 sessions |

## Testing Strategy

- Unit tests: metrics extraction, UI layouts, parsing
- Integration tests: full dashboard, monitor refresh
- Manual tests: skin integration, real Hermes instance
- Test data: mock session DB, mock logs, mock processes
