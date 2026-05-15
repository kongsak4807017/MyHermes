"""OMK Colors — ANSI escapes + Hermes skin integration.

Uses the same skin engine as Hermes CLI for consistent theming.
Falls back to built-in defaults if no skin is found.
"""

# =========================================================================
# Built-in defaults (dark terminal)
# =========================================================================

_COLORS = {
    "accent": "\033[38;2;255;191;0m",       # Gold accent
    "title": "\033[38;2;255;215;0m",        # Gold title
    "ok": "\033[38;2;76;175;80m",           # Green
    "warn": "\033[38;2;255;167;38m",        # Orange
    "error": "\033[38;2;239;83;80m",        # Red
    "dim": "\033[38;2;120;120;120m",        # Gray
    "label": "\033[38;2;77;208;225m",       # Cyan
    "value": "\033[38;2;255;248;220m",      # Warm white
    "border": "\033[38;2;138;134;130m",     # Brown
    "reset": "\033[0m",
}


def _resolve_skin_colors() -> dict:
    """Try to resolve colors from Hermes skin config."""
    try:
        import sys
        sys.path.insert(0, "/mnt/c/Users/User/hermes-agent")
        from hermes_cli.skin_engine import get_active_skin
        skin = get_active_skin()
        if skin:
            colors = skin.colors
            result = {}

            def _hex(key):
                h = colors.get(key, "")
                if h and len(h) == 7 and h[0] == "#":
                    r = int(h[1:3], 16)
                    g = int(h[3:5], 16)
                    b = int(h[5:7], 16)
                    return f"\033[38;2;{r};{g};{b}m"
                return ""

            accent = _hex("ui_accent") or _hex("banner_accent")
            result["accent"] = accent or _COLORS["accent"]
            result["title"] = _hex("banner_title") or _COLORS["title"]
            result["ok"] = _hex("ui_ok") or _COLORS["ok"]
            result["warn"] = _hex("ui_warn") or _COLORS["warn"]
            result["error"] = _hex("ui_error") or _COLORS["error"]
            result["dim"] = _hex("banner_dim") or _COLORS["dim"]
            result["label"] = _hex("ui_label") or _COLORS["label"]
            result["value"] = _hex("banner_text") or _COLORS["value"]
            result["border"] = _hex("session_border") or _COLORS["border"]
            result["reset"] = "\033[0m"
            return result
    except Exception:
        pass

    return _COLORS


_skin_colors: dict | None = None


def get_colors() -> dict:
    """Get resolved colors (lazy-loaded from skin)."""
    global _skin_colors
    if _skin_colors is None:
        _skin_colors = _resolve_skin_colors()
    return _skin_colors


def get_branding() -> str:
    """Get agent name from skin branding."""
    try:
        import sys
        sys.path.insert(0, "/mnt/c/Users/User/hermes-agent")
        from hermes_cli.skin_engine import get_active_skin
        skin = get_active_skin()
        if skin:
            return skin.branding.get("agent_name", "Hermes Agent")
    except Exception:
        pass
    return "Hermes Agent"


def get_skin_name() -> str:
    """Get active skin name."""
    try:
        import sys
        sys.path.insert(0, "/mnt/c/Users/User/hermes-agent")
        from hermes_cli.skin_engine import get_active_skin
        skin = get_active_skin()
        if skin:
            return skin.name
    except Exception:
        pass
    return "default"
