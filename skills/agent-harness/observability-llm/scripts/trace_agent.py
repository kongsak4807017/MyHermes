#!/usr/bin/env python3
"""
Agent tracing utilities for Langfuse, Opik, Helicone, and Phoenix.
"""

import json
import time
import uuid
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class TraceSpan:
    """Represents a single span in a trace."""
    name: str
    span_type: str = "span"
    input_data: Any = None
    output_data: Any = None
    metadata: Dict = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    error: Optional[str] = None
    
    def finish(self, output: Any = None, error: Optional[str] = None):
        self.end_time = time.time()
        if output is not None:
            self.output_data = output
        if error is not None:
            self.error = error
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.span_type,
            "input": self.input_data,
            "output": self.output_data,
            "metadata": self.metadata,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": (self.end_time - self.start_time) * 1000 if self.end_time else None,
            "error": self.error,
        }


@dataclass
class AgentTrace:
    """Represents a complete agent execution trace."""
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "agent-session"
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    spans: list = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    def start_span(self, name: str, span_type: str = "span", input_data: Any = None) -> TraceSpan:
        span = TraceSpan(name=name, span_type=span_type, input_data=input_data)
        self.spans.append(span)
        return span
    
    def finish(self):
        self.end_time = time.time()
    
    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": self.metadata,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": (self.end_time - self.start_time) * 1000 if self.end_time else None,
            "spans": [s.to_dict() for s in self.spans],
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


class SimpleTracer:
    """Simple tracer that works without external dependencies."""
    
    def __init__(self, output_dir: str = "/tmp/traces"):
        self.output_dir = output_dir
        self.active_traces: Dict[str, AgentTrace] = {}
        
    def start_trace(self, name: str = "agent-session", user_id: Optional[str] = None) -> AgentTrace:
        trace = AgentTrace(name=name, user_id=user_id)
        self.active_traces[trace.trace_id] = trace
        return trace
    
    def finish_trace(self, trace_id: str):
        if trace_id in self.active_traces:
            trace = self.active_traces[trace_id]
            trace.finish()
            self._save_trace(trace)
            del self.active_traces[trace_id]
    
    def _save_trace(self, trace: AgentTrace):
        import os
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, f"{trace.trace_id}.json")
        with open(filepath, "w") as f:
            f.write(trace.to_json())
        print(f"Trace saved: {filepath}")


class MetricsCollector:
    """Collect metrics for agent sessions."""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "errors": 0,
            "latencies": [],
        }
    
    def record_request(self, tokens: int, cost: float, latency_ms: float, error: bool = False):
        self.metrics["total_requests"] += 1
        self.metrics["total_tokens"] += tokens
        self.metrics["total_cost"] += cost
        self.metrics["latencies"].append(latency_ms)
        if error:
            self.metrics["errors"] += 1
    
    def get_summary(self) -> dict:
        latencies = self.metrics["latencies"]
        return {
            "total_requests": self.metrics["total_requests"],
            "total_tokens": self.metrics["total_tokens"],
            "total_cost": round(self.metrics["total_cost"], 4),
            "error_rate": self.metrics["errors"] / max(self.metrics["total_requests"], 1),
            "avg_latency_ms": sum(latencies) / max(len(latencies), 1),
            "p99_latency_ms": sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0,
        }


if __name__ == "__main__":
    # Demo
    tracer = SimpleTracer()
    metrics = MetricsCollector()
    
    trace = tracer.start_trace(name="demo-session", user_id="user-123")
    
    span1 = trace.start_span("web_search", input_data={"query": "Python tips"})
    time.sleep(0.1)
    span1.finish(output={"results": ["tip1", "tip2"]})
    metrics.record_request(tokens=100, cost=0.001, latency_ms=100)
    
    span2 = trace.start_span("code_execution", input_data={"code": "print('hello')"})
    time.sleep(0.05)
    span2.finish(output={"stdout": "hello"})
    metrics.record_request(tokens=50, cost=0.0005, latency_ms=50)
    
    tracer.finish_trace(trace.trace_id)
    
    print("\nMetrics Summary:")
    print(json.dumps(metrics.get_summary(), indent=2))
