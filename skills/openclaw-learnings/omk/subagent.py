"""OMK Subagent - AI Orchestrator for Hermes delegation.

Phase D: Parallel task execution + result synthesis.
"""

import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional


def run_monitor_task() -> Dict[str, Any]:
    """Run monitor and return snapshot."""
    from .metrics import collect_full_snapshot
    return {"task": "monitor", "result": collect_full_snapshot("compact")}


def run_status_task() -> Dict[str, Any]:
    """Run status and return snapshot."""
    from .metrics import collect_full_snapshot
    return {"task": "status", "result": collect_full_snapshot("compact")}


def run_health_task(days: int = 7) -> Dict[str, Any]:
    """Run health check and return results."""
    from .metrics import collect_full_snapshot
    from .analytics import compute_health_score, detect_anomalies, get_predictive_insights
    snap = collect_full_snapshot("compact")
    return {
        "task": "health",
        "result": {
            "health": compute_health_score(snap),
            "anomalies": detect_anomalies(days=days),
            "insights": get_predictive_insights(days=days),
        }
    }


def run_export_task(output_path: str) -> Dict[str, Any]:
    """Export full metrics to file."""
    from .metrics import collect_full_snapshot
    snap = collect_full_snapshot("full")
    with open(output_path, "w") as f:
        json.dump(snap, f, indent=2, default=str)
    return {"task": "export", "result": {"output_path": output_path, "keys": list(snap.keys())}}


def run_analytics_task(days: int = 7) -> Dict[str, Any]:
    """Run full analytics suite."""
    from .metrics import collect_full_snapshot
    from .analytics import compute_health_score, detect_anomalies, get_predictive_insights
    snap = collect_full_snapshot("compact")
    return {
        "task": "analytics",
        "result": {
            "timestamp": time.time(),
            "health": compute_health_score(snap),
            "anomalies": detect_anomalies(days=days),
            "insights": get_predictive_insights(days=days),
        }
    }


# Task registry
_TASK_REGISTRY = {
    "monitor": run_monitor_task,
    "status": run_status_task,
    "health": run_health_task,
    "export": run_export_task,
    "analytics": run_analytics_task,
}


def _execute_single_task(task_name: str, task_config: Optional[Dict] = None) -> Dict[str, Any]:
    """Execute a single task by name."""
    handler = _TASK_REGISTRY.get(task_name)
    if not handler:
        return {"task": task_name, "error": f"Unknown task: {task_name}"}
    try:
        if task_config:
            return handler(**task_config)
        return handler()
    except Exception as e:
        return {"task": task_name, "error": str(e)}


def run_subagent_mode(task: str, context: Optional[str] = None) -> int:
    """Run OMK in subagent mode (called by Hermes delegate_task).

    Args:
        task: Task description or JSON task plan.
        context: JSON context string.

    Task plan format (JSON):
        {
            "tasks": ["status", "health", "analytics"],
            "parallel": true,
            "days": 7
        }
    """
    ctx = {}
    if context:
        try:
            ctx = json.loads(context)
        except json.JSONDecodeError:
            pass

    # Parse task plan
    task_plan = {"tasks": [], "parallel": False, "days": 7}
    try:
        parsed = json.loads(task) if task.strip().startswith("{") else {}
        if "tasks" in parsed:
            task_plan.update(parsed)
        else:
            task_plan["tasks"] = [task]
    except Exception:
        task_plan["tasks"] = [task]

    days = ctx.get("days", task_plan.get("days", 7))
    parallel = task_plan.get("parallel", False)
    tasks = task_plan.get("tasks", [task])

    results = []

    if parallel and len(tasks) > 1:
        # Parallel execution
        with ThreadPoolExecutor(max_workers=min(len(tasks), 4)) as executor:
            futures = {}
            for t in tasks:
                config = {"days": days} if t in ("health", "analytics") else {}
                if t == "export":
                    config["output_path"] = ctx.get("output", "omk_export.json")
                futures[executor.submit(_execute_single_task, t, config)] = t

            for future in as_completed(futures):
                task_name = futures[future]
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append({"task": task_name, "error": str(e)})
    else:
        # Sequential execution
        for t in tasks:
            config = {"days": days} if t in ("health", "analytics") else {}
            if t == "export":
                config["output_path"] = ctx.get("output", "omk_export.json")
            results.append(_execute_single_task(t, config))

    # Synthesis
    synthesis = _synthesize_results(results)
    output = {
        "synthesis": synthesis,
        "results": results,
        "execution_mode": "parallel" if parallel else "sequential",
        "tasks_requested": tasks,
    }

    print(json.dumps(output, indent=2, default=str))
    return 0


def _synthesize_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Synthesize multiple task results into a unified report."""
    errors = [r for r in results if "error" in r]
    health_results = [r["result"] for r in results if r.get("task") == "health" and "result" in r]
    analytics_results = [r["result"] for r in results if r.get("task") == "analytics" and "result" in r]

    synthesis = {
        "status": "success" if not errors else "partial_failure",
        "tasks_completed": len([r for r in results if "error" not in r]),
        "tasks_failed": len(errors),
        "summary": [],
        "recommendations": [],
    }

    if errors:
        synthesis["summary"].append(f"{len(errors)} task(s) failed: {', '.join(e['error'] for e in errors)}")

    # Aggregate health scores
    all_health = health_results + [a.get("health", {}) for a in analytics_results]
    if all_health:
        scores = [h.get("score", 0) for h in all_health if "score" in h]
        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            synthesis["summary"].append(f"Average health score: {avg_score:.0f}/100 (min: {min_score})")
            if min_score < 50:
                synthesis["recommendations"].append("Critical health detected — investigate immediately")
            elif min_score < 80:
                synthesis["recommendations"].append("Degraded health — review anomaly details")

    # Aggregate anomalies
    all_anomalies = []
    for h in all_health:
        all_anomalies.extend(h.get("reasons", []))
    for a in analytics_results:
        all_anomalies.extend([x["message"] for x in a.get("anomalies", []) if x.get("severity") != "ok"])

    unique_anomalies = list(dict.fromkeys(all_anomalies))
    if unique_anomalies:
        synthesis["summary"].append(f"{len(unique_anomalies)} unique anomaly/reason(s) found")
        for anomaly in unique_anomalies[:3]:
            synthesis["recommendations"].append(f"Address: {anomaly}")

    if not synthesis["recommendations"]:
        synthesis["recommendations"].append("All systems operational — no action required")

    return synthesis


if __name__ == "__main__":
    # Can be called directly for testing
    task = sys.argv[1] if len(sys.argv) > 1 else '{"tasks":["status","health"],"parallel":true}'
    context = sys.argv[2] if len(sys.argv) > 2 else None
    sys.exit(run_subagent_mode(task, context))
