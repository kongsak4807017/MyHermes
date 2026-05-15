"""OMK CLI - Main entry point for the Operational Monitoring Kit.

Inspired by OpenClaw's focus on operational visibility:
- Cost transparency
- Session stability 
- Live monitoring
- Sub-agent orchestration
"""

import argparse
import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from omk.metrics import collect_full_snapshot, get_hermes_home
    from omk.dashboard import render_dashboard
    from omk.monitor import run_monitor
    from omk.subagent import run_subagent_mode
except ImportError as e:
    # Try alternative import for development
    try:
        from metrics import collect_full_snapshot, get_hermes_home
        from dashboard import render_dashboard
        from monitor import run_monitor
        from subagent import run_subagent_mode
    except ImportError:
        from omk.metrics import collect_full_snapshot, get_hermes_home
        from omk.dashboard import render_dashboard
        from omk.monitor import run_monitor
        # Subagent optional
        run_subagent_mode = None

# Alternative: make subagent optional
if 'run_subagent_mode' not in dir() or run_subagent_mode is None:
    def run_subagent_mode(args):
        print("Subagent mode not yet implemented")
        return 1


def cmd_status(args):
    """Show current operational status snapshot."""
    snapshot = collect_full_snapshot(args.verbosity)
    
    if args.json:
        print(json.dumps(snapshot, indent=2, default=str))
        return 0
    
    render_dashboard(snapshot, args.skin)
    return 0


def cmd_monitor(args):
    """Run live monitoring dashboard."""
    return run_monitor()


def cmd_subagent(args):
    """Run in subagent mode for Hermes delegation."""
    return run_subagent_mode(args.task, args.context)


def cmd_export(args):
    """Export metrics to file."""
    snapshot = collect_full_snapshot("full")
    
    output_path = Path(args.output)
    if args.format == "json":
        with open(output_path, "w") as f:
            json.dump(snapshot, f, indent=2, default=str)
    elif args.format == "csv":
        # Simple CSV export of key metrics
        import csv
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["metric", "value"])
            writer.writerow(["timestamp", snapshot.get("timestamp")])
            writer.writerow(["total_sessions", snapshot.get("sessions", {}).get("total")])
            writer.writerow(["active_24h", snapshot.get("sessions", {}).get("active_24h")])
            tokens = snapshot.get("token_usage", {})
            writer.writerow(["total_tokens", tokens.get("total_tokens")])
            writer.writerow(["cost_estimate", tokens.get("cost_estimate")])
    
    print(f"Exported to {output_path}")
    return 0


def cmd_inspect(args):
    """Inspect specific session or task."""
    from omk.metrics import get_hermes_home
    import sqlite3
    
    db_path = get_hermes_home() / "state.db"
    if not db_path.exists():
        print("No state.db found")
        return 1
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if args.session_id:
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (args.session_id,))
        row = cursor.fetchone()
        if row:
            print(json.dumps(dict(row), indent=2, default=str))
        else:
            print(f"Session {args.session_id} not found")
    elif args.recent:
        cursor.execute("SELECT * FROM sessions ORDER BY started_at DESC LIMIT ?", (args.recent,))
        rows = cursor.fetchall()
        for row in rows:
            print(f"\n{'='*60}")
            print(json.dumps(dict(row), indent=2, default=str))
    
    conn.close()
    return 0


def cmd_tree(args):
    """Show process tree."""
    from omk.views import render_process_tree
    from rich.console import Console
    
    console = Console()
    panel = render_process_tree()
    console.print(panel)
    return 0


def cmd_history(args):
    """Show session history trends."""
    from omk.views import render_history_trend
    from rich.console import Console
    
    console = Console()
    panel = render_history_trend(days=args.days)
    console.print(panel)
    return 0


def cmd_models(args):
    """Show model usage breakdown."""
    from omk.views import render_model_breakdown
    from rich.console import Console
    
    console = Console()
    panel = render_model_breakdown(days=args.days)
    console.print(panel)
    return 0


def cmd_sessions(args):
    """Show recent sessions."""
    from omk.views import render_recent_sessions
    from rich.console import Console
    
    console = Console()
    panel = render_recent_sessions(limit=args.limit)
    console.print(panel)
    return 0


def cmd_health(args):
    """Show health score and anomalies."""
    from omk.metrics import collect_full_snapshot
    from omk.analytics import compute_health_score, detect_anomalies, get_predictive_insights
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box

    console = Console()
    snapshot = collect_full_snapshot("compact")

    # Health score
    health = compute_health_score(snapshot)
    score = health["score"]
    status = health["status"]
    color = "green" if status == "healthy" else "yellow" if status == "degraded" else "red"
    icon = "🟢" if status == "healthy" else "🟡" if status == "degraded" else "🔴"

    # Components table
    comp_table = Table(show_header=True, box=box.SIMPLE)
    comp_table.add_column("Component", style="cyan")
    comp_table.add_column("Score", justify="right")
    comp_table.add_column("Weight")
    weights = {"session": "30%", "error": "25%", "token": "20%", "system": "15%", "process": "10%"}
    for comp, s in health["components"].items():
        scolor = "green" if s >= 80 else "yellow" if s >= 50 else "red"
        comp_table.add_row(comp.capitalize(), f"[{scolor}]{s}[/{scolor}]", weights.get(comp, ""))

    # Anomalies
    anomalies = detect_anomalies(days=args.days)
    anomaly_lines = []
    for a in anomalies:
        sev_color = "green" if a["severity"] == "ok" else "yellow" if a["severity"] == "warning" else "red"
        anomaly_lines.append(f"  [{sev_color}]{a['severity'].upper()}[/{sev_color}]: {a['message']}")

    # Insights
    insights = get_predictive_insights(days=args.days)
    insight_lines = [f"  💡 {i}" for i in insights]

    content = Text.assemble(
        f"{icon} Health Score: [bold {color}]{score}/100[/bold {color}]  (Status: {status.upper()})\n\n",
        "[bold underline]Component Breakdown[/bold underline]\n",
    )
    console.print(Panel(content, title="🦾 OMK Health Check", border_style=color))
    console.print(comp_table)

    if anomaly_lines:
        console.print(Panel("\n".join(anomaly_lines), title="🔍 Anomalies", border_style="yellow"))
    if insight_lines:
        console.print(Panel("\n".join(insight_lines), title="📈 Insights", border_style="cyan"))

    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="omk",
        description="OMK - Operational Monitoring Kit for Hermes Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  omk status              Show current operational status
  omk status --json       Export status as JSON
  omk monitor             Run live monitoring dashboard
  omk export -f json -o metrics.json   Export full metrics
  omk inspect --recent 5  Show last 5 sessions
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # status
    status_parser = subparsers.add_parser("status", help="Show operational status")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")
    status_parser.add_argument("--skin", default="default", help="UI skin (default, ares, mono)")
    status_parser.add_argument("--verbosity", choices=["minimal", "compact", "full"],
                               default="compact", help="Detail level")
    status_parser.set_defaults(func=cmd_status)
    
    # monitor
    monitor_parser = subparsers.add_parser("monitor", help="Live monitoring dashboard")
    monitor_parser.set_defaults(func=cmd_monitor)
    
    # export
    export_parser = subparsers.add_parser("export", help="Export metrics to file")
    export_parser.add_argument("-f", "--format", choices=["json", "csv"], default="json")
    export_parser.add_argument("-o", "--output", required=True, help="Output file path")
    export_parser.set_defaults(func=cmd_export)
    
    # tree
    tree_parser = subparsers.add_parser("tree", help="Show process tree")
    tree_parser.set_defaults(func=cmd_tree)
    
    # history
    history_parser = subparsers.add_parser("history", help="Show session history trends")
    history_parser.add_argument("--days", type=int, default=7, help="Number of days")
    history_parser.set_defaults(func=cmd_history)
    
    # models
    models_parser = subparsers.add_parser("models", help="Show model usage breakdown")
    models_parser.add_argument("--days", type=int, default=7, help="Number of days")
    models_parser.set_defaults(func=cmd_models)
    
    # sessions
    sessions_parser = subparsers.add_parser("sessions", help="Show recent sessions")
    sessions_parser.add_argument("--limit", type=int, default=20, help="Number of sessions")
    sessions_parser.set_defaults(func=cmd_sessions)
    
    # inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect sessions/tasks")
    inspect_parser.add_argument("--session-id", help="Inspect specific session")
    inspect_parser.add_argument("--recent", type=int, help="Show N recent sessions")
    inspect_parser.set_defaults(func=cmd_inspect)
    
    # subagent (used internally by Hermes)
    subagent_parser = subparsers.add_parser("subagent", help="Subagent mode (internal)")
    subagent_parser.add_argument("--task", required=True, help="Task description")
    subagent_parser.add_argument("--context", help="JSON context")
    subagent_parser.set_defaults(func=cmd_subagent)
    
    # health
    health_parser = subparsers.add_parser("health", help="Show health score and anomalies")
    health_parser.add_argument("--days", type=int, default=7, help="Analysis window in days")
    health_parser.set_defaults(func=cmd_health)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n Interrupted")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
