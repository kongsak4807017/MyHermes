---
name: agent-guardrails-security
description: "Security and governance for AI agents: permission boundaries, audit logging, data retention policies, and compliance frameworks."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Security, Governance, Compliance, Audit, Permissions, Data Retention, Policy, Agent Security]
---

# Agent Security & Governance

## What's inside

Security and governance framework for AI agents: permission boundaries, audit logging, data retention policies, and compliance frameworks.

## Quick start

```python
from agent_security import SecurityPolicy, AuditLogger

# Define policy
policy = SecurityPolicy(
    max_requests_per_minute=100,
    allowed_tools=["terminal", "file", "web"],
    forbidden_commands=["rm -rf /", "format", "mkfs"],
    data_retention_days=30,
)

# Check permission
if policy.is_allowed("terminal", "ls -la"):
    result = run_command("ls -la")
    AuditLogger.log("terminal", "ls -la", result)
```

## Common workflows

### Workflow 1: Permission Boundaries

```python
class PermissionBoundary:
    def __init__(self, role: str):
        self.role = role
        self.permissions = self._load_permissions(role)
    
    def can_execute(self, tool: str, command: str) -> bool:
        if tool not in self.permissions["tools"]:
            return False
        for forbidden in self.permissions["forbidden"]:
            if forbidden in command:
                return False
        return True
```

### Workflow 2: Audit Logging

```python
class AuditLogger:
    @staticmethod
    def log(action: str, input_data: str, output_data: str,
            user_id: str = None, session_id: str = None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "input": input_data[:1000],  # Truncate
            "output": output_data[:1000],
            "user_id": user_id,
            "session_id": session_id,
        }
        # Append to audit log
        with open("audit.log", "a") as f:
            f.write(json.dumps(entry) + "\n")
```

### Workflow 3: Data Retention

```python
class DataRetention:
    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
    
    def cleanup(self, data_dir: str):
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        for file in Path(data_dir).glob("*"):
            if datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
                file.unlink()
                print(f"Deleted: {file}")
```

## Security Checklist

- [ ] Permission boundaries defined
- [ ] Audit logging enabled
- [ ] Data retention policy set
- [ ] Input validation active
- [ ] Output filtering active
- [ ] Rate limiting configured
- [ ] Error handling secure
- [ ] Secrets not logged

## Resources

- OWASP AI Security: https://owasp.org/www-project-ai-security/
- NIST AI Risk Framework: https://www.nist.gov/itl/ai-risk-management-framework
