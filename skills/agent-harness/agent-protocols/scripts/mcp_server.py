#!/usr/bin/env python3
"""
MCP server implementation for agent tools.
Pure Python implementation without external dependencies.
"""

import json
import sys
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Tool:
    """MCP tool definition."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable = None


@dataclass
class ToolResult:
    """Result from tool execution."""
    content: List[Dict]
    is_error: bool = False


class MCPServer:
    """Simple MCP server implementation."""
    
    def __init__(self, name: str):
        self.name = name
        self.tools: Dict[str, Tool] = {}
        self.resources: Dict[str, Callable] = {}
    
    def tool(self, name: str = None, description: str = "",
             parameters: Dict = None):
        """Decorator to register a tool."""
        def decorator(func: Callable):
            tool_name = name or func.__name__
            self.tools[tool_name] = Tool(
                name=tool_name,
                description=description or func.__doc__ or "",
                parameters=parameters or {},
                handler=func,
            )
            return func
        return decorator
    
    def resource(self, uri: str):
        """Decorator to register a resource."""
        def decorator(func: Callable):
            self.resources[uri] = func
            return func
        return decorator
    
    def list_tools(self) -> List[Dict]:
        """List available tools."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            }
            for t in self.tools.values()
        ]
    
    def call_tool(self, name: str, arguments: Dict) -> ToolResult:
        """Call a tool."""
        if name not in self.tools:
            return ToolResult(
                content=[{"type": "text", "text": f"Tool '{name}' not found"}],
                is_error=True,
            )
        
        tool = self.tools[name]
        try:
            result = tool.handler(**arguments)
            return ToolResult(
                content=[{"type": "text", "text": str(result)}],
            )
        except Exception as e:
            return ToolResult(
                content=[{"type": "text", "text": str(e)}],
                is_error=True,
            )
    
    def handle_request(self, request: Dict) -> Dict:
        """Handle an MCP request."""
        method = request.get("method")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                    },
                    "serverInfo": {"name": self.name, "version": "1.0.0"},
                },
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"tools": self.list_tools()},
            }
        
        elif method == "tools/call":
            params = request.get("params", {})
            result = self.call_tool(params.get("name"), params.get("arguments", {}))
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": asdict(result),
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
    
    def run_stdio(self):
        """Run server over stdio."""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            
            except json.JSONDecodeError:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                }), flush=True)
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": str(e)},
                }), flush=True)


class MCPClient:
    """Simple MCP client implementation."""
    
    def __init__(self):
        self.tools: List[Dict] = []
    
    def connect(self, server_params: Dict):
        """Connect to MCP server."""
        # Stub for actual implementation
        pass
    
    def list_tools(self) -> List[Dict]:
        """List available tools."""
        return self.tools
    
    def call_tool(self, name: str, arguments: Dict) -> ToolResult:
        """Call a tool."""
        # Stub for actual implementation
        return ToolResult(content=[{"type": "text", "text": "Stub result"}])


def create_agents_md(project_name: str, stack: List[str],
                     commands: Dict[str, str],
                     guidelines: List[str]) -> str:
    """Generate AGENTS.md content."""
    lines = [
        f"# AGENTS.md",
        f"",
        f"## Project",
        f"{project_name}",
        f"",
        f"## Stack",
    ]
    
    for item in stack:
        lines.append(f"- {item}")
    
    lines.extend([
        f"",
        f"## Commands",
        f"```bash",
    ])
    
    for cmd, desc in commands.items():
        lines.append(f"{cmd}  # {desc}")
    
    lines.extend([
        f"```",
        f"",
        f"## Guidelines",
    ])
    
    for guideline in guidelines:
        lines.append(f"- {guideline}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo: MCP Server
    server = MCPServer("demo-server")
    
    @server.tool(name="read_file", description="Read a file",
                 parameters={"path": {"type": "string"}})
    def read_file(path: str) -> str:
        try:
            with open(path) as f:
                return f.read()
        except FileNotFoundError:
            return f"File not found: {path}"
    
    @server.tool(name="list_dir", description="List directory contents",
                 parameters={"path": {"type": "string"}})
    def list_dir(path: str = ".") -> List[str]:
        import os
        return os.listdir(path)
    
    print("MCP Server Tools:")
    print(json.dumps(server.list_tools(), indent=2))
    
    # Test tool call
    result = server.call_tool("list_dir", {"path": "."})
    print("\nTool Result:")
    print(json.dumps(asdict(result), indent=2))
    
    # Demo: AGENTS.md
    agents_md = create_agents_md(
        project_name="MyProject",
        stack=["React", "FastAPI", "PostgreSQL"],
        commands={
            "npm run dev": "Start dev server",
            "pytest": "Run tests",
            "npm run build": "Build for production",
        },
        guidelines=[
            "Use TypeScript strict mode",
            "Follow PEP 8 for Python",
            "Write tests for new features",
        ],
    )
    
    print("\nAGENTS.md:")
    print(agents_md)
