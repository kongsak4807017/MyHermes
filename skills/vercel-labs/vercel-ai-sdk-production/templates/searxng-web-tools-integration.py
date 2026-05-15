#!/usr/bin/env python3
"""
Template for adding SearXNG as a web search backend in Hermes Agent.

Copy this into tools/web_tools.py and adjust as needed.
"""

# ─── SearXNG Helpers ─────────────────────────────────────────────────────────

def _get_searxng_url() -> str:
    """Return the SearXNG instance URL from config or env."""
    config = _load_web_config()
    url = config.get("searxng_url", "")
    if url:
        return url.rstrip("/")
    env_url = os.getenv("SEARXNG_URL", "")
    if env_url:
        return env_url.rstrip("/")
    return "http://localhost:8888"


def _is_searxng_available() -> bool:
    """Check if SearXNG is reachable."""
    url = _get_searxng_url()
    try:
        import urllib.request
        req = urllib.request.Request(
            f"{url}/healthz",
            method="GET",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        pass
    # Fallback: try a simple search
    try:
        import urllib.request
        req = urllib.request.Request(
            f"{url}/search?q=test&format=json",
            method="GET",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _start_searxng() -> bool:
    """Auto-start SearXNG if not running. Returns True if successfully started."""
    import subprocess, time, os
    
    if _is_searxng_available():
        return True
    
    # Try common SearXNG locations with various venv paths
    possible_combos = [
        ("/tmp/searxng", "/tmp/searxng-venv"),
        ("/tmp/searxng", "/tmp/searxng/.venv"),
        ("/tmp/searxng", "/tmp/searxng/venv"),
        (os.path.expanduser("~/searxng"), os.path.expanduser("~/searxng/searxng-venv")),
        (os.path.expanduser("~/searxng"), os.path.expanduser("~/searxng/.venv")),
    ]
    
    for source_path, venv_path in possible_combos:
        if not os.path.exists(source_path):
            continue
        venv_python = os.path.join(venv_path, "bin/python")
        if not os.path.exists(venv_python):
            continue
        settings = os.path.join(source_path, "settings.yml")
        if not os.path.exists(settings):
            continue
        try:
            env = os.environ.copy()
            env["SEARXNG_SETTINGS_PATH"] = settings
            proc = subprocess.Popen(
                [venv_python, "-m", "searx.webapp"],
                cwd=source_path,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            for _ in range(15):
                time.sleep(1)
                if _is_searxng_available():
                    return True
        except Exception:
            pass
    
    return False


def _searxng_search(query: str, limit: int = 10) -> dict:
    """Search using local SearXNG instance and return results as a dict."""
    from tools.interrupt import is_interrupted
    if is_interrupted():
        return {"error": "Interrupted", "success": False}

    # Auto-start if not available
    if not _is_searxng_available():
        if not _start_searxng():
            return {"error": "SearXNG is not running and could not be auto-started", "success": False}

    url = _get_searxng_url()
    
    import urllib.parse
    import urllib.request

    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "language": "en",
    })
    req = urllib.request.Request(
        f"{url}/search?{params}",
        method="GET",
        headers={"Accept": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"SearXNG search failed: {e}", "success": False}

    web_results = []
    for i, result in enumerate(data.get("results", [])[:limit]):
        web_results.append({
            "url": result.get("url", ""),
            "title": result.get("title", ""),
            "description": result.get("content", "")[:300],
            "position": i + 1,
            "engine": result.get("engine", ""),
        })

    return {"success": True, "data": {"web": web_results}}
