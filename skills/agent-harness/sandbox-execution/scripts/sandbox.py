#!/usr/bin/env python3
"""
Sandbox execution utilities for agent code.
Supports Docker, Firejail, and restricted Python.
"""

import os
import subprocess
import tempfile
import json
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution."""
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    timeout: int = 300
    network: bool = False
    read_only: bool = True
    max_file_size: int = 100_000_000
    allowed_dirs: List[str] = None
    
    def __post_init__(self):
        if self.allowed_dirs is None:
            self.allowed_dirs = []


class DockerSandbox:
    """Docker-based sandbox execution."""
    
    def __init__(self, config: SandboxConfig = None):
        self.config = config or SandboxConfig()
    
    def run(self, code: str, workdir: Optional[str] = None) -> Dict:
        """Run Python code in Docker sandbox."""
        # Create temp file with code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            script_path = f.name
        
        try:
            # Build docker command
            cmd = [
                'docker', 'run', '--rm',
                '--memory', self.config.memory_limit,
                '--cpus', str(self.config.cpu_limit),
                '--timeout', str(self.config.timeout),
            ]
            
            if not self.config.network:
                cmd.append('--network=none')
            
            if self.config.read_only:
                cmd.append('--read-only')
                cmd.append('--tmpfs=/tmp:noexec,nosuid,size=100m')
            
            # Mount workspace
            workdir = workdir or os.path.dirname(script_path)
            cmd.extend(['-v', f'{workdir}:/workspace'])
            cmd.extend(['-w', '/workspace'])
            
            # Security
            cmd.extend([
                '--cap-drop', 'ALL',
                '--cap-add', 'CHOWN',
                '--security-opt', 'no-new-privileges:true',
            ])
            
            # Image and command
            cmd.extend([
                'python:3.11-slim',
                'python', os.path.basename(script_path)
            ])
            
            # Run
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
            }
            
        finally:
            os.unlink(script_path)
    
    def run_command(self, command: List[str], workdir: Optional[str] = None) -> Dict:
        """Run a command in Docker sandbox."""
        cmd = [
            'docker', 'run', '--rm',
            '--memory', self.config.memory_limit,
            '--cpus', str(self.config.cpu_limit),
        ]
        
        if not self.config.network:
            cmd.append('--network=none')
        
        workdir = workdir or os.getcwd()
        cmd.extend(['-v', f'{workdir}:/workspace'])
        cmd.extend(['-w', '/workspace'])
        
        cmd.extend(['python:3.11-slim'])
        cmd.extend(command)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.config.timeout
        )
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
        }


class FirejailSandbox:
    """Firejail-based sandbox execution."""
    
    def __init__(self, config: SandboxConfig = None):
        self.config = config or SandboxConfig()
    
    def run(self, code: str) -> Dict:
        """Run Python code with Firejail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            script_path = f.name
        
        try:
            cmd = [
                'firejail',
                '--net=none',
                f'--rlimit-cpu={self.config.timeout}',
                f'--rlimit-as={self.config.memory_limit.replace("m", "000000")}',
                f'--rlimit-fsize={self.config.max_file_size}',
                '--nosound',
                '--no3d',
                'python3', script_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
            }
            
        finally:
            os.unlink(script_path)


class RestrictedPythonSandbox:
    """RestrictedPython sandbox for safe code execution."""
    
    def __init__(self):
        self.allowed_builtins = {
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir',
            'enumerate', 'filter', 'float', 'format', 'frozenset',
            'hasattr', 'hex', 'id', 'int', 'isinstance', 'issubclass',
            'iter', 'len', 'list', 'map', 'max', 'min', 'next',
            'oct', 'ord', 'pow', 'print', 'range', 'repr', 'reversed',
            'round', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple',
            'type', 'vars', 'zip'
        }
    
    def run(self, code: str) -> Dict:
        """Execute code in restricted Python environment."""
        import builtins
        
        # Create restricted builtins
        restricted_builtins = {
            name: getattr(builtins, name)
            for name in self.allowed_builtins
            if hasattr(builtins, name)
        }
        
        # Add safe versions
        restricted_builtins['__import__'] = self._safe_import
        
        namespace = {
            '__builtins__': restricted_builtins,
        }
        
        stdout = []
        
        def safe_print(*args, **kwargs):
            stdout.append(' '.join(str(a) for a in args))
        
        namespace['print'] = safe_print
        
        try:
            exec(code, namespace)
            return {
                'success': True,
                'stdout': '\n'.join(stdout),
                'stderr': '',
                'returncode': 0,
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '\n'.join(stdout),
                'stderr': str(e),
                'returncode': 1,
            }
    
    def _safe_import(self, name, *args, **kwargs):
        """Restricted import that only allows safe modules."""
        allowed_modules = {
            'math', 'random', 'datetime', 'json', 're',
            'string', 'collections', 'itertools', 'functools',
            'statistics', 'fractions', 'decimal', 'typing',
        }
        
        if name.split('.')[0] not in allowed_modules:
            raise ImportError(f"Import of '{name}' is not allowed")
        
        return __import__(name, *args, **kwargs)


def create_sandbox(backend: str = "docker", config: SandboxConfig = None):
    """Factory function to create sandbox."""
    if backend == "docker":
        return DockerSandbox(config)
    elif backend == "firejail":
        return FirejailSandbox(config)
    elif backend == "restricted":
        return RestrictedPythonSandbox()
    else:
        raise ValueError(f"Unknown backend: {backend}")


if __name__ == "__main__":
    # Demo: Restricted Python
    sandbox = create_sandbox("restricted")
    
    code = """
import math
print("Hello from sandbox!")
print(f"Pi = {math.pi}")
for i in range(5):
    print(i)
"""
    
    result = sandbox.run(code)
    print("Restricted Python Result:")
    print(json.dumps(result, indent=2))
