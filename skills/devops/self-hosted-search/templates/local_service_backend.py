# Template: Integrating a Local Service as a Hermes Tool Backend
#
# This template shows the pattern for adding any self-hosted/local service
# as a first-class backend in Hermes Agent's web_tools.py (or similar tool modules).
#
# Pattern applies to: SearXNG, Ollama, local LLM APIs, self-hosted databases, etc.

# ─── 1. URL/Config Helper ───────────────────────────────────────────────────

def _get_<service>_url() -> str:
    """Return service URL from config, env, or default."""
    config = _load_web_config()  # reads ~/.hermes/config.yaml
    url = config.get("<service>_url", "")
    if url:
        return url.rstrip("/")
    env_url = os.getenv("<SERVICE>_URL", "")
    if env_url:
        return env_url.rstrip("/")
    return "http://localhost:<port>"  # default


# ─── 2. Availability Check ─────────────────────────────────────────────────

def _is_<service>_available() -> bool:
    """Check if service is reachable. Try health endpoint first, then functional endpoint."""
    url = _get_<service>_url()
    for endpoint in [f"{url}/healthz", f"{url}/api/test"]:
        try:
            import urllib.request
            req = urllib.request.Request(endpoint, method="GET", timeout=5)
            with urllib.request.urlopen(req) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
    return False


# ─── 3. Auto-Start (Optional) ──────────────────────────────────────────────

def _start_<service>() -> bool:
    """Auto-start service if not running. Returns True on success."""
    import subprocess, time, os
    
    if _is_<service>_available():
        return True
    
    # Try (source_path, venv_path) combos
    possible_combos = [
        ("/opt/<service>", "/opt/<service>/.venv"),
        ("/tmp/<service>", "/tmp/<service>-venv"),
    ]
    
    for source_path, venv_path in possible_combos:
        if not os.path.exists(source_path):
            continue
        venv_python = os.path.join(venv_path, "bin/python")
        if not os.path.exists(venv_python):
            continue
        
        try:
            env = os.environ.copy()
            proc = subprocess.Popen(
                [venv_python, "-m", "<service>.main"],
                cwd=source_path,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            for _ in range(15):
                time.sleep(1)
                if _is_<service>_available():
                    return True
        except Exception:
            pass
    
    return False


# ─── 4. Backend Registration ─────────────────────────────────────────────────

def _get_backend() -> str:
    configured = (_load_web_config().get("backend") or "").lower().strip()
    if configured in ("<service>", "other_backend"):
        return configured
    
    # Auto-detect: local services first (free), then paid APIs
    backend_candidates = (
        ("<service>", _is_<service>_available()),
        ("paid_api", _has_env("PAID_API_KEY")),
    )
    for backend, available in backend_candidates:
        if available:
            return backend
    return "paid_api"


def _is_backend_available(backend: str) -> bool:
    if backend == "<service>":
        return _is_<service>_available()
    # ... other backends


# ─── 5. Tool Dispatch ──────────────────────────────────────────────────────

def <service>_search(query: str, limit: int = 10) -> dict:
    """Main search function. Auto-starts service if needed."""
    if not _is_<service>_available():
        if not _start_<service>():
            return {"error": "Service not running and auto-start failed", "success": False}
    
    # ... perform search via HTTP API
    url = _get_<service>_url()
    # ...
    return {"success": True, "data": {"web": results}}


# ─── 6. Config ─────────────────────────────────────────────────────────────

# ~/.hermes/config.yaml:
# <service>:
#   backend: <service>
#   <service>_url: http://localhost:<port>
