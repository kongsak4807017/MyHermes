# SearXNG + Hermes Agent Integration

Integrating self-hosted SearXNG as a web search backend for Hermes Agent.

## Architecture

```
Hermes web_search_tool()
    └── _get_backend() → "searxng"
        └── _searxng_search() → localhost:8888/search?format=json
```

## Setup Steps

### 1. Install SearXNG

```bash
# Clone and setup
git clone https://github.com/searxng/searxng /tmp/searxng
cd /tmp/searxng
python -m venv searxng-venv
source searxng-venv/bin/activate
pip install -e .

# Create settings.yml
cat > settings.yml << 'EOF'
use_default_settings: true
server:
  secret_key: "dev-secret-key"
  bind_address: "0.0.0.0"
  port: 8888
  limiter: false
search:
  safe_search: 0
  formats:
    - html
    - json
EOF
```

### 2. Configure Hermes

Add to `~/.hermes/config.yaml`:

```yaml
web:
  backend: searxng
  searxng_url: http://localhost:8888
```

### 3. Auto-start Behavior

The `_start_searxng()` function in `web_tools.py` handles auto-start:

- Checks common paths: `/tmp/searxng`, `~/searxng`, `~/.local/searxng`
- Looks for venv in: `searxng-venv/`, `.venv/`, `venv/`
- Waits up to 15 seconds for startup
- Falls back to Docker if available

## Key Functions Added to web_tools.py

| Function | Purpose |
|----------|---------|
| `_get_searxng_url()` | Read URL from config/env |
| `_is_searxng_available()` | Health check via HTTP |
| `_start_searxng()` | Auto-start if not running |
| `_searxng_search()` | Execute search via JSON API |

## Code Changes in web_tools.py

### _get_backend() — Add searxng to candidates

```python
configured = (_load_web_config().get("backend") or "").lower().strip()
if configured in ("parallel", "firecrawl", "tavily", "exa", "searxng"):
    return configured

backend_candidates = (
    ("searxng", _is_searxng_available()),  # Highest priority
    ("firecrawl", _has_env("FIRECRAWL_API_KEY") or ...),
    ...
)
```

### web_search_tool() — Add searxng dispatch

```python
if backend == "searxng":
    response_data = _searxng_search(query, limit)
    ...
```

## Testing

```python
from web_tools import _get_backend, _is_searxng_available, _searxng_search

# Verify backend
assert _get_backend() == "searxng"

# Verify availability
assert _is_searxng_available()

# Execute search
result = _searxng_search("test query", limit=5)
assert result["success"]
assert len(result["data"]["web"]) > 0
```

## Benefits

- **No API costs** — Self-hosted, no per-query charges
- **Privacy** — No search data sent to third parties
- **Unlimited queries** — No rate limits
- **Multiple engines** — Aggregates Google, Bing, DuckDuckGo, etc.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 403 Forbidden | Add `limiter: false` to settings.yml |
| JSON not returned | Add `formats: [html, json]` to settings.yml |
| Auto-start fails | Check venv path matches source path |
| Slow results | Enable more engines in settings.yml |
