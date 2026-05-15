---
title: Prompt Quality & Verification Patterns from OpenClaw
description: Implement completion bias and verification patterns for more reliable agent responses
---

# Prompt Quality Patterns (OpenClaw Style)

## Overview

OpenClaw 2026.4.20-beta.1 ปรับ:
- **Completion bias** ที่ชัดขึ้น
- **Live-state checking** ดีขึ้น
- **Weak result recovery** - ฟื้นตัวจากผลลัพธ์ที่ไม่ดี
- **Pre-response verification** - verify ก่อนตอบ

## Pattern 1: Verification Bias

```python
# agent/verification.py

from typing import Dict, Any, Optional
import json

class ResponseVerifier:
    """Verify responses before returning to user."""
    
    CHECKS = [
        "completeness",
        "accuracy", 
        "source_citation",
        "uncertainty_disclosure"
    ]
    
    def verify(self, response: str, context: Dict) -> Dict[str, Any]:
        """Run verification checks on response."""
        results = {}
        
        # Check 1: Completeness
        results["completeness"] = self._check_complete(response, context)
        
        # Check 2: Has uncertainty markers
        results["uncertainty"] = self._check_uncertainty(response)
        
        # Check 3: Sources cited (if factual claims)
        results["sources"] = self._check_sources(response)
        
        # Overall score
        passed = sum(1 for r in results.values() if r.get("pass", False))
        results["score"] = passed / len(self.CHECKS)
        results["should_retry"] = results["score"] < 0.5
        
        return results
    
    def _check_complete(self, response: str, context: Dict) -> Dict:
        """Check if response addresses all parts of the query."""
        # Simple heuristic: check for question words in context
        # that don't have answers in response
        query = context.get("query", "")
        
        # If multiple questions (what, how, why), ensure all addressed
        questions = query.count("?")
        addressed = response.count("?")  # Rough proxy
        
        return {
            "pass": questions <= addressed + 1,  # Allow some mismatch
            "questions_found": questions,
            "answers_found": addressed
        }
    
    def _check_uncertainty(self, response: str) -> Dict:
        """Check for appropriate uncertainty markers."""
        uncertainty_markers = [
            "may", "might", "could", "possibly",
            "likely", "probably", "uncertain",
            "based on", "appears to"
        ]
        
        has_markers = any(m in response.lower() for m in uncertainty_markers)
        makes_strong_claims = any(
            phrase in response.lower()
            for phrase in ["definitely", "certainly", "absolutely", "100%"]
        )
        
        return {
            "pass": has_markers or not makes_strong_claims,
            "has_uncertainty": has_markers,
            "strong_claims": makes_strong_claims
        }
    
    def _check_sources(self, response: str) -> Dict:
        """Check if factual claims have sources."""
        # Look for citation patterns
        has_citations = any(
            pattern in response
            for pattern in ["[", "(", "source", "according to", "from"]
        )
        
        # Simple heuristic: long factual responses should cite
        is_factual = len(response) > 500 and not response.startswith("```")
        
        return {
            "pass": has_citations or not is_factual,
            "has_citations": has_citations,
            "is_factual": is_factual
        }


# Integration with agent loop
def generate_with_verification(agent, query: str, max_attempts: int = 2) -> str:
    """Generate response with OpenClaw-style verification."""
    verifier = ResponseVerifier()
    
    for attempt in range(max_attempts):
        response = agent.generate(query)
        
        verification = verifier.verify(response, {"query": query})
        
        if verification["score"] >= 0.7:
            return response
        
        if attempt < max_attempts - 1:
            # Retry with feedback
            query = f"{query}\n\n[Previous response had issues: {verification}. Please improve.]"
    
    # Return last attempt even if imperfect
    return response
```

## Pattern 2: Live-State Checking

```python
# agent/live_state.py

import sqlite3
from datetime import datetime
from pathlib import Path

class LiveStateChecker:
    """Check current system state before responding."""
    
    def __init__(self, hermes_home: Path):
        self.hermes_home = hermes_home
        self.db_path = hermes_home / "state.db"
    
    def get_state(self) -> Dict:
        """Get current operational state."""
        return {
            "recent_errors": self._get_recent_errors(),
            "active_sessions": self._get_active_sessions(),
            "cron_status": self._get_cron_health(),
            "disk_usage": self._get_disk_usage()
        }
    
    def _get_recent_errors(self, hours: int = 1) -> List[Dict]:
        """Get errors from last N hours."""
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Assuming error log table exists
        try:
            cursor.execute("""
                SELECT timestamp, error_type, message 
                FROM errors 
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
                LIMIT 5
            """.format(hours))
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
        finally:
            conn.close()
    
    def should_add_context_warning(self) -> Optional[str]:
        """Check if we should warn about system state."""
        state = self.get_state()
        
        warnings = []
        
        if len(state["recent_errors"]) > 5:
            warnings.append(f"Note: {len(state['recent_errors'])} recent errors detected")
        
        if state["disk_usage"] > 90:
            warnings.append(f"Warning: Disk usage at {state['disk_usage']}%")
        
        return " | ".join(warnings) if warnings else None
```

## Pattern 3: System Prompt Updates

```python
# agent/prompt_builder.py updates

VERIFICATION_INSTRUCTIONS = """
Before finalizing your response:
1. VERIFY you have addressed ALL parts of the user's query
2. CHECK for unsupported claims - mark uncertainty appropriately  
3. CITE sources for factual statements
4. CONFIRM tool results match expected outcomes

If uncertain, say so explicitly rather than guessing.
"""

LIVE_STATE_AWARENESS = """
Current system state (for awareness):
- Active sessions: {active_sessions}
- Recent errors: {error_count}
- Disk usage: {disk_percent}%

Consider operational constraints when planning multi-step operations.
"""
```

## Key Takeaways

1. **Verify before finalize** - Don't just trust first generation
2. **State awareness** - Agent รู้ตัวว่าระบบเป็นอย่างไร
3. **Uncertainty markers** - บอกเมื่อไม่แน่ใจ
4. **Retry with feedback** - แก้ไขอัตโนมัติถ้าผลไม่ดี

## Reference

- OpenClaw: v2026.4.20-beta.1 prompt improvements
- File: `~/.hermes/skills/openclaw-learnings/references/prompt-patterns.md`
