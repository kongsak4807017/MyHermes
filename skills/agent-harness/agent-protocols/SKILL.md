---
name: agent-protocols
description: "Agent protocols and interfaces: MCP, ACP, AGENTS.md, and spec-driven development patterns for tool interoperability."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [MCP, ACP, AGENTS.md, Protocols, Tool Interface, Spec-Driven, Interoperability]
---

# Agent Protocols

## What's inside

Agent protocols and interfaces: MCP (Model Context Protocol), ACP (Agent Client Protocol), AGENTS.md format, and spec-driven development patterns.

## Quick start

**MCP Server**:
```python
from mcp.server import Server

app = Server("my-server")

@app.tool()
def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()

@app.resource("file://{path}")
def get_file(path: str) -> str:
    return read_file(path)
```

**AGENTS.md**:
```markdown
# AGENTS.md

## Project
MyProject - A web application

## Stack
- Frontend: React
- Backend: FastAPI

## Commands
```bash
npm run dev    # Start dev server
pytest         # Run tests
```
```

## Common workflows

### Workflow 1: MCP Server

```python
from mcp.server import Server, stdio_server

app = Server("filesystem")

@app.tool()
def list_files(directory: str) -> list:
    import os
    return os.listdir(directory)

@app.tool()
def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()

# Run server
async with stdio_server() as streams:
    await app.run(streams)
```

### Workflow 2: MCP Client

```python
from mcp.client import ClientSession, stdio_client
from mcp.types import TextContent

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # List tools
        tools = await session.list_tools()
        
        # Call tool
        result = await session.call_tool("read_file", {"path": "/tmp/test.txt"})
        print(result.content[0].text)
```

### Workflow 3: AGENTS.md

```markdown
# AGENTS.md

## Overview
Brief project description.

## Architecture
- Layer 1: ...
- Layer 2: ...

## Development
### Setup
```bash
pip install -r requirements.txt
```

### Testing
```bash
pytest
```

## Guidelines
- Rule 1
- Rule 2
```

## Protocols

| Protocol | Purpose | Status |
|----------|---------|--------|
| MCP | Tool interoperability | Active |
| ACP | Agent client sessions | Draft |
| AGENTS.md | Repo instructions | Community |

## Resources

- MCP: https://modelcontextprotocol.io
- ACP: https://github.com/openclaw/acpx
- AGENTS.md: https://github.com/agentsmd/agents.md
