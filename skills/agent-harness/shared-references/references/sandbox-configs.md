# Sandbox Configurations

## Docker Sandbox
```yaml
# docker-compose.sandbox.yml
version: '3.8'
services:
  agent-sandbox:
    image: python:3.11-slim
    container_name: agent-sandbox
    volumes:
      - ./workspace:/workspace
      - ./scripts:/scripts:ro
    working_dir: /workspace
    network_mode: none  # Isolate network
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETUID
      - SETGID
    mem_limit: 512m
    cpus: 1.0
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
```

## Firejail Profile
```bash
# agent-sandbox.profile
include /etc/firejail/default.profile

# Restrict network
net none

# Restrict filesystem
whitelist ~/workspace
read-only ~/scripts

# Resource limits
rlimit-as 512000000
rlimit-cpu 300
rlimit-fsize 100000000
rlimit-nofile 50

# Disable dangerous features
nosound
no3d
nodvd
notv
nou2f
novideo
```

## Python Sandbox (RestrictedPython)
```python
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins

def execute_sandboxed(code: str):
    """Execute Python code in restricted environment."""
    restricted_globals = {
        "__builtins__": safe_builtins,
        "_getattr_": getattr,
        "_write_": lambda x: x,
    }
    
    compiled = compile_restricted(code, "<sandbox>", "exec")
    exec(compiled, restricted_globals)
```
