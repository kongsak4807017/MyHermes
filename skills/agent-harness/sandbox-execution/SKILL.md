---
name: sandbox-execution
description: "Secure sandbox execution for AI agents using Docker, Firejail, and restricted Python environments."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [docker, firejail]
platforms: [linux]
metadata:
  hermes:
    tags: [Sandbox, Security, Docker, Firejail, Execution, Isolation, Container]
---

# Sandbox Execution for Agents

## What's inside

Secure sandbox execution: Docker containers, Firejail profiles, restricted Python, and resource limits for safe agent code execution.

## Quick start

**Docker sandbox**:
```bash
docker run --rm \
  --network none \
  --memory 512m \
  --cpus 1.0 \
  --read-only \
  --tmpfs /tmp:noexec,nosuid,size=100m \
  -v $(pwd)/workspace:/workspace \
  python:3.11-slim \
  python /workspace/script.py
```

**Firejail sandbox**:
```bash
firejail --net=none --rlimit-cpu=300 python script.py
```

## Common workflows

### Workflow 1: Docker Sandbox

```bash
# Build sandbox image
docker build -t agent-sandbox -f Dockerfile.sandbox .

# Run with restrictions
docker run --rm \
  --name agent-sandbox \
  --network none \
  --memory 512m \
  --cpus 1.0 \
  --read-only \
  --tmpfs /tmp:noexec,nosuid,size=100m \
  --cap-drop ALL \
  --cap-add CHOWN \
  --security-opt no-new-privileges:true \
  -v $(pwd)/workspace:/workspace:rw \
  agent-sandbox
```

### Workflow 2: Firejail Profile

```bash
# Create profile
cat > agent.profile << 'EOF'
include /etc/firejail/default.profile
net none
whitelist ~/workspace
read-only ~/scripts
rlimit-cpu 300
rlimit-as 512000000
rlimit-fsize 100000000
rlimit-nofile 50
nosound
no3d
nodvd
notv
nou2f
novideo
EOF

# Run
firejail --profile=agent.profile python script.py
```

### Workflow 3: Restricted Python

```python
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins

def execute_sandboxed(code: str):
    restricted_globals = {
        "__builtins__": safe_builtins,
        "_getattr_": getattr,
        "_write_": lambda x: x,
    }
    compiled = compile_restricted(code, "<sandbox>", "exec")
    exec(compiled, restricted_globals)
```

## Resource Limits

| Resource | Docker | Firejail |
|----------|--------|----------|
| Memory | `--memory 512m` | `rlimit-as 512000000` |
| CPU | `--cpus 1.0` | `rlimit-cpu 300` |
| Disk | `--read-only` | `read-only` |
| Network | `--network none` | `net none` |
| Files | `--tmpfs /tmp` | `whitelist` |

## Common issues

**Issue: Permission denied**
- Add `--cap-add` for needed capabilities
- Use `--user $(id -u)` for user mapping

**Issue: Out of memory**
- Increase `--memory` limit
- Use swap if needed
- Optimize code

## Resources

- Daytona: https://daytona.io
- E2B: https://e2b.dev
- CUA: https://github.com/trycua/cua
