"""OMK Widgets — Custom Rich widgets for dashboard display."""

from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text


def gauge_bar(percent: float, label: str = "", width: int = 30, color: str = "green") -> str:
    """Create a text-based progress gauge bar.

    Returns a rich-formatted string like: ████████░░ 80%
    """
    percent = max(0, min(100, percent))
    filled = int(width * percent / 100)
    empty = width - filled

    bar = f"[{color}]{'█' * filled}{'░' * empty}[/{color}] {percent:.0f}%"
    if label:
        bar = f"{label} {bar}"
    return bar


def status_badge(text: str, status: str) -> str:
    """Create a status badge like ✅ OK or 🔴 ERROR."""
    badges = {
        "ok": "✅",
        "good": "✅",
        "running": "🟢",
        "warning": "⚠️",
        "warn": "⚠️",
        "error": "🔴",
        "failed": "🔴",
        "paused": "⏸️",
        "unknown": "❓",
    }
    icon = badges.get(status.lower(), "❓")
    return f"{icon} {text}"


def big_number(value: str, label: str, unit: str = "") -> str:
    """Create a big number display card."""
    if unit:
        return f"[bold cyan]{label}:[/bold cyan]  [bold green]{value}[/bold green] {unit}"
    return f"[bold cyan]{label}:[/bold cyan]  [bold green]{value}[/bold green]"


def separator() -> str:
    """Create a divider line."""
    return "[dim]─" * 50 + "[/dim]"


def panel_with_border(content, title: str = "", border_style: str = "blue") -> Panel:
    """Create a Rich Panel with colored borders."""
    return Panel(
        content,
        title=f"🦾 {title}" if title else "",
        border_style=border_style,
        padding=(1, 2),
    )


def make_gauge_panel(used_mb: int, total_mb: int, label: str = "Memory", color: str = "green") -> Panel:
    """Create a gauge panel with percentage bar."""
    if total_mb > 0:
        percent = (used_mb / total_mb) * 100
    else:
        percent = 0

    # Determine color based on usage
    if percent > 90:
        color = "red"
    elif percent > 70:
        color = "yellow"

    bar = gauge_bar(percent, "", width=30, color=color)
    text = Text.assemble(
        f"{label}: ",
        f"[bold]{used_mb}[/bold] / {total_mb} MB  ",
        bar,
    )
    return Panel(text, title=label, border_style=color)


def make_stat_line(label: str, value: str, icon: str = "•", color: str = "cyan") -> Text:
    """Create a one-line stat display."""
    return Text.assemble(
        f"[{color}]{icon}[/{color}] ",
        f"{label}: ",
        f"[bold white]{value}[/bold white]",
    )
