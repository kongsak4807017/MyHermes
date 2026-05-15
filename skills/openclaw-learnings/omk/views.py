"""OMK Views — Process tree, history trends, and detailed drill-down views.

Phase 3: Advanced visualizations for OMK CLI.
"""

import sqlite3
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

try:
    from rich.tree import Tree
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .metrics import get_hermes_home, get_hermes_processes


def build_process_tree(processes: List[Dict]) -> Tree:
    """Build a Rich tree of Hermes processes with parent/child relationships."""
    if not RICH_AVAILABLE:
        return None
    
    # Find root processes (no parent or parent not in list)
    pids = {p.get("pid") for p in processes}
    roots = []
    children = defaultdict(list)
    
    for proc in processes:
        ppid = proc.get("ppid")
        if ppid and ppid in pids:
            children[ppid].append(proc)
        else:
            roots.append(proc)
    
    # Build tree
    tree = Tree("🦾 Hermes Processes")
    
    def add_process(node, proc: Dict):
        pid = proc.get("pid", 0)
        name = proc.get("name", "unknown")
        cmd = proc.get("command", "")[:40]
        mem = proc.get("memory_mb", 0)
        cpu = proc.get("cpu", 0)
        
        status_icon = "🟢" if proc.get("is_child") else "🟡"
        label = f"{status_icon} [{pid}] {name} | {mem:.1f}MB | {cpu:.1f}% | {cmd}"
        
        child_node = node.add(label)
        
        # Add children recursively
        for child in children.get(pid, []):
            add_process(child_node, child)
    
    for root in sorted(roots, key=lambda x: x.get("memory_mb", 0), reverse=True):
        add_process(tree, root)
    
    return tree


def render_process_tree() -> Panel:
    """Render process tree as a Rich panel."""
    if not RICH_AVAILABLE:
        return Panel("rich library required")
    
    processes = get_hermes_processes()
    if not processes:
        return Panel("No Hermes processes found", title="Process Tree")
    
    tree = build_process_tree(processes)
    return Panel(tree, title=f"[bold]Process Tree ({len(processes)} processes)[/bold]", box=box.ROUNDED)


def get_session_history(days: int = 7) -> List[Dict]:
    """Get session history for trend analysis."""
    herm_home = get_hermes_home()
    db_path = herm_home / "state.db"

    if not db_path.exists():
        return []

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cutoff = time.time() - (days * 86400)

        cursor.execute("""
            SELECT
                date(started_at, 'unixepoch') as date,
                COUNT(*) as count,
                SUM(COALESCE(input_tokens, 0)) as input_tokens,
                SUM(COALESCE(output_tokens, 0)) as output_tokens,
                COUNT(DISTINCT model) as models_used
            FROM sessions
            WHERE started_at > ?
            GROUP BY date(started_at, 'unixepoch')
            ORDER BY date
        """, (cutoff,))

        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        conn.close()


def render_history_trend(days: int = 7) -> Panel:
    """Render session history trend as a table with sparklines."""
    if not RICH_AVAILABLE:
        return Panel("rich library required")
    
    history = get_session_history(days)
    
    if not history:
        return Panel("No history data available", title="History Trend")
    
    table = Table(show_header=True, box=box.SIMPLE)
    table.add_column("Date", style="cyan")
    table.add_column("Sessions", justify="right")
    table.add_column("Trend", width=15)
    table.add_column("Tokens", justify="right")
    table.add_column("Models", justify="right")
    
    # Calculate sparkline
    counts = [h.get("count", 0) for h in history]
    max_count = max(counts) if counts else 1
    
    for day in history:
        date_str = day.get("date", "unknown")
        count = day.get("count", 0)
        tokens = (day.get("input_tokens", 0) or 0) + (day.get("output_tokens", 0) or 0)
        models = day.get("models_used", 0)
        
        # Mini bar chart
        bar_len = int((count / max_count) * 10) if max_count > 0 else 0
        bar = "█" * bar_len + "░" * (10 - bar_len)
        
        table.add_row(
            date_str[-5:],  # Show MM-DD
            str(count),
            bar,
            f"{tokens:,}",
            str(models)
        )
    
    # Summary row
    total_sessions = sum(counts)
    total_tokens = sum((h.get("input_tokens", 0) or 0) + (h.get("output_tokens", 0) or 0) for h in history)
    
    table.add_row(
        "[bold]Total[/bold]",
        f"[bold]{total_sessions}[/bold]",
        "",
        f"[bold]{total_tokens:,}[/bold]",
        "",
        style="green"
    )
    
    return Panel(table, title=f"[bold]7-Day Session History[/bold]", box=box.ROUNDED)


def get_model_breakdown(days: int = 7) -> Dict[str, Dict]:
    """Get usage breakdown by model."""
    herm_home = get_hermes_home()
    db_path = herm_home / "state.db"

    if not db_path.exists():
        return {}

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cutoff = time.time() - (days * 86400)

        cursor.execute("""
            SELECT
                model,
                COUNT(*) as sessions,
                SUM(COALESCE(input_tokens, 0)) as input_tokens,
                SUM(COALESCE(output_tokens, 0)) as output_tokens
            FROM sessions
            WHERE started_at > ? AND model IS NOT NULL
            GROUP BY model
            ORDER BY sessions DESC
        """, (cutoff,))

        return {
            row["model"]: dict(row)
            for row in cursor.fetchall()
        }
    except Exception:
        return {}
    finally:
        conn.close()


def render_model_breakdown(days: int = 7) -> Panel:
    """Render model usage breakdown."""
    if not RICH_AVAILABLE:
        return Panel("rich library required")
    
    models = get_model_breakdown(days)
    
    if not models:
        return Panel("No model data available", title="Model Usage")
    
    table = Table(show_header=True, box=box.SIMPLE)
    table.add_column("Model", style="cyan")
    table.add_column("Sessions", justify="right")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Total", justify="right")
    
    total_tokens = 0
    for model_name, data in list(models.items())[:10]:  # Top 10
        sessions = data.get("sessions", 0)
        inp = data.get("input_tokens", 0) or 0
        out = data.get("output_tokens", 0) or 0
        total = inp + out
        total_tokens += total
        
        # Truncate model name
        display_name = model_name.split("/")[-1] if "/" in model_name else model_name
        display_name = display_name[:30]
        
        table.add_row(
            display_name,
            str(sessions),
            f"{inp:,}",
            f"{out:,}",
            f"{total:,}"
        )
    
    return Panel(table, title=f"[bold]Model Usage ({days}d)[/bold] - {len(models)} models", box=box.ROUNDED)


def get_recent_sessions(limit: int = 20) -> List[Dict]:
    """Get recent sessions with details."""
    herm_home = get_hermes_home()
    db_path = herm_home / "state.db"

    if not db_path.exists():
        return []

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                started_at,
                ended_at,
                model,
                source,
                COALESCE(input_tokens, 0) as input_tokens,
                COALESCE(output_tokens, 0) as output_tokens
            FROM sessions
            ORDER BY started_at DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        conn.close()


def render_recent_sessions(limit: int = 20) -> Panel:
    """Render recent sessions table."""
    if not RICH_AVAILABLE:
        return Panel("rich library required")

    sessions = get_recent_sessions(limit)

    if not sessions:
        return Panel("No sessions found", title="Recent Sessions")

    if "error" in sessions[0]:
        return Panel(f"Error: {sessions[0]['error']}", title="Recent Sessions")

    table = Table(show_header=True, box=box.SIMPLE)
    table.add_column("ID", style="dim", width=8)
    table.add_column("Time", style="cyan", width=12)
    table.add_column("Model", width=25)
    table.add_column("Source", width=10)
    table.add_column("Tokens", justify="right")
    table.add_column("Duration", justify="right")

    for s in sessions:
        sid = str(s.get("id", "unknown"))[:6]

        # Format time from Unix timestamp
        started = s.get("started_at")
        if started:
            try:
                dt = datetime.fromtimestamp(float(started))
                time_str = dt.strftime("%m-%d %H:%M")
            except Exception:
                time_str = str(started)[:16]
        else:
            time_str = "?"

        model = s.get("model", "unknown") or "unknown"
        model = model.split("/")[-1] if "/" in model else model
        model = model[:24]

        source = s.get("source", "cli") or "cli"
        source = source[:8]

        tokens = (s.get("input_tokens", 0) or 0) + (s.get("output_tokens", 0) or 0)

        # Calculate duration if available
        ended = s.get("ended_at")
        if started and ended:
            try:
                duration = int(float(ended) - float(started))
                dur_str = f"{duration}s"
            except Exception:
                dur_str = "-"
        else:
            dur_str = "-"

        table.add_row(sid, time_str, model, source, f"{tokens:,}", dur_str)

    return Panel(table, title=f"[bold]Recent Sessions ({len(sessions)} shown)[/bold]", box=box.ROUNDED)
