---
name: setup-local-model-ollama
description: Setup local Ollama model with Hermes Agent via ngrok - covers config, model naming, and validation bypass
category: devops
version: 1.0.0
metadata:
  hermes:
    tags: [local-model, ollama, ngrok, colab, configuration]
---

# Setup Local Ollama Model with Hermes Agent

Use this skill when setting up a local Ollama server (via Colab, local machine, or cloud) with Hermes Agent through ngrok or direct connection.

## Prerequisites

1. **Ollama server running** - Model must be pulled and available
2. **ngrok tunnel active** (if remote) - URL must be accessible
3. **Hermes config access** - Can edit ~/.hermes/config.yaml

## Step-by-Setup

### Phase 1: Verify Ollama Server

```bash
# Check model is pulled
ollama list

# Test API directly
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3.6:35b",
  "prompt": "test"
}'
```

### Phase 2: Configure Hermes Provider

**Critical:** Config version must be latest (22 as of Apr 2026). Old versions may drop provider sections during migration.

```yaml
# ~/.hermes/config.yaml
providers:
  local-qwen:
    name: Local Qwen (ngrok)
    base_url: https://YOUR_NGROK_URL.ngrok-free.dev/v1
    transport: openai_chat
    key_env: LOCAL_QWEN_API_KEY
    api: https://YOUR_NGROK_URL.ngrok-free.dev/v1
    skip_model_validation: true
    custom_model: true
    models:
      - fredrezones55/qwen3.6-35b-a3b-uncensored-hauhaucs-aggressive:iq2_m
      - qwen3.6:35b
      - qwen3.6
```

**Important fields:**
- `skip_model_validation: true` - Bypasses Hermes model catalog validation
- `custom_model: true` - Marks as user-defined model
- `models: [...]` - Lists acceptable model names (bypasses validation rejection)

### Phase 3: Upgrade Config Version (If Needed)

```python
from pathlib import Path
import yaml

config_path = Path.home() / '.hermes' / 'config.yaml'
with open(config_path) as f:
    config = yaml.safe_load(f)

# Upgrade to latest version
config['_config_version'] = 22

# Ensure providers section exists
if 'providers' not in config or not config['providers']:
    config['providers'] = {}

# Write back
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
```

### Phase 4: Set as Default (Optional)

```yaml
# ~/.hermes/config.yaml
model:
  default: qwen3.6:35b
  provider: local-qwen
  base_url: https://YOUR_NGROK_URL.ngrok-free.dev/v1
```

### Phase 5: Use in Hermes

```bash
# Start Hermes
hermes

# Switch to local model (if not default)
/model qwen3.6:35b

# Or use full model name
/model fredrezones55/qwen3.6-35b-a3b-uncensored-hauhaucs-aggressive:iq2_m
```

## Model Naming Conventions

### Ollama Format
- Lowercase: `qwen3.6:35b` (not `Qwen3.6:35B`)
- Colon for version: `model:size`
- Full name: `fredrezones55/qwen3.6-35b-a3b-uncensored-hauhaucs-aggressive:iq2_m`

### Hermes Format
- No spaces in model name
- Use quotes if needed: `"model-name"`
- Provider prefix: `provider:model`

## Common Pitfalls

### 1. Config Version Mismatch
**Symptom:** `providers: {}` after loading config
**Fix:** Upgrade `_config_version` to latest (22)

### 2. Model Validation Rejection
**Symptom:** `✗ Model was not found in this provider's model listing`
**Fix:** Add model to `providers.local-qwen.models` array in config.yaml

### 3. ngrok URL Expired
**Symptom:** Connection timeout, 422 error
**Fix:** Refresh ngrok tunnel, update base_url in config

### 4. Model Name Format
**Symptom:** `✗ Model names cannot contain spaces`
**Fix:** Use lowercase, no spaces, colon format

### 5. API Key Required
**Symptom:** 401 Unauthorized
**Fix:** Add `LOCAL_QWEN_API_KEY=xxx` to ~/.hermes/.env

## Verification Checklist

- [ ] Ollama server running (`ollama list` shows model)
- [ ] ngrok tunnel active (URL accessible)
- [ ] Config version upgraded to latest
- [ ] Provider config has `skip_model_validation: true`
- [ ] Model name in `models` array
- [ ] Test with curl before Hermes
- [ ] Hermes accepts model without error

## Testing

```bash
# Test ngrok endpoint
curl -X POST "https://YOUR_NGROK_URL.ngrok-free.dev/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.6:35b",
    "messages": [{"role": "user", "content": "test"}]
  }'

# Test in Hermes
hermes -q "/model qwen3.6:35b"
```

## References

- Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
- ngrok AI Gateway: https://ngrok.com/docs/ai-gateway/
- Hermes config: ~/.hermes/config.yaml
- Hermes providers: hermes_cli/providers.py