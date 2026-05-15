# SearXNG Installation in WSL — Session Notes (May 2026)

## Attempted Installation Steps

### 1. Clone Repository
```bash
cd /tmp && git clone --depth 1 https://github.com/searxng/searxng.git
```

### 2. Create Venv (PEP 668 Required)
WSL Ubuntu 24.04 has `externally-managed-environment`. Cannot `pip install` directly.
```bash
python3 -m venv /tmp/searxng-venv
```

### 3. Install Dependencies
```bash
# First attempt: pip install -e . (failed)
# Error: ModuleNotFoundError: No module named 'msgspec'

# Fix: Install build deps first
/tmp/searxng-venv/bin/pip install msgspec babel

# Second attempt: pip install -e . (failed again)
# Error: Getting requirements to build editable

# Fix: Use requirements.txt instead
/tmp/searxng-venv/bin/pip install -r /tmp/searxng/requirements.txt
# Success — installed 30+ packages
```

### 4. Create Config
```yaml
# /tmp/searxng/settings.yml
use_default_settings: true
server:
  secret_key: "your_secret_key_here_change_this"
  bind_address: "0.0.0.0"
  port: 8888
search:
  safe_search: 0
  autocomplete: ""
```

### 5. Run Server
```bash
cd /tmp/searxng && \
  SEARXNG_SETTINGS_PATH=/tmp/searxng/settings.yml \
  /tmp/searxng-venv/bin/python -m searx.webapp
```

Server starts on localhost:8888. HTML search works.

## Problems Encountered

### Problem 1: JSON Format Returns Empty
```bash
curl -s "http://localhost:8888/search?q=test&format=json"
# Returns empty — JSON format may need explicit enable in settings
```

**Not resolved in session.** Likely needs:
```yaml
search:
  formats:
    - html
    - json
```

### Problem 2: Google/Bing Rate Limited
```
SearxEngineTooManyRequestsException: Too many request (suspended_time=180)
```

SearXNG scrapes search engines and gets blocked immediately. This is expected behavior.

**Solutions:**
1. Use engines that don't block: DuckDuckGo, Qwant, Brave, Wikipedia
2. Add rate limiting/delay between requests
3. Use dedicated APIs instead (NewsAPI, SerpAPI)

### Problem 3: Not Suitable for Production Cron Jobs
For the nightly news narrative use case, SearXNG proved unreliable because:
- Rate limiting makes it unsuitable for automated daily runs
- JSON format issues complicate parsing
- Self-hosted maintenance overhead

**Better alternatives for news fetching:**
- RSS feeds (direct, no scraping)
- NewsAPI (structured, reliable)
- Direct website scraping with requests+BeautifulSoup
- Mock data for testing

## Key Learnings

1. **PEP 668 is enforced on Ubuntu 24.04** — always use venv, never system pip
2. **Editable installs can fail** — use `requirements.txt` as fallback
3. **msgspec is a build dependency** — install before `pip install -e .`
4. **SearXNG is for personal search** — not for automated scraping at scale
5. **Cloudflare tunnel + Colab is better for reliable API** — see `vllm-mtp-colab-setup.md`

## Files Created
- `/tmp/searxng/` — cloned repo
- `/tmp/searxng-venv/` — venv with dependencies
- `/tmp/searxng/settings.yml` — custom config
- `/tmp/searxng.log` — server logs
