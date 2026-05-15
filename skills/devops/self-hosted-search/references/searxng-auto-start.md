# SearXNG Auto-Start Pattern

When integrating SearXNG into AI agent tools (e.g., Hermes Agent `web_tools.py`), the service may not be running when a search is requested. Implement auto-start so the agent can recover transparently.

## Auto-Start Implementation

```python
def _start_searxng() -> bool:
    """Auto-start SearXNG if not running. Returns True if successfully started."""
    import subprocess, time, os
    
    # Already running?
    if _is_searxng_available():
        return True
    
    # Try (source_path, venv_path) combos — venv and source may be in different directories
    possible_combos = [
        ("/tmp/searxng", "/tmp/searxng-venv"),     # separate venv dir (common)
        ("/tmp/searxng", "/tmp/searxng/.venv"),     # hidden venv inside source
        ("/tmp/searxng", "/tmp/searxng/venv"),
        (os.path.expanduser("~/searxng"), os.path.expanduser("~/searxng/searxng-venv")),
        (os.path.expanduser("~/searxng"), os.path.expanduser("~/searxng/.venv")),
        (os.path.expanduser("~/.local/searxng"), os.path.expanduser("~/.local/searxng/venv")),
        ("/usr/local/searxng", "/usr/local/searxng/venv"),
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
            # Wait up to 15 seconds for startup
            for _ in range(15):
                time.sleep(1)
                if _is_searxng_available():
                    return True
        except Exception:
            pass
    
    # Fallback: Docker
    try:
        subprocess.run(["docker", "ps"], capture_output=True, timeout=5, check=True)
        subprocess.run([
            "docker", "run", "-d", "--name", "searxng-auto",
            "-p", "8888:8080", "-v", "searxng-data:/etc/searxng",
            "searxng/searxng:latest"
        ], capture_output=True, timeout=30)
        for _ in range(15):
            time.sleep(1)
            if _is_searxng_available():
                return True
    except Exception:
        pass
    
    return False
```

## Key Pitfalls

1. **Venv path separation** — SearXNG source and venv are often in *different* directories (e.g., `/tmp/searxng` + `/tmp/searxng-venv`). Don't assume they're co-located.
2. **SEARXNG_SETTINGS_PATH** — Must be set in the environment when starting, pointing to the actual `settings.yml` file.
3. **Startup time** — SearXNG takes 3-10 seconds to become ready. Loop with 1-second sleeps, not a single long sleep.
4. **Background process** — Use `start_new_session=True` so the process survives the parent.

## Wiring into web_search_tool

```python
def _searxng_search(query: str, limit: int = 10) -> dict:
    # Auto-start if not available
    if not _is_searxng_available():
        if not _start_searxng():
            return {"error": "SearXNG is not running and could not be auto-started", "success": False}
    # ... proceed with search
```

## Real-World Config Locations (WSL)

| Component | Path |
|-----------|------|
| Source code | `/tmp/searxng` |
| Virtual env | `/tmp/searxng-venv` |
| Settings | `/tmp/searxng/settings.yml` |
| Log file | `/tmp/searxng.log` |
