#!/usr/bin/env python3
"""
Security policy and governance for AI agents.
Permission boundaries, audit logging, and data retention.
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    max_requests_per_minute: int = 100
    max_tokens_per_request: int = 10000
    allowed_tools: List[str] = None
    forbidden_commands: List[str] = None
    data_retention_days: int = 30
    require_approval_for: List[str] = None
    
    def __post_init__(self):
        if self.allowed_tools is None:
            self.allowed_tools = ["terminal", "file", "web", "search"]
        if self.forbidden_commands is None:
            self.forbidden_commands = [
                "rm -rf /", "rm -rf ~", "format", "mkfs",
                "> /dev/sda", "dd if=/dev/zero",
                "shutdown", "reboot", "init 0",
            ]
        if self.require_approval_for is None:
            self.require_approval_for = [
                "delete", "remove", "drop", "truncate",
                "grant", "revoke", "chmod 777",
            ]
    
    def is_tool_allowed(self, tool: str) -> bool:
        return tool in self.allowed_tools
    
    def is_command_allowed(self, command: str) -> bool:
        for forbidden in self.forbidden_commands:
            if forbidden in command.lower():
                return False
        return True
    
    def requires_approval(self, action: str) -> bool:
        for pattern in self.require_approval_for:
            if pattern in action.lower():
                return True
        return False


class AuditLogger:
    """Audit logger for agent actions."""
    
    def __init__(self, log_dir: str = "/tmp/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    def log(self, action: str, tool: str, input_data: str,
            output_data: str = "", user_id: str = None,
            session_id: str = None, success: bool = True,
            error: str = None):
        """Log an action."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "tool": tool,
            "input_hash": self._hash(input_data),
            "output_hash": self._hash(output_data),
            "user_id": user_id,
            "session_id": session_id,
            "success": success,
            "error": error,
        }
        
        with open(self.current_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get_logs(self, start_time: datetime = None,
                 end_time: datetime = None,
                 user_id: str = None) -> List[Dict]:
        """Retrieve logs with filters."""
        logs = []
        
        for log_file in self.log_dir.glob("audit_*.jsonl"):
            with open(log_file) as f:
                for line in f:
                    entry = json.loads(line.strip())
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    
                    if start_time and entry_time < start_time:
                        continue
                    if end_time and entry_time > end_time:
                        continue
                    if user_id and entry.get("user_id") != user_id:
                        continue
                    
                    logs.append(entry)
        
        return sorted(logs, key=lambda x: x["timestamp"])
    
    def get_summary(self, days: int = 7) -> Dict:
        """Get audit summary."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        logs = self.get_logs(start_time=cutoff)
        
        total = len(logs)
        successful = sum(1 for l in logs if l.get("success", True))
        failed = total - successful
        
        by_tool = {}
        for log in logs:
            tool = log.get("tool", "unknown")
            by_tool[tool] = by_tool.get(tool, 0) + 1
        
        return {
            "period_days": days,
            "total_actions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "by_tool": by_tool,
        }


class DataRetention:
    """Manage data retention policies."""
    
    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
    
    def cleanup(self, data_dir: str, dry_run: bool = True) -> List[Path]:
        """Clean up old data."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        data_path = Path(data_dir)
        
        to_delete = []
        for file in data_path.rglob("*"):
            if file.is_file():
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if mtime < cutoff:
                    to_delete.append(file)
        
        if not dry_run:
            for file in to_delete:
                file.unlink()
                print(f"Deleted: {file}")
        
        return to_delete
    
    def get_retention_report(self, data_dir: str) -> Dict:
        """Get retention report."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        data_path = Path(data_dir)
        
        total_files = 0
        old_files = 0
        total_size = 0
        old_size = 0
        
        for file in data_path.rglob("*"):
            if file.is_file():
                size = file.stat().st_size
                total_files += 1
                total_size += size
                
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if mtime < cutoff:
                    old_files += 1
                    old_size += size
        
        return {
            "retention_days": self.retention_days,
            "total_files": total_files,
            "old_files": old_files,
            "total_size_mb": total_size / (1024 * 1024),
            "old_size_mb": old_size / (1024 * 1024),
            "cleanup_percentage": (old_files / total_files * 100) if total_files > 0 else 0,
        }


class PermissionBoundary:
    """Permission boundary for agent actions."""
    
    def __init__(self, policy: SecurityPolicy, role: str = "user"):
        self.policy = policy
        self.role = role
        self.approvals: Set[str] = set()
    
    def check(self, tool: str, command: str) -> Dict:
        """Check if action is allowed."""
        # Check tool
        if not self.policy.is_tool_allowed(tool):
            return {
                "allowed": False,
                "reason": f"Tool '{tool}' not allowed",
                "requires_approval": False,
            }
        
        # Check command
        if not self.policy.is_command_allowed(command):
            return {
                "allowed": False,
                "reason": "Command contains forbidden pattern",
                "requires_approval": False,
            }
        
        # Check approval
        if self.policy.requires_approval(command):
            action_id = f"{tool}:{command}"
            if action_id not in self.approvals:
                return {
                    "allowed": False,
                    "reason": "Requires approval",
                    "requires_approval": True,
                    "action_id": action_id,
                }
        
        return {
            "allowed": True,
            "reason": None,
            "requires_approval": False,
        }
    
    def approve(self, action_id: str):
        """Approve an action."""
        self.approvals.add(action_id)
    
    def revoke(self, action_id: str):
        """Revoke approval."""
        self.approvals.discard(action_id)


if __name__ == "__main__":
    # Demo
    policy = SecurityPolicy()
    
    # Test permission checks
    boundary = PermissionBoundary(policy)
    
    print("Permission Checks:")
    print(boundary.check("terminal", "ls -la"))
    print(boundary.check("terminal", "rm -rf /"))
    print(boundary.check("dangerous_tool", "do_something"))
    
    # Test audit logging
    logger = AuditLogger()
    logger.log("file_read", "file", "/etc/passwd", "root:x:0:0")
    logger.log("terminal", "terminal", "ls -la", "file1 file2")
    
    print("\nAudit Summary:")
    print(json.dumps(logger.get_summary(), indent=2))
    
    # Test data retention
    retention = DataRetention(retention_days=30)
    report = retention.get_retention_report("/tmp")
    print("\nRetention Report:")
    print(json.dumps(report, indent=2))
