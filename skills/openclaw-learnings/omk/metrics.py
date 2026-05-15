"""OMK Metrics Extraction Engine.

Reads data from Hermes Agent's session store, logs, filesystem,
and processes to build a comprehensive operational metrics snapshot.
Designed to be lightweight — no network calls, reads local data only.
"""

import json
import os
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import psutil
except ImportError:
    psutil = None


# =========================================================================
# Hermes Home Resolution
# =========================================================================

def get_hermes_home() -> Path:
    """Resolve HERMES_HOME, fallback to ~/.hermes."""
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env)
    return Path.home() / ".hermes"


# =========================================================================
# Session Metrics
# =========================================================================

def get_session_stats() -> Dict[str, Any]:
    """Read session DB stats from SQLite store."""
    herm_home = get_hermes_home()
    db_path = herm_home / "state.db"

    if not db_path.exists():
        return {"error": "state.db not found", "total": 0}

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Total sessions
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total = cursor.fetchone()[0]

        # Total size
        size_bytes = db_path.stat().st_size

        # Recent sessions (last 24h) — started_at is REAL (Unix timestamp)
        cutoff = time.time() - (24 * 3600)
        cursor.execute(
            "SELECT COUNT(*) FROM sessions WHERE started_at > ?",
            (cutoff,)
        )
        active_24h = cursor.fetchone()[0]

        # Compression stats (if available)
        try:
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE compressed = 1")
            compressed = cursor.fetchone()[0]
        except Exception:
            compressed = 0

        # Top models
        try:
            cursor.execute("""
                SELECT model, COUNT(*) as count 
                FROM sessions 
                GROUP BY model 
                ORDER BY count DESC 
                LIMIT 5
            """)
            top_models = [{"model": row[0], "count": row[1]} for row in cursor.fetchall()]
        except Exception:
            top_models = []

        # Oldest and newest session timestamps
        try:
            cursor.execute("SELECT MIN(started_at), MAX(started_at) FROM sessions")
            row = cursor.fetchone()
            oldest = row[0] if row[0] else None
            newest = row[1] if row[1] else None
        except Exception:
            oldest = newest = None

        conn.close()

        return {
            "total": total,
            "size_bytes": size_bytes,
            "size_human": _human_size(size_bytes),
            "active_24h": active_24h,
            "oldest": oldest,
            "newest": newest,
            "compressed": compressed,
            "top_models": top_models,
            "status": "ok",
        }

    except Exception as e:
        return {"error": str(e), "total": 0, "status": "error"}


def get_session_store_size() -> Dict[str, Any]:
    """Calculate total size of session files."""
    herm_home = get_hermes_home()
    sessions_dir = herm_home / "sessions"

    if not sessions_dir.exists():
        return {"size_bytes": 0, "size_human": "0 B", "file_count": 0}

    total = 0
    count = 0
    for root, dirs, files in os.walk(sessions_dir):
        for f in files:
            p = Path(root) / f
            if p.is_file():
                total += p.stat().st_size
                count += 1

    return {
        "size_bytes": total,
        "size_human": _human_size(total),
        "file_count": count,
    }


# =========================================================================
# Token / Cost Metrics
# =========================================================================

def get_token_usage(days: int = 1) -> Dict[str, Any]:
    """Estimate token usage from session records."""
    herm_home = get_hermes_home()
    db_path = herm_home / "state.db"

    if not db_path.exists():
        return {"input_tokens": 0, "output_tokens": 0, "cost_estimate": 0.0}

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cutoff = time.time() - (days * 86400)

        cursor.execute("""
            SELECT
                COALESCE(SUM(input_tokens), 0),
                COALESCE(SUM(output_tokens), 0),
                COALESCE(SUM(estimated_cost_usd), 0.0),
                COUNT(*)
            FROM sessions
            WHERE started_at > ?
        """, (cutoff,))
        row = cursor.fetchone()
        input_tokens = row[0] or 0
        output_tokens = row[1] or 0
        total_cost = row[2] or 0.0
        session_count = row[3] or 0

        conn.close()

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_estimate": total_cost,
            "session_count": session_count,
        }

    except Exception as e:
        return {"error": str(e), "input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "cost_estimate": 0.0}


def _human_size(n: int) -> str:
    """Format bytes to human-readable string."""
    if n < 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


# =========================================================================
# Log / Error Metrics
# =========================================================================

def get_error_summary(hours: int = 24) -> Dict[str, Any]:
    """Scan logs for errors and warnings in the last N hours."""
    herm_home = get_hermes_home()
    log_dir = herm_home / "logs"
    errors = []
    warnings = []
    info_count = 0

    if not log_dir.exists():
        return {"errors": [], "warnings": [], "info_count": 0}

    cutoff_time = datetime.now() - timedelta(hours=hours)
    cutoff_str = cutoff_time.strftime("%Y-%m-%d %H:%M:%S")

    # Scan gateway.log
    gateway_log = log_dir / "gateway.log"
    if gateway_log.exists():
        try:
            with open(gateway_log, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    ts_text = line[:19] if len(line) > 19 else ""
                    if not _is_recent(ts_text, cutoff_str):
                        continue

                    if "error" in line.lower() or "exception" in line.lower():
                        errors.append(line[:200])
                    elif "warn" in line.lower():
                        warnings.append(line[:200])
                    elif "info" in line.lower():
                        info_count += 1
        except Exception:
            pass

    # Scan hermes.log if exists
    hermes_log = log_dir / "hermes.log"
    if hermes_log.exists():
        try:
            with open(hermes_log, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    ts_text = line[:19] if len(line) > 19 else ""
                    if not _is_recent(ts_text, cutoff_str):
                        continue

                    if "error" in line.lower() or "exception" in line.lower():
                        errors.append(line[:200])
                    elif "warn" in line.lower():
                        warnings.append(line[:200])
        except Exception:
            pass

    return {
        "errors": errors[-20:],   # Last 20
        "warnings": warnings[-20:],
        "error_count": len(errors),
        "warning_count": len(warnings),
        "info_count": info_count,
    }


def _is_recent(ts_text: str, cutoff: str) -> bool:
    """Check if timestamp string is more recent than cutoff."""
    if not ts_text or len(ts_text) < 19:
        return True
    try:
        return ts_text >= cutoff
    except Exception:
        return True


# =========================================================================
# Cron / Job Metrics
# =========================================================================

def get_cron_stats() -> Dict[str, Any]:
    """Get cron job statistics."""
    herm_home = get_hermes_home()

    # Check for cron state files
    state_files = [
        herm_home / "cron" / "jobs.json",
        herm_home / "cron" / "jobs-state.json",
    ]

    jobs = []
    for sf in state_files:
        if sf.exists():
            try:
                with open(sf, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        jobs.extend(data)
                    elif isinstance(data, dict):
                        if "jobs" in data:
                            jobs.extend(data["jobs"])
                        else:
                            jobs.append(data)
            except Exception:
                pass

    running = sum(1 for j in jobs if j.get("status") == "running")
    scheduled = sum(1 for j in jobs if j.get("status") in ("scheduled", "pending"))
    failed = sum(1 for j in jobs if j.get("status") == "failed")
    paused = sum(1 for j in jobs if j.get("status") == "paused")

    return {
        "total": len(jobs),
        "running": running,
        "scheduled": scheduled,
        "failed": failed,
        "paused": paused,
        "jobs": jobs[:10],  # First 10 for display
    }


# =========================================================================
# Skills Metrics
# =========================================================================

def get_skills_stats() -> Dict[str, Any]:
    """Count installed skills."""
    herm_home = get_hermes_home()
    skills_dir = herm_home / "skills"

    if not skills_dir.exists():
        return {"total": 0, "categories": []}

    categories = {}
    total = 0
    for item in skills_dir.iterdir():
        if item.is_dir():
            total += 1
            parent = item.parent.name
            if parent not in categories:
                categories[parent] = 0
            categories[parent] += 1
            # Count nested
            for sub in item.iterdir():
                if sub.is_dir() and (sub / "SKILL.md").exists():
                    total += 1

    return {
        "total": total,
        "categories": categories,
    }


# =========================================================================
# System / Process Metrics
# =========================================================================

def get_system_stats() -> Dict[str, Any]:
    """Get system resource usage."""
    result = {}

    # Memory
    if psutil:
        mem = psutil.virtual_memory()
        result["memory"] = {
            "used_mb": round(mem.used / (1024 ** 2)),
            "total_mb": round(mem.total / (1024 ** 2)),
            "percent": mem.percent,
        }
    else:
        result["memory"] = {"used_mb": 0, "total_mb": 0, "percent": 0, "note": "pip install psutil for memory tracking"}

    # Disk usage for ~/.hermes
    herm_home = get_hermes_home()
    if herm_home.exists():
        try:
            usage = shutil_disk_usage(str(herm_home))
            result["hermes_disk"] = {
                "used_mb": round(usage.used / (1024 ** 2)),
                "total_mb": round(usage.total / (1024 ** 2)),
                "used_human": _human_size(usage.used),
                "total_human": _human_size(usage.total),
                "percent": round(usage.used / usage.total * 100, 1) if usage.total > 0 else 0,
            }
        except Exception:
            result["hermes_disk"] = {"used_mb": 0, "total_mb": 0, "percent": 0}
    else:
        result["hermes_disk"] = {"used_mb": 0, "total_mb": 0, "percent": 0}

    return result


def shutil_disk_usage(path: str):
    """Get disk usage without importing shutil (to avoid circular)."""
    st = os.statvfs(path)
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    free = st.f_bfree * st.f_frsize
    from collections import namedtuple
    usage = namedtuple("usage", ["total", "used", "free"])
    return usage(total, used, free)


def get_hermes_processes() -> List[Dict[str, Any]]:
    """Find all running Hermes-related processes."""
    processes = []

    if not psutil:
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if "hermes" in line.lower() or "python" in line.lower():
                    if "hermes" in line.lower():
                        parts = line.split()
                        if len(parts) >= 11:
                            processes.append({
                                "pid": int(parts[1]) if parts[1].isdigit() else 0,
                                "user": parts[0],
                                "cpu": float(parts[2]),
                                "mem": float(parts[3]),
                                "command": " ".join(parts[10:]),
                            })
        except Exception:
            pass
        return processes

    # psutil approach
    current_pid = os.getpid()
    for proc in psutil.process_iter(["pid", "name", "cmdline", "cpu_percent", "memory_percent"]):
        try:
            cmdline = proc.info.get("cmdline") or []
            cmd_str = " ".join(cmdline)
            if "hermes" in cmd_str.lower() or (
                "python" in cmd_str.lower() and "hermes" in cmd_str.lower()
            ):
                is_child = proc.info.get("ppid") == current_pid

                processes.append({
                    "pid": proc.info["pid"],
                    "ppid": proc.ppid() if hasattr(proc, "ppid") else None,
                    "name": proc.info["name"],
                    "command": cmd_str[:120],
                    "cpu": proc.info.get("cpu_percent", 0),
                    "mem": proc.info.get("memory_percent", 0),
                    "memory_mb": round(proc.memory_info().rss / (1024 ** 2), 1) if hasattr(proc, "memory_info") else 0,
                    "status": proc.status() if hasattr(proc, "status") else "unknown",
                    "is_child": is_child,
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return processes


# =========================================================================
# Full Metrics Snapshot
# =========================================================================

def collect_full_snapshot(verbosity: str = "full") -> Dict[str, Any]:
    """Collect all metrics for the OMK dashboard.

    Args:
        verbosity: 'minimal', 'compact', or 'full'
    """
    snap = {
        "timestamp": datetime.now().isoformat(),
        "hermes_home": str(get_hermes_home()),
    }

    # Always collect
    snap["system"] = get_system_stats()
    snap["sessions"] = get_session_stats()
    snap["token_usage"] = get_token_usage()

    if verbosity in ("compact", "full"):
        snap["errors"] = get_error_summary()
        snap["cron"] = get_cron_stats()
        snap["skills"] = get_skills_stats()
        snap["processes"] = get_hermes_processes()

    if verbosity == "full":
        snap["session_files"] = get_session_store_size()
        snap["token_usage_7d"] = get_token_usage(7)
        snap["token_usage_30d"] = get_token_usage(30)

    return snap
