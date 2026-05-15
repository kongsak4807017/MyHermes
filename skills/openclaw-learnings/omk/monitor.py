"""OMK Live Monitor - Real-time dashboard with auto-refresh.

Keyboard controls:
  q: Quit
  p: Pause/unpause refresh
  r: Force refresh
  s: Change refresh speed (2s / 5s / 10s)
"""

import sys
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .metrics import collect_full_snapshot, get_hermes_home


def _set_raw_mode():
    """Put stdin into raw (single-char) mode. Unix only."""
    import termios, tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    return old


def _restore_mode(old):
    """Restore stdin terminal settings."""
    import termios
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSADRAIN, old)


class LiveMonitor:
    """Real-time OMK monitor with keyboard controls."""

    REFRESH_RATES = [2, 5, 10]  # seconds

    def __init__(self):
        self.refresh_idx = 0  # Start with 2 seconds
        self.paused = False
        self.running = True
        self.force_refresh = False
        self.last_snapshot: Optional[Dict] = None
        self.history: List[Dict] = []  # For sparklines
        self.max_history = 60  # Keep last 60 data points
        self._lock = threading.Lock()

    def _read_keyboard(self):
        """Background thread: read single keys without Enter."""
        try:
            old = _set_raw_mode()
        except Exception:
            # Non-tty or Windows without termios — skip raw keyboard
            return

        try:
            while self.running:
                import select
                # Small timeout so we can check self.running frequently
                ready, _, _ = select.select([sys.stdin], [], [], 0.2)
                if not ready:
                    continue
                ch = sys.stdin.read(1)
                if not ch:
                    continue
                with self._lock:
                    if ch.lower() == "q":
                        self.running = False
                    elif ch.lower() == "p":
                        self.paused = not self.paused
                    elif ch.lower() == "r":
                        self.force_refresh = True
                    elif ch.lower() == "s":
                        self.refresh_idx = (self.refresh_idx + 1) % len(self.REFRESH_RATES)
        finally:
            _restore_mode(old)

    def _make_layout(self) -> Layout:
        """Create the monitor layout."""
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right"),
        )
        layout["left"].split(
            Layout(name="sessions"),
            Layout(name="tokens"),
        )
        layout["right"].split(
            Layout(name="system"),
            Layout(name="processes"),
        )
        return layout

    def _header_text(self) -> Text:
        """Create header with status."""
        with self._lock:
            status = "⏸ PAUSED" if self.paused else "▶ LIVE"
            refresh = self.REFRESH_RATES[self.refresh_idx]
        text = Text()
        text.append("🦾 OMK Live Monitor ", style="bold cyan")
        text.append(f"| {status} ", style="yellow" if self.paused else "green")
        text.append(f"| Refresh: {refresh}s ", style="dim")
        text.append("| [q]uit [p]ause [r]efresh [s]peed", style="dim")
        return text

    def _footer_text(self, snapshot: Dict) -> Text:
        """Create footer with stats."""
        text = Text()
        ts = snapshot.get("timestamp", "unknown")
        text.append(f"Last update: {ts} | ", style="dim")
        sessions = snapshot.get("sessions", {})
        text.append(f"Sessions: {sessions.get('total', 0)} | ", style="dim")
        procs = len(snapshot.get("processes", []))
        text.append(f"Processes: {procs}", style="dim")
        return text

    def _system_panel(self, snapshot: Dict) -> Panel:
        """Create system stats panel."""
        system = snapshot.get("system", {})
        memory = system.get("memory", {})
        disk = system.get("hermes_disk", {})

        content = []
        mem_pct = memory.get("percent", 0)
        mem_color = "green" if mem_pct < 70 else "yellow" if mem_pct < 90 else "red"
        content.append(f"💾 Memory: {memory.get('used_mb', 0)} / {memory.get('total_mb', 0)} MB")
        content.append(f"   [{mem_color}]{'█' * int(mem_pct/5)}{'░' * (20-int(mem_pct/5))}[/{mem_color}] {mem_pct}%")

        disk_pct = disk.get("percent", 0)
        disk_color = "green" if disk_pct < 70 else "yellow" if disk_pct < 90 else "red"
        content.append(f"")
        content.append(f"💿 Disk: {disk.get('used_human', '0 B')} / {disk.get('total_human', '0 B')}")
        content.append(f"   [{disk_color}]{'█' * int(disk_pct/5)}{'░' * (20-int(disk_pct/5))}[/{disk_color}] {disk_pct}%")

        return Panel(
            "\n".join(content),
            title="[bold]System[/bold]",
            border_style="cyan",
            box=box.ROUNDED,
        )

    def _sessions_panel(self, snapshot: Dict) -> Panel:
        """Create sessions panel."""
        sessions = snapshot.get("sessions", {})

        content = []
        content.append(f"📊 Total: {sessions.get('total', 0)}")
        content.append(f"📁 Size: {sessions.get('size_human', '0 B')}")
        content.append(f"🟢 Active 24h: {sessions.get('active_24h', 0)}")

        # Top models
        top = sessions.get("top_models", [])
        if top:
            content.append("")
            content.append("[bold]Top Models:[/bold]")
            for m in top[:3]:
                model_name = m.get('model', 'unknown')[:20]
                content.append(f"  • {model_name}: {m.get('count', 0)}")

        return Panel(
            "\n".join(content),
            title="[bold]Sessions[/bold]",
            border_style="green",
            box=box.ROUNDED,
        )

    def _tokens_panel(self, snapshot: Dict) -> Panel:
        """Create token usage panel with mini sparkline."""
        tokens = snapshot.get("token_usage", {})

        content = []
        inp = tokens.get("input_tokens", 0)
        out = tokens.get("output_tokens", 0)
        total = tokens.get("total_tokens", 0)
        cost = tokens.get("cost_estimate", 0)

        content.append(f"📥 Input: {inp:,}")
        content.append(f"📤 Output: {out:,}")
        content.append(f"🔢 Total: {total:,}")
        content.append(f"💰 Cost: ${cost:.4f}")

        # Mini sparkline from history
        with self._lock:
            hist = list(self.history)
        if len(hist) > 1:
            content.append("")
            spark = self._make_sparkline([h.get("token_usage", {}).get("total_tokens", 0) for h in hist[-20:]])
            content.append(f"Trend: {spark}")

        return Panel(
            "\n".join(content),
            title="[bold]Tokens (Today)[/bold]",
            border_style="yellow",
            box=box.ROUNDED,
        )

    def _make_sparkline(self, values: List[int]) -> str:
        """Create ASCII sparkline from values."""
        if not values or len(values) < 2:
            return "─" * 10

        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            return "─" * min(len(values), 20)

        bars = " ▁▂▃▄▅▆▇█"
        result = ""
        for v in values[-20:]:  # Last 20 points
            idx = int((v - min_val) / (max_val - min_val) * 8)
            result += bars[min(idx, 8)]
        return result

    def _processes_panel(self, snapshot: Dict) -> Panel:
        """Create processes panel."""
        processes = snapshot.get("processes", [])

        if not processes:
            return Panel(
                "No Hermes processes found",
                title="[bold]Processes[/bold]",
                border_style="cyan",
                box=box.ROUNDED,
            )

        table = Table(show_header=True, header_style="bold", box=None)
        table.add_column("PID", justify="right", style="cyan", width=6)
        table.add_column("Name", style="white", width=15)
        table.add_column("CPU%", justify="right", width=6)
        table.add_column("Mem MB", justify="right", width=8)
        table.add_column("Status", width=10)

        for proc in processes[:8]:  # Show top 8
            pid = proc.get("pid", 0)
            name = proc.get("name", "unknown")[:14]
            cpu = proc.get("cpu", 0)
            mem = proc.get("memory_mb", 0)
            status = "🟢 child" if proc.get("is_child") else "🟡 worker"

            table.add_row(
                str(pid),
                name,
                f"{cpu:.1f}",
                f"{mem:.1f}",
                status,
            )

        return Panel(
            table,
            title=f"[bold]Processes ({len(processes)} total)[/bold]",
            border_style="cyan",
            box=box.ROUNDED,
        )

    def _update(self, layout: Layout):
        """Update all panels with fresh data."""
        with self._lock:
            do_refresh = not self.paused or self.force_refresh
            if self.force_refresh:
                self.force_refresh = False

        if do_refresh:
            self.last_snapshot = collect_full_snapshot("compact")
            with self._lock:
                self.history.append(self.last_snapshot)
                if len(self.history) > self.max_history:
                    self.history.pop(0)

        if self.last_snapshot:
            layout["header"].update(Panel(self._header_text(), box=box.SIMPLE))
            layout["sessions"].update(self._sessions_panel(self.last_snapshot))
            layout["tokens"].update(self._tokens_panel(self.last_snapshot))
            layout["system"].update(self._system_panel(self.last_snapshot))
            layout["processes"].update(self._processes_panel(self.last_snapshot))
            layout["footer"].update(Panel(self._footer_text(self.last_snapshot), box=box.SIMPLE))

    def run(self):
        """Run the live monitor."""
        if not RICH_AVAILABLE:
            print("Error: rich library required. pip install rich")
            return 1

        from rich.console import Console

        console = Console(force_terminal=True)

        # Initial data load
        self.last_snapshot = collect_full_snapshot("compact")
        self.history = [self.last_snapshot]

        layout = self._make_layout()

        # Start keyboard listener thread
        kb_thread = threading.Thread(target=self._read_keyboard, daemon=True)
        kb_thread.start()

        try:
            with Live(
                layout,
                console=console,
                refresh_per_second=4,
                transient=True,
                screen=False
            ) as live:
                while self.running:
                    self._update(layout)
                    with self._lock:
                        refresh = self.REFRESH_RATES[self.refresh_idx]
                    time.sleep(refresh)
        finally:
            with self._lock:
                self.running = False
            kb_thread.join(timeout=1.0)
            console.print()

        return 0


def run_monitor():
    """Entry point for omk monitor command."""
    monitor = LiveMonitor()
    return monitor.run()
