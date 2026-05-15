# vLLM + MTP Integration for OMK CLI

## Context

OMK CLI aims for parity with Hermes Agent capabilities. One gap is support for fast local model serving via vLLM with speculative decoding (MTP). This reference documents the integration pattern.

## What is MTP?

Multi-Token Prediction (MTP) is a speculative decoding technique where a lightweight "drafter" model predicts 2-4 tokens ahead, and the main model verifies them all at once. This speeds up generation by 2-3x without quality loss.

Google's Gemma 4 models support MTP natively. vLLM (the fastest LLM serving engine) added Day-0 support.

## Architecture Options

### Option A: vLLM on Colab + Cloudflare Tunnel (Recommended for Free Tier)

```
[Google Colab T4 GPU]
  └─ vLLM + MTP (gemma-4-4B-it)
      └─ Cloudflare Tunnel (trycloudflare.com)
          └─ [WSL / Any Device]
              └─ OMK CLI / Hermes Agent
```

**Pros:**
- Free T4 GPU
- No local GPU needed
- 2-3x faster than local CPU Ollama

**Cons:**
- 12-hour session limit
- Tunnel URL changes every restart
- Needs daily setup or automation

**Setup:** See `slow-local-model-batch/references/vllm-mtp-colab-setup.md`

### Option B: vLLM on Local GPU

```
[Local Machine with NVIDIA GPU]
  └─ vLLM + MTP (any supported model)
      └─ localhost:8000
          └─ OMK CLI / Hermes Agent
```

**Pros:**
- Persistent, no session limits
- Fixed localhost URL
- Full control over models

**Cons:**
- Requires NVIDIA GPU
- More complex setup on Windows

**Setup:**
```bash
# Install vLLM
pip install vllm

# Run with MTP
python -m vllm.entrypoints.openai.api_server \
  --model google/gemma-4-4B-it \
  --speculative-config '{"method": "mtp", "num_speculative_tokens": 4}' \
  --port 8000
```

### Option C: vLLM Backend for Ollama (Future)

Ollama may add vLLM as a backend option. When available:
```bash
ollama serve --backend vllm
```

## OMK CLI Provider Configuration

Add to `~/.omk/auth.json`:
```json
{
  "providers": {
    "vllm-local": {
      "api_key": "dummy-key",
      "api_base": "http://localhost:8000/v1",
      "model": "gemma-4-4B-it",
      "transport": "openai"
    },
    "vllm-colab": {
      "api_key": "dummy-key",
      "api_base": "https://abc123.trycloudflare.com/v1",
      "model": "gemma-4-4B-it",
      "transport": "openai"
    }
  }
}
```

Add to `omk/config.py` DEFAULT_CONFIG:
```python
"vllm-local": {
    "base_url": "http://localhost:8000/v1",
    "env_var": "VLLM_API_KEY",
    "models": ["gemma-4-4B-it", "gemma-4-2B-it", "gemma-4-9B-it"],
}
```

## Code Changes Needed in OMK

### 1. Provider Registry (`omk/providers/__init__.py`)
Add vLLM as an OpenAI-compatible provider:
```python
_PROVIDERS = {
    "openrouter": OpenRouterProvider,
    "kimi": KimiProvider,
    "codex": CodexProvider,
    "gemini": GeminiProvider,
    "vllm-local": lambda auth, **kw: OpenAICompatibleProvider(
        auth, base_url="http://localhost:8000/v1", **kw
    ),
    "vllm-colab": lambda auth, **kw: OpenAICompatibleProvider(
        auth, base_url=kw.get("api_base"), **kw
    ),
}
```

### 2. OpenAI-Compatible Provider (`omk/providers/base.py`)
Ensure `OpenAICompatibleProvider` handles dummy API keys:
```python
class OpenAICompatibleProvider(BaseProvider):
    def __init__(self, auth_manager, base_url=None, **kwargs):
        self.base_url = base_url or "http://localhost:8000/v1"
        self.api_key = auth_manager.get_api_key("vllm") or "dummy-key"
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
```

### 3. CLI Commands (`omk/monitoring/cli.py`)
Add vLLM-specific commands:
```python
def cmd_vllm_status(args):
    """Check vLLM server health."""
    import requests
    try:
        resp = requests.get(f"{args.base_url}/health")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("vLLM server is running")
    except Exception as e:
        print(f"vLLM not reachable: {e}")

def cmd_vllm_models(args):
    """List available vLLM models."""
    import requests
    resp = requests.get(f"{args.base_url}/v1/models")
    data = resp.json()
    for model in data.get("data", []):
        print(f"  {model['id']}")
```

## Testing

```bash
# Test vLLM endpoint
curl http://localhost:8000/v1/models

# Test chat completion
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4-4B-it",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# Test with OMK
./bin/omk run --provider vllm-local --model gemma-4-4B-it --prompt "Say hi in Thai"
```

## Performance Benchmarks (Expected)

| Setup | Tokens/sec | Relative |
|-------|-----------|----------|
| Ollama CPU (WSL) | 5-10 | 1x |
| Ollama GPU (local) | 20-40 | 4x |
| vLLM no MTP (T4) | 30-50 | 6x |
| vLLM + MTP=2 (T4) | 50-80 | 10x |
| vLLM + MTP=4 (T4) | 60-100 | 12x |
| vLLM + MTP=4 (A100) | 200+ | 40x |

## Known Issues

1. **Dummy API key:** vLLM doesn't require auth by default, but OpenAI client needs a non-empty string. Use `"dummy-key"` or any placeholder.

2. **Model name mismatch:** vLLM serves the model under its HuggingFace name (`google/gemma-4-4B-it`) but OMK may use a shorthand (`gemma-4-4B-it`). Ensure `model` parameter matches exactly.

3. **Context window:** vLLM on Colab T4 with 16GB VRAM can only handle ~8K context with MTP=4. For longer contexts, reduce `num_speculative_tokens` or use a smaller model.

4. **Tunnel timeout:** Cloudflare free tunnels timeout after ~1 hour of inactivity. For cron jobs, use a named tunnel or keep-alive pings.

## Future Enhancements

- Auto-detect vLLM server on startup
- Show MTP stats in token dashboard (speculative tokens accepted/rejected)
- Support vLLM's `--quantization` flag for even smaller models
- Integrate with OMK's batch runner for parallel generation

## References

- vLLM docs: https://docs.vllm.ai/
- Gemma 4: https://ai.google.dev/gemma
- Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- Colab vLLM setup: `slow-local-model-batch/references/vllm-mtp-colab-setup.md`
