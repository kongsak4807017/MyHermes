#!/usr/bin/env python3
"""
Template: Integrate SearXNG into Hermes Agent web_tools.py

This adds SearXNG as a first-class web search backend alongside
Firecrawl, Exa, Parallel, and Tavily.
"""

# === ADD TO _get_backend() ===
# Add "searxng" to the configured backends tuple:
configured = (_load_web_config().get("backend") or "").lower().strip()
if configured in ("parallel", "firecrawl", "tavily", "exa", "searxng"):
    return configured

# Add searxng as highest-priority fallback candidate:
backend_candidates = (
    ("searxng", _is_searxng_available()),
    ("firecrawl", _has_env("FIRECRAWL_API_KEY") or ...),
    ("parallel", _has_env("PARALLEL_API_KEY")),
    ("tavily", _has_env("TAVILY_API_KEY")),
    ("exa", _has_env("EXA_API_KEY")),
)


# === ADD TO _is_backend_available() ===
if backend == "searxng":
    return _is_searxng_available()


# === ADD TO web_search_tool() dispatch ===
if backend == "searxng":
    response_data = _searxng_search(query, limit)
    debug_call_data["results_count"] = len(response_data.get("data", {}).get("web", []))
    result_json = json.dumps(response_data, indent=2, ensure_ascii=False)
    debug_call_data["final_response_size"] = len(result_json)
    _debug.log_call("web_search_tool", debug_call_data)
    _debug.save()
    return result_json


# === PASTE THESE FUNCTIONS INTO web_tools.py ===

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
    """Auto-start SearXNG if not running."""
    import subprocess, time, os
    
    if _is_searxng_available():
        return True
    
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
    """Search using local SearXNG instance."""
    from tools.interrupt import is_interrupted
    if is_interrupted():
        return {"error": "Interrupted", "success": False}
    
    if not _is_searxng_available():
        if not _start_searxng():
            return {"error": "SearXNG not running and could not be auto-started", "success": False}
    
    url = _get_searxng_url()
    import urllib.parse, urllib.request
    
    params = urllib.parse.urlencode({"q": query, "format": "json", "language": "en"})
    req = urllib.request.Request(f"{url}/search?{params}", headers={"Accept": "application/json"})
    
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
