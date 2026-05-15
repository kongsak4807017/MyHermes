---
name: self-hosted-search
description: "Self-hosted search infrastructure: SearXNG metasearch, local deployment, API integration, and troubleshooting."
version: 1.0.0
author: Hermes Agent
license: MIT
dependencies: [docker, python]
metadata:
  hermes:
    tags: [SearXNG, Search, Metasearch, Self-Hosted, Privacy, API]
---

# Self-Hosted Search

Running SearXNG or similar self-hosted metasearch engines for privacy-respecting, multi-engine search with API access for AI tools.

## When to use

**Use when:**
- Need privacy-respecting web search for AI agents
- Want to aggregate multiple search engines (Google, Bing, DuckDuckGo, Brave)
- Need JSON API for programmatic search from AI tools
- Want to avoid rate limits from direct search engine APIs

## Quick Start

### SearXNG Docker

```bash
docker run -d \
  -p 8888:8080 \
  -v searxng:/etc/searxng \
  searxng/searxng
```

### Python Virtual Environment

```bash
python -m venv /tmp/searxng-venv
source /tmp/searxng-venv/bin/activate
pip install searxng
```

## Core Configuration

### Enable JSON API

Edit `settings.yml`:

```yaml
search:
  formats:
    - html
    - json
    - rss

server:
  limiter: false
  bind_address: "0.0.0.0"
  port: 8888
```

### API Usage

```bash
# Web search
curl "http://localhost:8888/search?q=breaking+news&format=json"

# With time filter (day/week/month/year)
curl "http://localhost:8888/search?q=news&format=json&time_range=day"

# Image search
curl "http://localhost:8888/search?q=cats&format=json&categories=images"
```

## Integration with AI Tools

### Standalone Python

```python
import requests, json

def searxng_search(query, time_range=None):
    url = f"http://localhost:8888/search?q={query}&format=json"
    if time_range:
        url += f"&time_range={time_range}"
    r = requests.get(url)
    return r.json().get("results", [])
```

### Integrating into Hermes Agent web_tools.py

To make SearXNG the default web search backend for Hermes Agent:

**1. Add SearXNG helpers to `web_tools.py`:**

```python
def _get_searxng_url() -> str:
    """Return SearXNG URL from config (web.searxng_url), env (SEARXNG_URL), or default."""
    config = _load_web_config()
    url = config.get("searxng_url", "")
    if url:
        return url.rstrip("/")
    env_url = os.getenv("SEARXNG_URL", "")
    if env_url:
        return env_url.rstrip("/")
    return "http://localhost:8888"


def _is_searxng_available() -> bool:
    """Check if SearXNG is reachable via healthz or a test search."""
    url = _get_searxng_url()
    for endpoint in [f"{url}/healthz", f"{url}/search?q=test&format=json"]:
        try:
            import urllib.request
            req = urllib.request.Request(endpoint, method="GET", headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
    return False


def _searxng_search(query: str, limit: int = 10) -> dict:
    """Search using SearXNG and return normalized results."""
    import urllib.parse, urllib.request
    
    url = _get_searxng_url()
    params = urllib.parse.urlencode({"q": query, "format": "json", "language": "en"})
    req = urllib.request.Request(f"{url}/search?{params}", method="GET", headers={"Accept": "application/json"})
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
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
```

**2. Register in backend dispatch:**

```python
def _get_backend() -> str:
    configured = (_load_web_config().get("backend") or "").lower().strip()
    if configured in ("parallel", "firecrawl", "tavily", "exa", "searxng"):
        return configured
    
    # Auto-detect: SearXNG first (free, no API key), then paid backends
    backend_candidates = (
        ("searxng", _is_searxng_available()),
        ("firecrawl", _has_env("FIRECRAWL_API_KEY") or ...),
        ("parallel", _has_env("PARALLEL_API_KEY")),
        ("tavily", _has_env("TAVILY_API_KEY")),
        ("exa", _has_env("EXA_API_KEY")),
    )
    for backend, available in backend_candidates:
        if available:
            return backend
    return "firecrawl"


def _is_backend_available(backend: str) -> bool:
    if backend == "searxng":
        return _is_searxng_available()
    # ... other backends
```

**3. Add dispatch in `web_search_tool()`:**

```python
if backend == "searxng":
    response_data = _searxng_search(query, limit)
    # ... same debug/logging pattern as other backends
    return json.dumps(response_data, indent=2, ensure_ascii=False)
```

**4. Configure in `~/.hermes/config.yaml`:**

```yaml
web:
  backend: searxng
  searxng_url: http://localhost:8888
```

Or via environment variable:
```bash
export SEARXNG_URL=http://localhost:8888
```

**Priority:** SearXNG is checked first in auto-detection because it's free (no API key required) and privacy-respecting.

## Troubleshooting

See `references/searxng-troubleshooting.md` for common issues and fixes.

## Auto-Start for AI Agents

When SearXNG is the default search backend for an AI agent, implement auto-start so the agent recovers transparently if the service is down:

```python
# In web_search_tool or equivalent:
if not _is_searxng_available():
    if not _start_searxng():
        return {"error": "SearXNG not running and auto-start failed", "success": False}
```

See `references/searxng-auto-start.md` for the full implementation including venv path detection, startup polling, and Docker fallback.

**Key pitfall:** SearXNG source and venv are often in *different* directories (e.g., `/tmp/searxng` + `/tmp/searxng-venv`). Check both separately.

## References

- https://docs.searxng.org
- `references/searxng-troubleshooting.md` — 403 errors, JSON API issues, restart procedures
- `references/hermes-integration.md` — Integrating SearXNG into Hermes Agent web_tools.py as a first-class backend
- `references/searxng-auto-start.md` — Auto-start pattern for AI agents when SearXNG is not running
- `references/searxng-hermes-integration.md` — Full session notes from integrating SearXNG into Hermes (May 2026)
- `templates/searxng-hermes-web-tools.py` — Copy-paste template for adding SearXNG to web_tools.py
- `templates/searxng_tool.py` — Standalone SearXNG search tool for non-Hermes use
- `templates/local_service_backend.py` — Generic pattern for adding local service backends to Hermes
