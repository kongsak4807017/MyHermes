---
title: OpenClaw Session Management Patterns
description: Apply OpenClaw's session stability patterns to Hermes Agent
---

# OpenClaw Session Patterns for Hermes

## Overview

OpenClaw 2026.4.20-beta.1 แนะนำ patterns สำคัญสำหรับ session stability:

1. **Built-in entry cap** - จำกัดจำนวน entries ใน session
2. **Age-based pruning** - ลบ session เก่าอัตโนมัติ
3. **Store size limits** - ป้องกัน OOM จาก backlog
4. **Context compaction notices** - แจ้งเตือนเมื่อ compress context

## Implementation for Hermes

```python
# hermes_cli/session_manager.py

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

def prune_old_sessions(max_age_days: int = 30, max_entries: int = 1000):
    """OpenClaw-style session pruning.
    
    Run this on startup and periodically via cron.
    """
    hermes_home = Path.home() / ".hermes"
    db_path = hermes_home / "state.db"
    
    if not db_path.exists():
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Age-based prune
    cutoff = (datetime.now() - timedelta(days=max_age_days)).isoformat()
    cursor.execute(
        "DELETE FROM sessions WHERE started_at < ?",
        (cutoff,)
    )
    age_pruned = cursor.rowcount
    
    # Entry cap enforce - keep only most recent N
    cursor.execute("""
        DELETE FROM sessions 
        WHERE id NOT IN (
            SELECT id FROM sessions 
            ORDER BY started_at DESC 
            LIMIT ?
        )
    """, (max_entries,))
    cap_pruned = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return {
        "age_pruned": age_pruned,
        "cap_pruned": cap_pruned,
        "kept": max_entries - cap_pruned
    }
```

## Usage

```python
# In Hermes startup
from hermes_cli.session_manager import prune_old_sessions

# Auto-prune on load if store > threshold
result = prune_old_sessions(max_age_days=30, max_entries=500)
if result["age_pruned"] > 0 or result["cap_pruned"] > 0:
    logger.info(f"Pruned sessions: {result}")
```

## Key Takeaways

- ใช้ **FIFO + age hybrid** - กันทั้งไฟล์ใหญ่และ session เก่า
- **แจ้งเตือน user** เมื่อ context ถูก compacted
- **Separate state files** - cron jobs-state.json แยกจาก jobs.json

## References

- OpenClaw Release: v2026.4.20-beta.1
- File: `~/.hermes/skills/openclaw-learnings/SKILL.md`
- Implement: `hermes_cli/session_manager.py`
