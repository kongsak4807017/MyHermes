# Observability Patterns

## Tracing Patterns

### OpenTelemetry Trace Structure
```json
{
  "trace_id": "abc123",
  "span_id": "span456",
  "name": "agent.tool_call",
  "start_time": "2026-01-01T00:00:00Z",
  "end_time": "2026-01-01T00:00:01Z",
  "attributes": {
    "agent.id": "agent-001",
    "tool.name": "terminal",
    "tool.input": "ls -la",
    "tool.output": "...",
    "token.usage": 150,
    "latency_ms": 1000
  }
}
```

### Metrics to Track
- Token usage (input/output)
- Latency (TTFT, total)
- Cost per request
- Error rate
- Tool call frequency
- Session duration

## Logging Patterns

### Structured Log Format
```json
{
  "timestamp": "2026-01-01T00:00:00Z",
  "level": "INFO",
  "agent_id": "agent-001",
  "session_id": "sess-123",
  "event": "tool_call",
  "tool": "terminal",
  "input": "ls -la",
  "output": "...",
  "duration_ms": 1000
}
```

## Alerting Rules
- Error rate > 5% for 5 minutes
- Latency p99 > 10 seconds
- Cost per hour > $10
- Token usage spike > 3x baseline
