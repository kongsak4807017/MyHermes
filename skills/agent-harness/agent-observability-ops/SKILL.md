---
name: agent-observability-ops
description: "Reliability operations for agents: health checks, circuit breakers, retries, alerting, and incident response."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Reliability, Health Check, Circuit Breaker, Retry, Alerting, Incident Response, SRE, Operations]
---

# Agent Observability Operations

## What's inside

Reliability operations for AI agents: health checks, circuit breakers, retries, alerting, and incident response patterns.

## Quick start

```python
from agent_ops import HealthChecker, CircuitBreaker, RetryPolicy

# Health check
health = HealthChecker()
status = health.check()
print(status.healthy)  # True/False

# Circuit breaker
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

try:
    with breaker:
        result = risky_operation()
except CircuitBreakerOpen:
    print("Circuit breaker is open")

# Retry policy
retry = RetryPolicy(max_retries=3, backoff_factor=2)
result = retry.execute(lambda: api_call())
```

## Common workflows

### Workflow 1: Health Checks

```python
class HealthChecker:
    def check(self) -> HealthStatus:
        checks = {
            "llm_api": self._check_llm(),
            "database": self._check_db(),
            "disk_space": self._check_disk(),
        }
        
        healthy = all(c.healthy for c in checks.values())
        return HealthStatus(healthy=healthy, checks=checks)
```

### Workflow 2: Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure = None
        self.state = "closed"
    
    def call(self, func):
        if self.state == "open":
            if time.time() - self.last_failure > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise CircuitBreakerOpen()
        
        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
```

### Workflow 3: Alerting

```python
class AlertManager:
    def __init__(self, thresholds: Dict):
        self.thresholds = thresholds
    
    def check(self, metrics: Dict):
        for metric, value in metrics.items():
            if metric in self.thresholds:
                if value > self.thresholds[metric]:
                    self._alert(metric, value)
    
    def _alert(self, metric: str, value: float):
        print(f"ALERT: {metric} = {value} (threshold: {self.thresholds[metric]})")
```

## Reliability Patterns

| Pattern | Use Case |
|---------|----------|
| Health checks | Monitor system health |
| Circuit breaker | Prevent cascade failures |
| Retry | Handle transient errors |
| Timeout | Prevent hung operations |
| Rate limiting | Control load |
| Bulkhead | Isolate failures |
| Fallback | Graceful degradation |

## Resources

- Google SRE Book: https://sre.google/sre-book/table-of-contents/
- AWS Well-Architected: https://aws.amazon.com/architecture/well-architected/
