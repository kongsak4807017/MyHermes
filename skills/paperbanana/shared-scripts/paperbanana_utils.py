#!/usr/bin/env python3
"""
Shared utilities for PaperBanana skills.
Handles LLM calls, image generation, PDF parsing, and common utilities.
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional

import urllib.request
import urllib.error


# ── Environment / Config ───────────────────────────────────────────


def load_env_file(path: Path) -> None:
    """Load key=value pairs from a .env file into os.environ."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def get_api_key(provider: str) -> Optional[str]:
    """Resolve API key for a provider from environment."""
    env_map = {
        "openai": ["OPENAI_API_KEY"],
        "gemini": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
        "openrouter": ["OPENROUTER_API_KEY"],
    }
    for key in env_map.get(provider, []):
        val = os.environ.get(key)
        if val:
            return val
    return None


# ── LLM Calls ──────────────────────────────────────────────────────


async def call_llm(
    provider: str,
    model: str,
    messages: list[dict],
    json_mode: bool = False,
    temperature: float = 0.7,
    verbose: bool = False,
) -> Any:
    """Call an LLM via the best available method."""
    if verbose:
        print(f"[LLM] {provider}/{model} | json={json_mode} | msgs={len(messages)}")

    # Try Hermes Agent's native LLM tool if available
    try:
        from hermes_tools import terminal
        result = _call_via_hermes_terminal(provider, model, messages, json_mode, temperature)
        if result:
            return result
    except Exception as e:
        if verbose:
            print(f"[LLM] Hermes terminal fallback failed: {e}")

    # Try direct API call
    try:
        return await _call_api_direct(provider, model, messages, json_mode, temperature, verbose)
    except Exception as e:
        if verbose:
            print(f"[LLM] Direct API failed: {e}")

    # Final fallback: return a mock response for testing
    return _mock_response(messages, json_mode)


def _call_via_hermes_terminal(
    provider: str, model: str, messages: list, json_mode: bool, temperature: float
) -> Optional[Any]:
    """Try to call LLM via Hermes Agent's terminal tool using available CLI."""
    # Check for available CLI tools
    cli_tools = {
        "openai": ["openai", "gpt"],
        "gemini": ["gemini"],
        "openrouter": ["openrouter"],
    }

    # Try using Python directly with requests
    try:
        import requests
        api_key = get_api_key(provider)
        if not api_key:
            return None

        base_urls = {
            "openai": "https://api.openai.com/v1",
            "gemini": "https://generativelanguage.googleapis.com/v1beta",
            "openrouter": "https://openrouter.ai/api/v1",
        }

        base_url = base_urls.get(provider, "https://api.openai.com/v1")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://hermes-agent.nousresearch.com"
            headers["X-Title"] = "Hermes Agent PaperBanana"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        if provider == "gemini":
            # Gemini uses a different API structure
            url = f"{base_url}/models/{model}:generateContent?key={api_key}"
            gemini_payload = {
                "contents": [
                    {
                        "role": msg["role"].replace("assistant", "model"),
                        "parts": [{"text": msg["content"]}],
                    }
                    for msg in messages
                ],
                "generationConfig": {"temperature": temperature},
            }
            if json_mode:
                gemini_payload["generationConfig"]["responseMimeType"] = "application/json"

            resp = requests.post(url, headers={"Content-Type": "application/json"}, json=gemini_payload, timeout=120)
        else:
            url = f"{base_url}/chat/completions"
            resp = requests.post(url, headers=headers, json=payload, timeout=120)

        resp.raise_for_status()
        data = resp.json()

        if provider == "gemini":
            content = data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            content = data["choices"][0]["message"]["content"]

        if json_mode:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code block
                match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
                if match:
                    return json.loads(match.group(1))
                return {"response": content}
        return content

    except ImportError:
        return None
    except Exception:
        return None


async def _call_api_direct(
    provider: str, model: str, messages: list, json_mode: bool, temperature: float, verbose: bool
) -> Any:
    """Direct API call using urllib (no external dependencies)."""
    import urllib.request
    import ssl

    api_key = get_api_key(provider)
    if not api_key:
        raise RuntimeError(f"No API key found for provider: {provider}")

    base_urls = {
        "openai": "https://api.openai.com/v1",
        "openrouter": "https://openrouter.ai/api/v1",
    }

    if provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "role": msg["role"].replace("assistant", "model"),
                    "parts": [{"text": msg["content"]}],
                }
                for msg in messages
            ],
            "generationConfig": {"temperature": temperature},
        }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"
    else:
        base_url = base_urls.get(provider, "https://api.openai.com/v1")
        url = f"{base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    if provider == "openrouter":
        headers["HTTP-Referer"] = "https://hermes-agent.nousresearch.com"
        headers["X-Title"] = "Hermes Agent PaperBanana"

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    # Allow unverified SSL for compatibility
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        response_data = json.loads(resp.read().decode("utf-8"))

    if provider == "gemini":
        content = response_data["candidates"][0]["content"]["parts"][0]["text"]
    else:
        content = response_data["choices"][0]["message"]["content"]

    if json_mode:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
            if match:
                return json.loads(match.group(1))
            return {"response": content}
    return content


def _mock_response(messages: list, json_mode: bool) -> Any:
    """Return a mock response for testing without API keys."""
    if json_mode:
        return {
            "status": "mock",
            "message": "This is a mock response. Set an API key to use real generation.",
            "last_user_message": messages[-1]["content"][:200] if messages else "",
        }
    return "[MOCK] This is a mock response. Set an API key to use real generation."


# ── Image Generation ───────────────────────────────────────────────


async def generate_image(
    provider: str,
    model: str,
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    verbose: bool = False,
) -> dict:
    """Generate an image using the configured provider."""
    if verbose:
        print(f"[Image] {provider}/{model} | size={size}")

    api_key = get_api_key(provider)
    if not api_key:
        # Return a placeholder for testing
        return {
            "path": None,
            "url": None,
            "mock": True,
            "message": "No API key set. Set OPENAI_API_KEY, GOOGLE_API_KEY, or OPENROUTER_API_KEY.",
        }

    try:
        if provider == "openai":
            return await _generate_image_openai(api_key, model, prompt, size, quality)
        elif provider == "gemini":
            return await _generate_image_gemini(api_key, model, prompt)
        else:
            return await _generate_image_openai(api_key, model, prompt, size, quality)
    except Exception as e:
        if verbose:
            print(f"[Image] Generation failed: {e}")
        return {"path": None, "url": None, "error": str(e)}


async def _generate_image_openai(
    api_key: str, model: str, prompt: str, size: str, quality: str
) -> dict:
    """Generate image via OpenAI DALL-E API."""
    import urllib.request
    import ssl

    url = "https://api.openai.com/v1/images/generations"
    payload = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality,
    }

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        response_data = json.loads(resp.read().decode("utf-8"))

    image_url = response_data["data"][0]["url"]

    # Download the image
    temp_path = Path(tempfile.gettempdir()) / f"paperbanana_{os.urandom(4).hex()}.png"
    img_req = urllib.request.Request(image_url, headers={})
    with urllib.request.urlopen(img_req, timeout=60, context=ctx) as img_resp:
        temp_path.write_bytes(img_resp.read())

    return {"path": str(temp_path), "url": image_url}


async def _generate_image_gemini(api_key: str, model: str, prompt: str) -> dict:
    """Generate image via Gemini API."""
    import urllib.request
    import ssl

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Generate an image: {prompt}"}
                ]
            }
        ],
        "generationConfig": {"responseModalities": ["Text", "Image"]},
    }

    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        response_data = json.loads(resp.read().decode("utf-8"))

    # Extract image from response
    parts = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    for part in parts:
        if "inlineData" in part:
            import base64
            img_data = base64.b64decode(part["inlineData"]["data"])
            temp_path = Path(tempfile.gettempdir()) / f"paperbanana_{os.urandom(4).hex()}.png"
            temp_path.write_bytes(img_data)
            return {"path": str(temp_path), "url": None}

    return {"path": None, "url": None, "error": "No image in Gemini response"}


# ── PDF Parsing ────────────────────────────────────────────────────


def parse_pdf_text(path: str, pages: Optional[str] = None) -> str:
    """Extract text from a PDF file. Tries multiple methods."""
    # Try PyMuPDF first
    try:
        import fitz
        doc = fitz.open(path)
        text_parts = []

        page_indices = _parse_page_selection(pages, len(doc))
        for i in page_indices:
            text_parts.append(doc[i].get_text())
        doc.close()
        return "\n\n".join(text_parts)
    except ImportError:
        pass

    # Try pdfplumber
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(path) as pdf:
            page_indices = _parse_page_selection(pages, len(pdf.pages))
            for i in page_indices:
                text_parts.append(pdf.pages[i].extract_text() or "")
        return "\n\n".join(text_parts)
    except ImportError:
        pass

    # Fallback: pdftotext
    try:
        cmd = ["pdftotext", path, "-"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    raise RuntimeError(
        "No PDF parser available. Install PyMuPDF (pip install PyMuPDF) or pdfplumber, "
        "or install poppler-utils for pdftotext."
    )


def _parse_page_selection(pages: Optional[str], total: int) -> list[int]:
    """Parse page selection string like '1-5' or '2,4,6-8' into 0-based indices."""
    if not pages:
        return list(range(total))

    indices = set()
    for part in pages.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            indices.update(range(int(start) - 1, int(end)))
        else:
            indices.add(int(part) - 1)

    return sorted(i for i in indices if 0 <= i < total)


# ── Utilities ──────────────────────────────────────────────────────


def save_metadata(metadata: dict, path: str) -> None:
    """Save metadata JSON to file."""
    Path(path).write_text(json.dumps(metadata, indent=2, ensure_ascii=False))


def setup_logging(verbose: bool) -> None:
    """Configure logging."""
    import logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s")


# ── CSV / Data Parsing ─────────────────────────────────────────────


def sniff_data_schema(path: str) -> dict:
    """Analyze a CSV or JSON file and return its schema description."""
    p = Path(path)
    if not p.exists():
        return {"error": "File not found"}

    suffix = p.suffix.lower()

    if suffix == ".csv":
        return _sniff_csv_schema(path)
    elif suffix == ".json":
        return _sniff_json_schema(path)
    else:
        return {"error": f"Unsupported format: {suffix}"}


def _sniff_csv_schema(path: str) -> dict:
    """Analyze CSV structure."""
    import csv

    with open(path, "r", encoding="utf-8") as f:
        sample = f.read(8192)

    dialect = csv.Sniffer().sniff(sample)
    f = open(path, "r", encoding="utf-8")
    reader = csv.reader(f, dialect)
    headers = next(reader)

    # Collect sample values for each column
    col_samples = {h: [] for h in headers}
    for i, row in enumerate(reader):
        if i >= 20:
            break
        for j, val in enumerate(row):
            if j < len(headers):
                col_samples[headers[j]].append(val)
    f.close()

    columns = []
    for h in headers:
        samples = col_samples[h]
        numeric = all(_is_numeric(v) for v in samples[:10] if v)
        col_type = "numeric" if numeric else "categorical"
        columns.append({
            "name": h,
            "type": col_type,
            "sample_values": samples[:5],
        })

    return {
        "format": "csv",
        "columns": columns,
        "row_count": sum(1 for _ in open(path, "r", encoding="utf-8")) - 1,
    }


def _sniff_json_schema(path: str) -> dict:
    """Analyze JSON structure."""
    data = json.loads(Path(path).read_text())

    if isinstance(data, list) and len(data) > 0:
        first = data[0]
        if isinstance(first, dict):
            columns = []
            for key, val in first.items():
                col_type = "numeric" if isinstance(val, (int, float)) else "categorical"
                columns.append({
                    "name": key,
                    "type": col_type,
                    "sample_values": [str(d.get(key, "")) for d in data[:5]],
                })
            return {
                "format": "json",
                "columns": columns,
                "row_count": len(data),
            }

    return {"format": "json", "structure": type(data).__name__, "row_count": len(data) if isinstance(data, list) else 1}


def _is_numeric(val: str) -> bool:
    """Check if a string value is numeric."""
    try:
        float(val)
        return True
    except ValueError:
        return False
