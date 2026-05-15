"""OMK Dashboard — Rich panel layout for status snapshot."""

from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from datetime import datetime

from omk.metrics import collect_full_snapshot
from omk.ui.colors import get_colors, get_branding, get_skin_name
from omk.ui.tables import (
    session_table, token_table, error_table, cron_table, skills_table, process_table
)
from omk.ui.widgets import (
    gauge_bar, status_badge, big_number, separator,
    make_gauge_panel, make_stat_line, panel_with_border
)


def render_dashboard(snapshot: dict, compact: bool = False) -> Panel:
    """Render the full OMK dashboard panel."""
    colors = get_colors()
    agent_name = get_branding()
    skin_name = get_skin_name()
    ts = datetime.fromisoformat(snapshot["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

    # Build sections
    sections = []

    # === Header ===
    header = Text.assemble(
        f"[bold cyan]🦾 OMK Operational Dashboard[/bold cyan]  [{colors['dim']}]"
        f"— {agent_name} ({skin_name} skin)[/{colors['dim']}]"
    )
    sections.append(header)
    sections.append(Rule())

    # === System Health ===
    system = snapshot.get("system", {})
    mem = system.get("memory", {})
    disk = system.get("hermes_disk", {})

    sys_section = Group(
        Text("[bold underline]System Health[/bold underline]"),
        Text(""),
        make_stat_line("Memory", f"{mem.get('used_mb', 0)} / {mem.get('total_mb', 0)} MB",
                       icon="💾", color="cyan"),
        Text(gauge_bar(mem.get("percent", 0), "", width=30,
                       color="green" if mem.get("percent", 0) < 70 else "yellow" if mem.get("percent", 0) < 90 else "red")),
        Text(""),
        make_stat_line("Disk (~/.hermes)", f"{disk.get('used_human', 'N/A')} / {disk.get('total_human', 'N/A')}",
                       icon="💿", color="cyan"),
        Text(gauge_bar(disk.get("percent", 0), "", width=30,
                       color="green" if disk.get("percent", 0) < 70 else "yellow" if disk.get("percent", 0) < 90 else "red")),
    )
    sections.append(sys_section)
    sections.append(Rule())

    # === Sessions ===
    sessions = snapshot.get("sessions", {})
    sess_section = Group(
        Text("[bold underline]Sessions[/bold underline]"),
        Text(""),
        make_stat_line("Total Sessions", str(sessions.get("total", 0)), icon="📊"),
        make_stat_line("Database Size", sessions.get("size_human", "N/A"), icon="📁"),
        make_stat_line("Active (24h)", str(sessions.get("active_24h", 0)), icon="🟢"),
    )

    # Top models
    models = sessions.get("top_models", [])
    if models:
        model_text = " | ".join(
            f"{m['model'].split('/')[-1]}({m['count']})" for m in models[:3]
        )
        sess_section = Group(
            *sess_section.renderables,
            Text(""),
            make_stat_line("Top Models", model_text, icon="🤖"),
        )
    sections.append(sess_section)

    if not compact:
        sections.append(Rule())

        # === Token Usage ===
        tokens = snapshot.get("token_usage", {})
        tok_section = Group(
            Text("[bold underline]Token Usage (Today)[/bold underline]"),
            Text(""),
            make_stat_line("Input Tokens", f"{tokens.get('input_tokens', 0):,}", icon="📥"),
            make_stat_line("Output Tokens", f"{tokens.get('output_tokens', 0):,}", icon="📤"),
            make_stat_line("Total Tokens", f"{tokens.get('total_tokens', 0):,}", icon="🔢"),
            make_stat_line("Cost Estimate", f"${tokens.get('cost_estimate', 0):.4f}", icon="💰"),
        )
        sections.append(tok_section)

    sections.append(Rule())

    # === Errors ===
    errors = snapshot.get("errors", {})
    ec = errors.get("error_count", 0)
    wc = errors.get("warning_count", 0)
    err_status = "error" if ec > 0 else "warning" if wc > 0 else "ok"

    err_section = Group(
        Text("[bold underline]Errors (24h)[/bold underline]"),
        Text(""),
        Text(status_badge(f"Errors: {ec}", "error" if ec > 0 else "ok")),
        Text(status_badge(f"Warnings: {wc}", "warn" if wc > 0 else "ok")),
    )

    # Show recent errors
    recent_errors = errors.get("errors", [])[-3:]
    if recent_errors:
        err_lines = []
        for e in recent_errors:
            err_lines.append(Text(f"  🔴 {e[-90:]}", style="dim"))
        err_section = Group(
            *err_section.renderables,
            Text(""),
            *err_lines,
        )
    sections.append(err_section)

    if not compact:
        sections.append(Rule())

        # === Active Jobs ===
        cron = snapshot.get("cron", {})
        jobs_section = Group(
            Text("[bold underline]Cron Jobs[/bold underline]"),
            Text(""),
            Text(status_badge(f"Running: {cron.get('running', 0)}", "running")),
            Text(status_badge(f"Scheduled: {cron.get('scheduled', 0)}", "ok")),
            Text(status_badge(f"Paused: {cron.get('paused', 0)}", "paused") if cron.get("paused", 0) > 0 else ""),
            Text(status_badge(f"Failed: {cron.get('failed', 0)}", "error") if cron.get("failed", 0) > 0 else ""),
        )
        sections.append(jobs_section)

    if not compact:
        sections.append(Rule())

        # === Processes ===
        procs = snapshot.get("processes", [])
        proc_section = Group(
            Text("[bold underline]Hermes Processes[/bold underline]"),
            Text(""),
            Text(f"  Found {len(procs)} process(es)") if procs else Text("  [dim]No Hermes processes detected[/dim]"),
        )
        for p in procs[:5]:
            status = p.get("status", "unknown")
            icon = "🟢" if status == "running" else "🟡" if status == "sleeping" else "❓"
            cmd = p.get("command", "")[:70]
            pid = p.get("pid", "?")
            mem_mb = p.get("memory_mb", 0)
            proc_section = Group(
                *proc_section.renderables,
                Text(f"  {icon} [{pid}] {cmd}  [{mem_mb} MB]"),
            )
        sections.append(proc_section)

    # === Footer ===
    sections.append(Rule())

    # Skills
    skills = snapshot.get("skills", {})
    sf_section = Group(
        Text.assemble(
            f"[dim]Skills: {skills.get('total', 0)} loaded[/dim]"
            f"  |  [dim]Timestamp: {ts}[/dim]"
            f"  |  [dim]Hermes Home: {snapshot.get('hermes_home', 'N/A')}[/dim]"
        )
    )
    sections.append(sf_section)

    # Compose all sections
    content = Group(*sections)

    return Panel(
        content,
        title=f"🦾 OMK — {agent_name}",
        subtitle=f"[dim]v0.1.0 | {skin_name} skin | {ts}[/dim]",
        border_style="bright_blue",
        padding=(1, 2),
        expand=True,
    )


def print_dashboard(console: Console = None, compact: bool = False, verbosity: str = "full"):
    """Collect metrics and print the formatted dashboard."""
    console = console or Console()

    snapshot = collect_full_snapshot(verbosity=verbosity)
    panel = render_dashboard(snapshot, compact=compact)

    console.print(panel)

    return snapshot
