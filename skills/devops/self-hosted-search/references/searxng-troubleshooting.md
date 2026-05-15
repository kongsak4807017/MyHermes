# SearXNG Troubleshooting

## 403 Forbidden on JSON API

**Symptom:** `curl "http://localhost:8888/search?q=test&format=json"` returns HTML 403 Forbidden instead of JSON.

**Root cause:** SearXNG default config only enables `html` format. JSON requires explicit `formats` list plus `limiter: false` for localhost access.

**Fix:**

```yaml
# settings.yml
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

**Restart required:** After editing config, kill the process and restart:

```bash
# Find PID
ps aux | grep searxng | grep -v grep

# Kill and restart
kill <PID>
cd /tmp/searxng
SEARXNG_SETTINGS_PATH=/tmp/searxng/settings.yml /tmp/searxng-venv/bin/python -m searx.webapp
```

## No results with time_range filter

**Symptom:** `time_range=day` returns empty results.

**Cause:** Not all search engines support time filtering. SearXNG may return 0 results if the active engines don't honor the parameter.

**Fix:** Search without `time_range` then filter client-side, or check which engines support it in SearXNG preferences.

## Config file location confusion

**Symptom:** Edited one config file but changes don't apply.

**Cause:** SearXNG may be running with a different `SEARXNG_SETTINGS_PATH`.

**Check:**
```bash
ps aux | grep searxng
# Look for SEARXNG_SETTINGS_PATH in the command line
```

**Fix:** Edit the file pointed to by `SEARXNG_SETTINGS_PATH`, or restart with the correct path.

## Engine returns no results

**Symptom:** All queries return 0 results.

**Check:**
1. Verify network connectivity: `curl https://www.google.com`
2. Check SearXNG logs: `cat /tmp/searxng.log`
3. Some engines (Google) may block requests from datacenter IPs

**Fix:** Enable more engines in `settings.yml` or use `use_default_settings: true`.
