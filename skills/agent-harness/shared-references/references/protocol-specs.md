# Protocol Specifications

## Model Context Protocol (MCP)

### Server Configuration
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    },
    "terminal": {
      "command": "uvx",
      "args": ["mcp-server-terminal"]
    }
  }
}
```

### Tool Definition
```json
{
  "name": "read_file",
  "description": "Read a file from the filesystem",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Absolute path to the file"
      }
    },
    "required": ["path"]
  }
}
```

## Agent Client Protocol (ACP)

### Session Init
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {}
    }
  },
  "id": 1
}
```

## AGENTS.md Format
```markdown
# AGENTS.md

## Project Overview
Brief description of the project.

## Architecture
- Frontend: React + TypeScript
- Backend: FastAPI + Python
- Database: PostgreSQL

## Development Guidelines
- Use TypeScript strict mode
- Follow PEP 8 for Python
- Run tests before committing

## Common Commands
```bash
# Start dev server
npm run dev

# Run tests
pytest

# Lint
npm run lint
```

## Important Files
- `src/config.ts` - Configuration
- `src/api/` - API endpoints
- `tests/` - Test files
```
