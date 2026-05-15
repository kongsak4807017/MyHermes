# vLLM + MTP (Multi-Token Prediction) on Google Colab

## Overview

vLLM with speculative decoding (MTP) can speed up local models by 2-3x. Running on Google Colab (free T4 GPU) + Cloudflare tunnel provides a fast remote endpoint for Hermes Agent/OMK CLI.

## What is MTP?

Multi-Token Prediction changes the generation pattern:
- **Normal:** Think → guess 1 token → think → guess 1 token (slow, like walking)
- **MTP:** A lightweight "drafter" guesses 2-4 tokens ahead → main model verifies all at once (fast, like running)

Google claims up to 3x speedup. Real-world: ~2.3x for sequential, ~1.9x for concurrent.

## Colab Notebook Setup

### Prerequisites
- Google Colab account (free tier)
- GPU runtime enabled (Runtime → Change runtime type → T4)

### Step 1: Install vLLM
```python
!pip install vllm==0.8.3
```

### Step 2: Download Gemma 4 Model
```python
from huggingface_hub import snapshot_download

MODEL = "google/gemma-4-4B-it"  # Recommended for T4
# MODEL = "google/gemma-4-2B-it"  # Lighter option
# MODEL = "google/gemma-4-9B-it"  # Needs more VRAM

model_path = snapshot_download(
    MODEL,
    cache_dir="/content/models",
    local_dir="/content/models/gemma-4",
    local_dir_use_symlinks=False
)
```

### Step 3: Install Cloudflared
```python
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared
!chmod +x /usr/local/bin/cloudflared
```

### Step 4: Start vLLM with MTP
```python
import subprocess

NUM_SPECULATIVE_TOKENS = 4  # 2-4 recommended. Higher = faster but more overhead

vllm_cmd = [
    "python", "-m", "vllm.entrypoints.openai.api_server",
    "--model", "/content/models/gemma-4",
    "--port", "8000",
    "--speculative-config", f'{{"method": "mtp", "num_speculative_tokens": {NUM_SPECULATIVE_TOKENS}}}',
    "--dtype", "half",
    "--max-model-len", "8192",
    "--gpu-memory-utilization", "0.9",
]

server = subprocess.Popen(vllm_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(f"Server PID: {server.pid}")
```

### Step 5: Start Cloudflare Tunnel
```python
import subprocess
import re

tunnel = subprocess.Popen(
    ["cloudflared", "tunnel", "--url", "http://localhost:8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

tunnel_url = None
for line in iter(tunnel.stdout.readline, ''):
    print(line, end='')
    match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
    if match:
        tunnel_url = match.group(0)
        break

print(f"\n{'='*60}")
print(f"TUNNEL URL: {tunnel_url}")
print(f"{'='*60}")
print(f"\nAPI Endpoint: {tunnel_url}/v1")
```

### Step 6: Test API
```python
import requests

api_url = f"{tunnel_url}/v1/chat/completions"

response = requests.post(api_url, json={
    "model": "gemma-4-4B-it",
    "messages": [{"role": "user", "content": "สวัสดี อธิบาย MTP คืออะไร"}],
    "max_tokens": 100
})

print(f"Status: {response.status_code}")
print(f"Response: {response.json()['choices'][0]['message']['content'][:200]}")
```

## Hermes Agent / OMK CLI Integration

### Option A: Direct Config Update
```python
# setup_vllm_hermes.py
import yaml
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
config_path = HERMES_HOME / "config.yaml"

with open(config_path) as f:
    config = yaml.safe_load(f) or {}

config.setdefault("providers", {})
config["providers"]["vllm-colab"] = {
    "name": "vLLM on Colab (MTP)",
    "base_url": "https://abc123.trycloudflare.com/v1",  # Your tunnel URL
    "transport": "openai_chat",
    "key_env": "VLLM_API_KEY",  # Can be dummy
}

with open(config_path, "w") as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
```

### Option B: OMK CLI Auth
```python
import json
from pathlib import Path

OMK_HOME = Path("/mnt/c/Users/User/.omk")
auth_path = OMK_HOME / "auth.json"

with open(auth_path) as f:
    auth = json.load(f)

auth.setdefault("providers", {})
auth["providers"]["vllm-colab"] = {
    "api_key": "dummy-key-not-needed",
    "api_base": "https://abc123.trycloudflare.com/v1",
    "model": "gemma-4-4B-it",
    "transport": "openai"
}

with open(auth_path, "w") as f:
    json.dump(auth, f, indent=2, ensure_ascii=False)
```

### Usage
```bash
# Hermes Agent
hermes chat --provider vllm-colab --model gemma-4-4B-it

# OMK CLI
omk chat --provider vllm-colab --model gemma-4-4B-it

# Python
from run_agent import AIAgent
agent = AIAgent(provider="vllm-colab", model="gemma-4-4B-it")
```

## Performance Comparison

| Setup | Speed | Context | Notes |
|-------|-------|---------|-------|
| Ollama local (CPU) | ~5-10 tok/s | 131K | Very slow, no GPU |
| Ollama local (GPU) | ~20-40 tok/s | 131K | Needs local GPU |
| vLLM on Colab (no MTP) | ~30-50 tok/s | 8K | T4 GPU, limited context |
| vLLM on Colab (MTP=4) | ~60-100 tok/s | 8K | **2-3x faster** |
| vLLM on A100 (MTP) | ~200+ tok/s | 32K+ | Paid tier |

## Limitations

1. **Colab session limit:** 12 hours max → must restart daily
2. **Tunnel URL changes:** Every restart gets new URL → must update config
3. **VRAM limit:** T4 has 16GB → max ~9B parameter model with MTP
4. **MTP overhead:** Uses extra VRAM for drafter model (~5-10%)
5. **Free tier queue:** May wait for GPU allocation during peak hours

## Automation Tips

### Persistent Tunnel (Named Tunnel)
Instead of temporary tunnels, create a named Cloudflare tunnel:
```bash
cloudflared tunnel create vllm-gemma4
cloudflared tunnel route dns vllm-gemma4 vllm-gemma4.yourdomain.com
cloudflared tunnel run vllm-gemma4
```
This gives a fixed URL that doesn't change between restarts.

### Keep Colab Alive
```python
# Run in a cell to prevent timeout
import time
while True:
    time.sleep(60)
    print(f"[{time.strftime('%H:%M:%S')}] Keeping alive...")
```

Or use browser automation (Selenium/Playwright) to click "Reconnect" if disconnected.

## Troubleshooting

### "CUDA out of memory"
- Reduce model size (use 2B instead of 4B)
- Reduce `num_speculative_tokens` to 2
- Reduce `--max-model-len` to 4096
- Use `-- quantization` (e.g., `--quantization awq`)

### "cloudflared: command not found"
- Re-run Step 3 installation
- Or use `!pip install pycloudflare` alternative

### "Failed to connect to localhost:8000"
- vLLM server hasn't started yet → wait 2-3 minutes
- Check server logs: `server.stdout.read()`
- Port conflict → change `--port` to 8001

### Model generates garbled Thai text
- Gemma 4 has good Thai support but may need prompt in Thai
- Add system prompt: "You are a helpful assistant. Respond in Thai."
- Reduce temperature to 0.7 for more consistent output

## References

- vLLM docs: https://docs.vllm.ai/
- Gemma 4 on HuggingFace: https://huggingface.co/google/gemma-4-4B-it
- Cloudflare Tunnel docs: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- Colab FAQ: https://research.google.com/colaboratory/faq.html
