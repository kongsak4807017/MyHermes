"""OMK Analytics — Anomaly detection, health scoring, and predictive insights.

Phase B: Operational Intelligence layer for OMK.
No LLM calls — pure statistical analysis from local data.
"""

import json
import sqlite3
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .metrics import get_hermes_home


# =========================================================================
# Health Score Engine
# =========================================================================

def compute_health_score(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a composite health score (0-100) from metrics snapshot.

    Components:
      - Session health (30%): active sessions vs baseline
      - Error health (25%): error/warning rate vs baseline
      - Token health (20%): token usage trend vs 7-day average
      - System health (15%): memory/disk usage
      - Process health (10%): running processes status
    """
    scores = {}
    reasons = []

    # --- Session Health (30%) ---
    sessions = snapshot.get("sessions", {})
    total = sessions.get("total", 0)
    active_24h = sessions.get("active_24h", 0)
    # Simple heuristic: having recent activity is good
    if total == 0:
        scores["session"] = 50  # Neutral if no data
        reasons.append("No session data available")
    elif active_24h > 0:
        scores["session"] = 100
    else:
        scores["session"] = 70  # Deduction for no recent activity
        reasons.append("No sessions in last 24h")

    # --- Error Health (25%) ---
    errors = snapshot.get("errors", {})
    ec = errors.get("error_count", 0)
    wc = errors.get("warning_count", 0)
    if ec > 10:
        scores["error"] = 0
        reasons.append(f"High error count: {ec}")
    elif ec > 0:
        scores["error"] = max(0, 100 - ec * 15)
        reasons.append(f"{ec} errors in last 24h")
    elif wc > 5:
        scores["error"] = 80
        reasons.append(f"{wc} warnings in last 24h")
    else:
        scores["error"] = 100

    # --- Token Health (20%) ---
    tokens = snapshot.get("token_usage", {})
    total_tokens = tokens.get("total_tokens", 0)
    # Compare with 7-day average if available
    token_7d = snapshot.get("token_usage_7d", {})
    avg_7d = token_7d.get("total_tokens", 0) / 7 if token_7d else 0
    if avg_7d > 0 and total_tokens > avg_7d * 3:
        scores["token"] = 60
        reasons.append("Today's token usage is 3x above 7-day average")
    elif avg_7d > 0 and total_tokens > avg_7d * 2:
        scores["token"] = 80
        reasons.append("Today's token usage is 2x above 7-day average")
    else:
        scores["token"] = 100

    # --- System Health (15%) ---
    system = snapshot.get("system", {})
    mem = system.get("memory", {})
    disk = system.get("hermes_disk", {})
    mem_pct = mem.get("percent", 0)
    disk_pct = disk.get("percent", 0)
    sys_score = 100
    if mem_pct > 90:
        sys_score -= 40
        reasons.append(f"Memory usage critical: {mem_pct}%")
    elif mem_pct > 80:
        sys_score -= 20
        reasons.append(f"Memory usage high: {mem_pct}%")
    if disk_pct > 90:
        sys_score -= 40
        reasons.append(f"Disk usage critical: {disk_pct}%")
    elif disk_pct > 80:
        sys_score -= 20
        reasons.append(f"Disk usage high: {disk_pct}%")
    scores["system"] = max(0, sys_score)

    # --- Process Health (10%) ---
    procs = snapshot.get("processes", [])
    cron = snapshot.get("cron", {})
    failed_jobs = cron.get("failed", 0)
    proc_score = 100
    if failed_jobs > 0:
        proc_score -= min(50, failed_jobs * 10)
        reasons.append(f"{failed_jobs} failed cron jobs")
    if not procs:
        proc_score -= 20
        reasons.append("No Hermes processes detected")
    scores["process"] = max(0, proc_score)

    # Weighted composite
    composite = round(
        scores["session"] * 0.30 +
        scores["error"] * 0.25 +
        scores["token"] * 0.20 +
        scores["system"] * 0.15 +
        scores["process"] * 0.10
    )

    status = "healthy" if composite >= 80 else "degraded" if composite >= 50 else "critical"

    return {
        "score": composite,
        "status": status,
        "components": scores,
        "reasons": reasons if reasons else ["All systems operational"],
    }


# =========================================================================
# Anomaly Detection
# =========================================================================

def detect_anomalies(days: int = 7) -> List[Dict[str, Any]]:
    """Detect anomalies in session and token patterns.

    Returns a list of anomaly objects with type, severity, and message.
    """
    anomalies = []
    herm_home = get_hermes_home()
    db_path = herm_home / "state.db"

    if not db_path.exists():
        return [{"type": "data", "severity": "info", "message": "No state.db found"}]

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # --- Anomaly 1: Error spike (sessions with high tool_call_count but 0 tokens) ---
        cutoff = time.time() - (days * 86400)
        cursor.execute("""
            SELECT COUNT(*) FROM sessions
            WHERE started_at > ? AND tool_call_count > 0
            AND input_tokens = 0 AND output_tokens = 0
        """, (cutoff,))
        empty_tool_sessions = cursor.fetchone()[0]
        if empty_tool_sessions > 0:
            anomalies.append({
                "type": "execution",
                "severity": "warning" if empty_tool_sessions < 5 else "critical",
                "message": f"{empty_tool_sessions} sessions with tool calls but zero tokens (possible failures)",
            })

        # --- Anomaly 2: Token outlier sessions ---
        cursor.execute("""
            SELECT input_tokens + output_tokens as total
            FROM sessions
            WHERE started_at > ? AND input_tokens + output_tokens > 0
            ORDER BY total DESC
            LIMIT 20
        """, (cutoff,))
        token_counts = [row[0] for row in cursor.fetchall()]
        if len(token_counts) >= 5:
            mean = statistics.mean(token_counts)
            stdev = statistics.stdev(token_counts) if len(token_counts) > 1 else 0
            if stdev > 0:
                outliers = [t for t in token_counts if t > mean + 2.5 * stdev]
                if outliers:
                    anomalies.append({
                        "type": "cost",
                        "severity": "warning",
                        "message": f"{len(outliers)} outlier session(s) with >2.5σ token usage (max: {max(outliers):,})",
                    })

        # --- Anomaly 3: Model switching anomaly ---
        cursor.execute("""
            SELECT model, COUNT(*) as cnt FROM sessions
            WHERE started_at > ? AND model IS NOT NULL
            GROUP BY model ORDER BY cnt DESC
        """, (cutoff,))
        model_rows = cursor.fetchall()
        if len(model_rows) >= 3:
            top_count = model_rows[0][1]
            total_count = sum(r[1] for r in model_rows)
            if top_count / total_count < 0.3:
                anomalies.append({
                    "type": "pattern",
                    "severity": "info",
                    "message": f"High model diversity: {len(model_rows)} models used, no dominant model",
                })

        # --- Anomaly 4: Disk growth ---
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE started_at > ?", (cutoff,))
        recent_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE started_at > ? AND started_at <= ?",
                       (cutoff - days * 86400, cutoff))
        prev_count = cursor.fetchone()[0]
        if prev_count > 0 and recent_count > prev_count * 2:
            anomalies.append({
                "type": "growth",
                "severity": "info",
                "message": f"Session count doubled vs previous period ({recent_count} vs {prev_count})",
            })

        conn.close()
    except Exception as e:
        anomalies.append({"type": "system", "severity": "warning", "message": f"Anomaly detection failed: {e}"})

    if not anomalies:
        anomalies.append({"type": "system", "severity": "ok", "message": "No anomalies detected"})

    return anomalies


# =========================================================================
# Predictive Insights
# =========================================================================

def get_predictive_insights(days: int = 7) -> List[str]:
    """Generate simple predictive insights based on trends.

    No ML — just moving averages and linear extrapolation.
    """
    insights = []
    herm_home = get_hermes_home()
    db_path = herm_home / "state.db"

    if not db_path.exists():
        return ["No data available for predictions"]

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Daily token totals for last N days
        cutoff = time.time() - (days * 86400)
        cursor.execute("""
            SELECT
                date(started_at, 'unixepoch') as day,
                SUM(COALESCE(input_tokens, 0) + COALESCE(output_tokens, 0)) as total
            FROM sessions
            WHERE started_at > ?
            GROUP BY day
            ORDER BY day
        """, (cutoff,))
        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 3:
            return ["Insufficient data for trend analysis (need >= 3 days)"]

        totals = [r[1] for r in rows]
        avg = statistics.mean(totals)
        recent_avg = statistics.mean(totals[-3:])

        if recent_avg > avg * 1.5:
            insights.append(f"Token usage accelerating: last-3-day avg is {recent_avg/avg:.1f}x above {days}-day average")
        elif recent_avg < avg * 0.5:
            insights.append(f"Token usage declining: last-3-day avg is {recent_avg/avg:.1f}x below {days}-day average")

        # Simple linear projection
        if len(totals) >= 2:
            trend = totals[-1] - totals[-2]
            if trend > 0:
                insights.append(f"Upward trend: +{trend:,} tokens vs previous day")
            elif trend < 0:
                insights.append(f"Downward trend: {trend:,} tokens vs previous day")

        # Cost projection (if cost data exists)
        if any(t > 100000 for t in totals):
            insights.append("High-volume days detected — consider reviewing model selection for cost optimization")

        if not insights:
            insights.append("Usage patterns stable — no significant trends detected")

    except Exception as e:
        insights.append(f"Prediction engine error: {e}")

    return insights


# =========================================================================
# Helpers
# =========================================================================

import time


def _get_db_connection():
    """Get a SQLite connection to state.db."""
    db_path = get_hermes_home() / "state.db"
    return sqlite3.connect(str(db_path))
