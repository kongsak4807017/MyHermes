# SearXNG tool for Hermes Agent
# Drop this into hermes-agent/tools/ to enable search

import os
import json
import urllib.parse
from tools.registry import registry

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8888")

def searxng_search(query: str, time_range: str = None, category: str = "general", task_id: str = None) -> str:
    """Search web using SearXNG metasearch engine."""
    params = {
        "q": query,
        "format": "json",
        "categories": category,
    }
    if time_range:
        params["time_range"] = time_range
    
    query_string = urllib.parse.urlencode(params)
    url = f"{SEARXNG_URL}/search?{query_string}"
    
    import requests
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])[:10]
        
        output = []
        for i, res in enumerate(results, 1):
            title = res.get("title", "No title")
            snippet = res.get("content", "")[:200]
            link = res.get("url", "")
            output.append(f"{i}. {title}\n   {snippet}\n   {link}")
        
        return "\n\n".join(output) if output else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

def searxng_image_search(query: str, task_id: str = None) -> str:
    """Search images using SearXNG."""
    return searxng_search(query, category="images", task_id=task_id)

def check_requirements() -> bool:
    try:
        import requests
        r = requests.get(f"{SEARXNG_URL}/", timeout=5)
        return r.status_code == 200
    except:
        return False

registry.register(
    name="searxng_search",
    toolset="search",
    schema={
        "name": "searxng_search",
        "description": "Search the web using SearXNG metasearch engine. Returns top 10 results with title, snippet, and URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "time_range": {"type": "string", "enum": ["day", "week", "month", "year"], "description": "Time filter"},
                "category": {"type": "string", "enum": ["general", "images", "news", "videos"], "description": "Search category"}
            },
            "required": ["query"]
        }
    },
    handler=lambda args, **kw: searxng_search(
        query=args.get("query", ""),
        time_range=args.get("time_range"),
        category=args.get("category", "general"),
        task_id=kw.get("task_id")
    ),
    check_fn=check_requirements
)

registry.register(
    name="searxng_image_search",
    toolset="search",
    schema={
        "name": "searxng_image_search",
        "description": "Search images using SearXNG.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Image search query"}
            },
            "required": ["query"]
        }
    },
    handler=lambda args, **kw: searxng_image_search(
        query=args.get("query", ""),
        task_id=kw.get("task_id")
    ),
    check_fn=check_requirements
)
