---
title: OpenClaw Cost Visibility Patterns
description: Implement tiered pricing and cost tracking for multi-model usage
---

# OpenClaw Cost Visibility for Hermes

## Pattern Overview

OpenClaw 2026.4.20-beta.1 เพิ่ม:
- **Tiered model pricing** from cached catalogs
- **Cost estimates** ใน token-usage reports
- **Model-specific pricing** (Moonshot Kimi K2.6/K2.5)

## Implementation

```python
# hermes_cli/cost_tracker.py

import json
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class ModelPricing:
    """Pricing tier for a model."""
    model_id: str
    input_per_1m: float  # USD per 1M input tokens
    output_per_1m: float  # USD per 1M output tokens
    cached_input_per_1m: Optional[float] = None
    
    def calculate(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD."""
        input_cost = (input_tokens / 1_000_000) * self.input_per_1m
        output_cost = (output_tokens / 1_000_000) * self.output_per_1m
        return round(input_cost + output_cost, 6)


# Cached pricing catalog (update periodically)
DEFAULT_PRICING = {
    # Anthropic
    "claude-sonnet-4": ModelPricing("claude-sonnet-4", 3.0, 15.0),
    "claude-opus-4": ModelPricing("claude-opus-4", 15.0, 75.0),
    "claude-haiku-4": ModelPricing("claude-haiku-4", 0.25, 1.25),
    
    # OpenAI
    "gpt-5": ModelPricing("gpt-5", 1.25, 10.0),
    "gpt-4o": ModelPricing("gpt-4o", 2.5, 10.0),
    
    # Moonshot / Kimi
    "kimi-k2.6": ModelPricing("kimi-k2.6", 2.0, 8.0),
    "kimi-k2.5": ModelPricing("kimi-k2.5", 1.5, 6.0),
    
    # OpenRouter free tier
    "free": ModelPricing("free", 0.0, 0.0),
}


class CostTracker:
    """Track costs across models with OpenClaw-style visibility."""
    
    def __init__(self, cache_path: Optional[Path] = None):
        self.cache_path = cache_path or (Path.home() / ".hermes" / "cost_cache.json")
        self.pricing = self._load_pricing()
        self.daily_usage: Dict[str, Dict] = {}
        
    def _load_pricing(self) -> Dict[str, ModelPricing]:
        """Load pricing from cache or defaults."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path) as f:
                    data = json.load(f)
                return {k: ModelPricing(**v) for k, v in data.items()}
            except Exception:
                pass
        return DEFAULT_PRICING.copy()
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a request before sending."""
        # Normalize model name
        model_key = model.split("/")[-1] if "/" in model else model
        pricing = self.pricing.get(model_key, ModelPricing(model_key, 3.0, 15.0))
        return pricing.calculate(input_tokens, output_tokens)
    
    def log_usage(self, model: str, input_tokens: int, output_tokens: int, actual_cost: Optional[float] = None):
        """Log actual usage for reporting."""
        cost = actual_cost or self.estimate_cost(model, input_tokens, output_tokens)
        
        if model not in self.daily_usage:
            self.daily_usage[model] = {
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0
            }
        
        self.daily_usage[model]["calls"] += 1
        self.daily_usage[model]["input_tokens"] += input_tokens
        self.daily_usage[model]["output_tokens"] += output_tokens
        self.daily_usage[model]["cost"] += cost
    
    def get_report(self) -> Dict:
        """Generate cost report (OpenClaw-style)."""
        total_cost = sum(u["cost"] for u in self.daily_usage.values())
        total_tokens = sum(u["input_tokens"] + u["output_tokens"] for u in self.daily_usage.values())
        
        return {
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "by_model": self.daily_usage,
            "top_expensive": sorted(
                self.daily_usage.items(),
                key=lambda x: x[1]["cost"],
                reverse=True
            )[:5]
        }
```

## Usage

```python
from hermes_cli.cost_tracker import CostTracker

tracker = CostTracker()

# Pre-request estimate (OpenClaw pattern)
estimated = tracker.estimate_cost("claude-sonnet-4", 4000, 1000)
print(f"Estimated cost: ${estimated:.4f}")

# Post-request logging
tracker.log_usage("claude-sonnet-4", 4000, 1200)

# Daily report
report = tracker.get_report()
print(f"Today: ${report['total_cost_usd']} for {report['total_tokens']} tokens")
```

## Key Takeaways

1. **Pre-flight estimates** - คำนวณก่อนส่ง (OpenClaw pattern)
2. **Cached catalogs** - เก็บ pricing ไว้ load เร็วๆ
3. **Model normalization** - รองรับ provider/model ID หลายรูปแบบ
4. **Daily aggregation** - รายงานรายวันเหมือน OpenClaw

## Reference

- OpenClaw: v2026.4.20-beta.1 cost visibility improvements
- File: `~/.hermes/skills/openclaw-learnings/references/cost-patterns.md`
