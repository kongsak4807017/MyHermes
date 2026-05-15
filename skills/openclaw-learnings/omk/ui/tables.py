"""OMK Tables — Rich table layouts for dashboard display."""

from rich.table import Table


def session_table(stats: dict) -> Table:
    """Build sessions statistics table."""
    table = Table(
        title="📊 Sessions",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Value", style="green")

    total = stats.get("total", 0)
    table.add_row("Total Sessions", str(total))

    size = stats.get("size_human", "N/A")
    table.add_row("DB Size", size)

    active = stats.get("active_24h", 0)
    table.add_row("Active (24h)", str(active))

    compressed = stats.get("compressed", 0)
    table.add_row("Compressed", f"{compressed}/{total}")

    oldest = stats.get("oldest", "N/A")
    newest = stats.get("newest", "N/A")
    table.add_row("Oldest / Newest", f"{oldest[:16]} / {newest[:16]}")

    if stats.get("top_models"):
        models = ", ".join(
            f"{m['model'].split('/')[-1]}({m['count']})"
            for m in stats["top_models"][:3]
        )
        table.add_row("Top Models", models)

    return table


def token_table(usage: dict) -> Table:
    """Build token usage table."""
    table = Table(
        title="💰 Token Usage",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Value", justify="right")

    inp = usage.get("input_tokens", 0)
    out = usage.get("output_tokens", 0)
    total = usage.get("total_tokens", 0)
    cost = usage.get("cost_estimate", 0)

    table.add_row("Input Tokens (today)", f"{inp:,}")
    table.add_row("Output Tokens (today)", f"{out:,}")
    table.add_row("Total Tokens (today)", f"{total:,}")
    table.add_row("Cost Estimate (today)", f"${cost:.4f}")

    if usage.get("token_usage_7d"):
        d7 = usage["token_usage_7d"]
        table.add_row("7-day Total Tokens", f"{d7.get('total_tokens', 0):,}")
        table.add_row("7-day Cost", f"${d7.get('cost_estimate', 0):.4f}")

    return table


def error_table(errors: dict) -> Table:
    """Build error summary table."""
    table = Table(
        title="⚠️  Errors (24h)",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Level", style="bold", width=8)
    table.add_column("Count", justify="right", width=8)

    ec = errors.get("error_count", 0)
    wc = errors.get("warning_count", 0)

    level_style = "red" if ec > 0 else "green"
    table.add_row("Errors", str(ec), style=level_style)

    level_style = "yellow" if wc > 0 else "green"
    table.add_row("Warnings", str(wc), style=level_style)

    # Show recent errors
    recent = errors.get("errors", [])[-3:]
    for err in recent:
        # Extract just the message part
        msg = err[-80:] if len(err) > 80 else err
        table.add_row("  └─", f"[dim]{msg}[/dim]")

    return table


def cron_table(stats: dict) -> Table:
    """Build cron jobs table."""
    table = Table(
        title="⏰ Cron Jobs",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Status", style="bold", width=12)
    table.add_column("Count", justify="right", width=8)

    statuses = [
        ("Running", stats.get("running", 0), "green"),
        ("Scheduled", stats.get("scheduled", 0), "cyan"),
        ("Paused", stats.get("paused", 0), "yellow"),
        ("Failed", stats.get("failed", 0), "red"),
    ]

    for label, count, style in statuses:
        if count > 0 or label in ("Running", "Scheduled"):
            table.add_row(label, str(count), style=style)

    return table


def skills_table(stats: dict) -> Table:
    """Build skills table."""
    table = Table(
        title="📚 Skills",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Total", style="green", width=12)
    table.add_column("Categories", style="cyan")

    total = stats.get("total", 0)
    cats = stats.get("categories", {})
    cat_text = ", ".join(f"{k}: {v}" for k, v in sorted(cats.items()) if v > 0)
    if len(cat_text) > 60:
        cat_text = cat_text[:57] + "..."

    table.add_row(str(total), cat_text or "None found")

    return table


def process_table(processes: list) -> Table:
    """Build process table."""
    table = Table(
        title="🔧 Processes",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("PID", width=8)
    table.add_column("CPU%", width=8)
    table.add_column("MEM%", width=8)
    table.add_column("Status", width=10)
    table.add_column("Command", style="dim")

    for p in processes[:8]:
        status = p.get("status", "unknown")
        status_style = "green" if status == "running" else "yellow"
        table.add_row(
            str(p.get("pid", "?")),
            f"{p.get('cpu', 0):.1f}",
            f"{p.get('mem', 0):.1f}",
            f"[{status_style}]{status}[/]",
            p.get("command", "")[:60],
        )

    if not processes:
        table.add_row("—", "—", "—", "—", "[dim]No Hermes processes found[/dim]")

    return table
