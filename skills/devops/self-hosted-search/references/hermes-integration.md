# SearXNG Integration with Hermes Agent web_tools.py

## What was done

Integrated SearXNG as a first-class backend in Hermes Agent's `web_tools.py`, allowing it to be used as the default web search provider without any external API keys.

## Files modified

- `/mnt/c/Users/User/hermes-agent/tools/web_tools.py` — added `_get_searxng_url()`, `_is_searxng_available()`, `_searxng_search()`, and registered `searxng` in backend dispatch

## Key design decisions

1. **Priority in auto-detection:** SearXNG is checked FIRST before paid backends (Firecrawl, Parallel, Tavily, Exa). This means if SearXNG is running, Hermes will use it automatically without requiring API keys.

2. **Config sources (in order):**
   - `web.searxng_url` in `~/.hermes/config.yaml`
   - `SEARXNG_URL` environment variable
   - Default: `http://localhost:8888`

3. **Availability check:** Tries `/healthz` first, then falls back to a test search query. Both use 5-second timeout.

4. **Result normalization:** Returns the same shape as other backends: `{"success": true, "data": {"web": [{"url", "title", "description", "position", "engine"}]}}`

## Testing

```python
from web_tools import _searxng_search, _is_searxng_available, _get_searxng_url

print(_get_searxng_url())      # http://localhost:8888
print(_is_searxng_available()) # True/False
result = _searxng_search("breaking news today", limit=5)
print(result["data"]["web"][0]["title"])
```

## Troubleshooting integration

If `web_search_tool()` still uses a paid backend even though SearXNG is running:
- Check `web.backend` in config.yaml — if set to a specific backend, it overrides auto-detection
- Check that SearXNG actually responds: `curl http://localhost:8888/search?q=test&format=json`
- Check Hermes logs for backend selection: it logs which backend was chosen
