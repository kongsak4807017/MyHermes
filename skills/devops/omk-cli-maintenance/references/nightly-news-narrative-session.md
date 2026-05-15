# Session: Nightly News Narrative Generator with gemma4:e4b (May 2026)

**Date:** 2026-05-06
**Model:** gemma4:e4b via ollama-local provider
**Goal:** Generate 3 narrative styles (Standard News, Friend-to-Friend, Expert Deep Dive) as cron job

## Key Discoveries

### 1. Windows Venv Cannot Be Used from WSL

Hermes Agent venv at `/mnt/c/Users/User/hermes-agent/venv/` contains Windows Python (`Scripts/python.exe`). Attempting to run from WSL produces:

```
python.exe: can't open file 'C:\home\user\.hermes\scripts\...': [Errno 2]
```

**Solution:** Create separate WSL venv:
```bash
python3 -m venv /tmp/hermes-run-venv
/tmp/hermes-run-venv/bin/pip install python-dotenv openai anthropic httpx \
    rich tenacity pyyaml requests jinja2 pydantic prompt_toolkit exa-py \
    firecrawl-py parallel-web fal-client croniter edge-tts PyJWT
```

### 2. PEP 668 System Package Restriction

WSL Ubuntu 24.04 has PEP 668 enabled. `pip install` without venv fails:
```
error: externally-managed-environment
```

**Solution:** Always use venv. Never use `--break-system-packages` in scripts.

### 3. Hermes Cron Job Script Path Rules

`hermes cron create --script` requires filename relative to `~/.hermes/scripts/`, not absolute path:

```bash
# CORRECT
hermes cron create "nightly-news" --script "run_nightly_news.sh"

# WRONG — rejected by validator
hermes cron create "nightly-news" --script "/home/user/.hermes/scripts/run.sh"
```

### 4. Bash Wrapper Pattern for Venv Scripts

When the Python script needs a specific interpreter, create a bash wrapper in `~/.hermes/scripts/`:

```bash
#!/bin/bash
VENV_PYTHON="/tmp/hermes-run-venv/bin/python"
SCRIPT="/home/user/.hermes/scripts/nightly_news_narrative.py"
cd /mnt/c/Users/User/hermes-agent || exit 1
exec "$VENV_PYTHON" "$SCRIPT" "$@"
```

Register the wrapper (not the .py) as the cron job script.

### 5. Mock News vs Real News Fetch

**SearXNG status:** Not running in this WSL instance. From memory, SearXNG runs at localhost:8888 but may be on Windows host or another machine.

**Web search tools:** Hermes `web_search_tool` requires API keys (Firecrawl, Exa, Parallel, Tavily). No free option without API key.

**Working approach for now:** Use mock news data in prompt, or use Kimi (fast, with web search) to fetch news first, then pass to gemma4:e4b for narrative generation.

### 6. Gemma 4 Thai Content Quality

**Verified capabilities:**
- Context: 131,072 tokens (confirmed)
- Speed: ~4 minutes per ~2,500-2,700 char response
- Quality: Good for all 3 styles
- Issues: Still produces some meta-text ("คำแนะนำในการนำไปใช้", "💡 ข้อแนะนำเพิ่มเติม")

**Post-processing required:**
```python
import re

def clean_for_tts(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'#{1,6}\s*คำแนะนำ.*?(?=---|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'\*\*💡.*?(?=---|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'\[SCRIPT\]\s*', '', text)
    return text.strip()
```

### 7. Tool Loop Warning Trigger

When terminal tool fails 3+ times in one turn, the system emits:
```
[Tool loop warning: same_tool_failure_warning; count=3; terminal has failed 3 times this turn. This looks like a loop; change approach before retrying.]
```

**Response:** Switch to a different tool (e.g., `write_file` instead of `terminal`) or change approach entirely.

### 8. Background Process Hang Detection

When a background process hangs (no output for minutes), use `process(action="kill")` to stop it. The exit code will be `-15` (SIGTERM).

## Files Created

| File | Purpose |
|------|---------|
| `~/.hermes/scripts/nightly_news_narrative.py` | Main generator script |
| `~/.hermes/scripts/nightly_news_narrative_test.py` | Test with mock news |
| `~/.hermes/scripts/run_nightly_news.sh` | Bash wrapper for venv |
| `~/.hermes/narratives/news/2026-05-06_Standard_News.md` | Output sample |
| `~/.hermes/narratives/news/2026-05-06_Friend-to-Friend.md` | Output sample |
| `~/.hermes/narratives/news/2026-05-06_Expert_Deep_Dive.md` | Output sample |

## Cron Job Status

```
Job ID: 8bbbc65ab123
Name: nightly-news-narrative
Schedule: 0 2 * * * (02:00 daily)
Script: run_nightly_news.sh
State: scheduled
Next run: 2026-05-06 02:00+07:00
```

## Open Issues

1. SearXNG not running — need to start or use alternative news source
2. Script still uses mock news — need to integrate real news fetch
3. Meta-text cleanup regex may need refinement based on more samples
4. No notification on completion — consider adding Telegram/Discord webhook
