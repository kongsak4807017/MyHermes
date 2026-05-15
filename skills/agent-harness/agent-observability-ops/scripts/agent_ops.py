#!/usr/bin/env python3
"""
Reliability operations for AI agents.
Health checks, circuit breakers, retries, and alerting.
"""

import time
import random
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class HealthStatus:
    """Health check status."""
    healthy: bool
    checks: Dict[str, Dict]
    timestamp: float = field(default_factory=time.time)


class HealthChecker:
    """Health checker for agent components."""
    
    def __init__(self):
        self.checks: Dict[str, Callable[[], Dict]] = {}
    
    def register(self, name: str, check_fn: Callable[[], Dict]):
        """Register a health check."""
        self.checks[name] = check_fn
    
    def check(self) -> HealthStatus:
        """Run all health checks."""
        results = {}
        all_healthy = True
        
        for name, check_fn in self.checks.items():
            try:
                result = check_fn()
                results[name] = {
                    "healthy": result.get("healthy", True),
                    "message": result.get("message", "OK"),
                    "latency_ms": result.get("latency_ms", 0),
                }
                if not results[name]["healthy"]:
                    all_healthy = False
            except Exception as e:
                results[name] = {
                    "healthy": False,
                    "message": str(e),
                    "latency_ms": 0,
                }
                all_healthy = False
        
        return HealthStatus(healthy=all_healthy, checks=results)
    
    def check_component(self, name: str) -> Dict:
        """Check a single component."""
        if name not in self.checks:
            return {"healthy": False, "message": "Unknown component"}
        
        try:
            return self.checks[name]()
        except Exception as e:
            return {"healthy": False, "message": str(e)}


class CircuitBreaker:
    """Circuit breaker pattern."""
    
    def __init__(self, failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
            else:
                raise CircuitBreakerOpen("Circuit breaker is OPEN")
        
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                raise CircuitBreakerOpen("Circuit breaker is HALF_OPEN (max calls reached)")
            self.half_open_calls += 1
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failures = 0
            self.half_open_calls = 0
        else:
            self.failures = max(0, self.failures - 1)
    
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def get_status(self) -> Dict:
        return {
            "state": self.state.value,
            "failures": self.failures,
            "threshold": self.failure_threshold,
            "last_failure": self.last_failure_time,
            "recovery_timeout": self.recovery_timeout,
        }


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class RetryPolicy:
    """Retry policy with exponential backoff."""
    
    def __init__(self, max_retries: int = 3,
                 backoff_factor: float = 2.0,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exceptions: tuple = (Exception,)):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exceptions = exceptions
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except self.exceptions as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with jitter."""
        delay = self.base_delay * (self.backoff_factor ** attempt)
        jitter = random.uniform(0, delay * 0.1)
        return min(delay + jitter, self.max_delay)
    
    def execute_async(self, func: Callable, *args, **kwargs):
        """Async version (placeholder)."""
        return self.execute(func, *args, **kwargs)


class AlertManager:
    """Alert manager for agent operations."""
    
    def __init__(self):
        self.thresholds: Dict[str, float] = {}
        self.alerts: List[Dict] = []
        self.alert_handlers: List[Callable] = []
    
    def set_threshold(self, metric: str, threshold: float):
        """Set alert threshold."""
        self.thresholds[metric] = threshold
    
    def add_handler(self, handler: Callable):
        """Add alert handler."""
        self.alert_handlers.append(handler)
    
    def check(self, metrics: Dict[str, float]):
        """Check metrics against thresholds."""
        for metric, value in metrics.items():
            if metric in self.thresholds:
                threshold = self.thresholds[metric]
                if value > threshold:
                    alert = {
                        "timestamp": time.time(),
                        "metric": metric,
                        "value": value,
                        "threshold": threshold,
                        "severity": self._get_severity(value, threshold),
                    }
                    self.alerts.append(alert)
                    self._notify(alert)
    
    def _get_severity(self, value: float, threshold: float) -> str:
        ratio = value / threshold
        if ratio > 3:
            return "critical"
        elif ratio > 2:
            return "high"
        elif ratio > 1.5:
            return "medium"
        return "low"
    
    def _notify(self, alert: Dict):
        """Notify all handlers."""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception:
                pass
    
    def get_alerts(self, severity: str = None) -> List[Dict]:
        """Get alerts, optionally filtered by severity."""
        if severity:
            return [a for a in self.alerts if a["severity"] == severity]
        return self.alerts.copy()
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts = []


class Timeout:
    """Timeout wrapper for operations."""
    
    def __init__(self, seconds: float):
        self.seconds = seconds
    
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        pass
    
    def is_expired(self) -> bool:
        return time.time() - self.start > self.seconds
    
    def remaining(self) -> float:
        return max(0, self.seconds - (time.time() - self.start))


if __name__ == "__main__":
    import json
    
    # Demo: Health checker
    health = HealthChecker()
    health.register("llm_api", lambda: {"healthy": True, "latency_ms": 100})
    health.register("db", lambda: {"healthy": False, "message": "Connection timeout"})
    
    status = health.check()
    print("Health Status:")
    print(json.dumps({"healthy": status.healthy, "checks": status.checks}, indent=2))
    
    # Demo: Circuit breaker
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
    
    def flaky_func():
        if random.random() < 0.7:
            raise Exception("Random failure")
        return "success"
    
    for i in range(10):
        try:
            result = breaker.call(flaky_func)
            print(f"Call {i+1}: {result}")
        except CircuitBreakerOpen:
            print(f"Call {i+1}: Circuit breaker OPEN")
        except Exception as e:
            print(f"Call {i+1}: {e}")
    
    print("\nCircuit Breaker Status:")
    print(json.dumps(breaker.get_status(), indent=2, default=str))
    
    # Demo: Retry policy
    retry = RetryPolicy(max_retries=3, base_delay=0.1)
    
    attempt = 0
    def failing_then_succeeding():
        global attempt
        attempt += 1
        if attempt < 3:
            raise Exception(f"Attempt {attempt} failed")
        return "Success!"
    
    try:
        result = retry.execute(failing_then_succeeding)
        print(f"\nRetry Result: {result}")
    except Exception as e:
        print(f"\nRetry Failed: {e}")
    
    # Demo: Alert manager
    alerts = AlertManager()
    alerts.set_threshold("error_rate", 0.05)
    alerts.set_threshold("latency_p99", 1000)
    
    def print_alert(alert):
        print(f"ALERT [{alert['severity'].upper()}]: {alert['metric']} = {alert['value']}")
    
    alerts.add_handler(print_alert)
    alerts.check({"error_rate": 0.08, "latency_p99": 1200})
    
    print("\nActive Alerts:")
    print(json.dumps(alerts.get_alerts(), indent=2))
