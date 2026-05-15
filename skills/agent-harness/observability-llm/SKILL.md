---
name: observability-llm
description: "LLM observability and monitoring: tracing, metrics, cost tracking, and debugging for agent workflows using Langfuse, Opik, Helicone, and Phoenix patterns."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [langfuse, opik, helicone, arize-phoenix]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Observability, LLMOps, Tracing, Metrics, Langfuse, Opik, Helicone, Phoenix, Cost Tracking, Debugging]
---

# Observability for LLM Agents

## What's inside

Comprehensive observability stack for LLM agents: tracing requests, tracking metrics, monitoring costs, and debugging failures. Covers Langfuse, Opik, Helicone, and Phoenix patterns.

## Quick start

**Install Langfuse (self-hosted)**:
```bash
docker compose -f docker-compose.langfuse.yml up -d
```

**Trace an agent session**:
```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    host="http://localhost:3000"
)

# Start a trace
trace = langfuse.trace(name="agent-session", user_id="user-123")

# Log a generation
generation = trace.generation(
    name="llm-call",
    model="gpt-4",
    input={"messages": [{"role": "user", "content": "Hello"}]},
    output={"content": "Hi there!"}
)

# Update with usage
generation.update(
    usage={"input": 10, "output": 5, "total": 15},
    cost={"input": 0.0003, "output": 0.0006}
)
```

## Common workflows

### Workflow 1: Setup Langfuse Self-Hosted

```bash
# docker-compose.langfuse.yml
version: '3.8'
services:
  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/langfuse
      - NEXTAUTH_SECRET=secret
      - SALT=salt
      - ENCRYPTION_KEY=key
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=langfuse
```

### Workflow 2: Trace Agent Tool Calls

```python
from langfuse.decorators import observe

@observe()
def agent_run(query: str):
    # Tool call 1
    with langfuse.span(name="web_search") as span:
        results = search_web(query)
        span.update(output=results)
    
    # Tool call 2
    with langfuse.span(name="code_execution") as span:
        output = execute_code(results)
        span.update(output=output)
    
    # LLM call
    response = llm.generate(f"Query: {query}\nResults: {output}")
    return response
```

### Workflow 3: Cost Tracking with Helicone

```python
import openai

# Configure Helicone
openai.api_base = "https://oai.hconeai.com/v1"
openai.default_headers = {
    "Helicone-Auth": "Bearer sk-helicone-...",
    "Helicone-Cache-Enabled": "true"
}

# All requests automatically tracked
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# View dashboard at https://helicone.ai
```

### Workflow 4: Debug with Phoenix

```python
import phoenix as px
from phoenix.trace.langchain import LangChainInstrumentor

# Launch Phoenix
session = px.launch_app()

# Instrument LangChain
LangChainInstrumentor().instrument()

# Run your agent
agent.run("What is the weather?")

# View traces in Phoenix UI
print(f"Phoenix UI: {session.url}")
```

## Metrics to Track

| Metric | Tool | Alert Threshold |
|--------|------|----------------|
| Token usage | Langfuse, Helicone | > 10k/session |
| Latency (TTFT) | All | > 2 seconds |
| Cost per request | Helicone | > $0.50 |
| Error rate | All | > 5% |
| Tool call frequency | Langfuse | > 50/session |

## Common issues

**Issue: Traces not showing**
- Verify API keys
- Check network connectivity
- Ensure `langfuse.flush()` is called

**Issue: High latency**
- Enable Helicone caching
- Use batch processing
- Check model selection

## Resources

- Langfuse: https://langfuse.com
- Opik: https://opik.comet.com
- Helicone: https://helicone.ai
- Phoenix: https://phoenix.arize.com
