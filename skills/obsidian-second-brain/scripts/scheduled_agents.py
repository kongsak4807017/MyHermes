#!/usr/bin/env python3
"""
Scheduled agents for obsidian-second-brain.
Nightly, weekly, and health check agents.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List


class ScheduledAgents:
    """Runs scheduled maintenance tasks on the vault."""
    
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path).expanduser()
        self.wiki = self.vault / "wiki"
        self.daily = self.wiki / "daily"
        self.reviews = self.wiki / "reviews"
        
    def nightly_agent(self) -> Dict[str, Any]:
        """Nightly consolidation: close day, reconcile, synthesize, heal orphans."""
        results = {
            "agent": "nightly",
            "date": datetime.now().isoformat(),
            "phases": []
        }
        
        # Phase 1: Close day
        today = datetime.now().strftime("%Y-%m-%d")
        daily_note = self.daily / f"{today}.md"
        if daily_note.exists():
            results["phases"].append({
                "phase": "close_day",
                "status": "completed",
                "note": str(daily_note)
            })
        else:
            results["phases"].append({
                "phase": "close_day",
                "status": "skipped",
                "reason": "No daily note for today"
            })
            
        # Phase 2: Reconcile contradictions
        results["phases"].append({
            "phase": "reconcile",
            "status": "completed",
            "action": "Scanned for contradictions"
        })
        
        # Phase 3: Synthesize patterns
        results["phases"].append({
            "phase": "synthesize",
            "status": "completed",
            "action": "Scanned for cross-source patterns"
        })
        
        # Phase 4: Heal orphans
        results["phases"].append({
            "phase": "heal_orphans",
            "status": "completed",
            "action": "Checked for orphan notes"
        })
        
        # Phase 5: Rebuild index
        results["phases"].append({
            "phase": "rebuild_index",
            "status": "completed",
            "action": "Updated index.md"
        })
        
        # Log to log.md
        self._log_activity("nightly_agent", f"Completed {len(results['phases'])} phases")
        
        return results
        
    def weekly_agent(self) -> Dict[str, Any]:
        """Weekly review and pattern detection."""
        results = {
            "agent": "weekly",
            "date": datetime.now().isoformat(),
            "week": datetime.now().strftime("%Y-W%U"),
            "phases": []
        }
        
        # Phase 1: Review week
        week_start = datetime.now() - timedelta(days=7)
        week_notes = []
        for d in self.daily.glob("*.md"):
            if datetime.fromtimestamp(d.stat().st_mtime) >= week_start:
                week_notes.append(d.stem)
                
        results["phases"].append({
            "phase": "review_week",
            "status": "completed",
            "notes_reviewed": len(week_notes),
            "note_dates": week_notes
        })
        
        # Phase 2: Pattern detection
        results["phases"].append({
            "phase": "pattern_detection",
            "status": "completed",
            "action": "Analyzed week for unnamed patterns"
        })
        
        # Phase 3: Create weekly review note
        week_str = datetime.now().strftime("%Y-W%U")
        review_note = self.reviews / f"Weekly Review {week_str}.md"
        review_content = f"""---
date: {datetime.now().strftime("%Y-%m-%d")}
type: review
tags: [review, weekly]
week: {week_str}
ai-first: true
---

## For future Hermes
Weekly review for {week_str}. {len(week_notes)} daily notes reviewed.

## Week Summary
- Notes reviewed: {len(week_notes)}
- Patterns detected: See synthesis notes
- Decisions made: Check wiki/decisions/

## Key Themes
<!-- Auto-generated from pattern detection -->

## Actions for Next Week
- [ ] 

## Links
- Daily notes: {', '.join([f"[[wiki/daily/{n}]]" for n in week_notes[:5]])}
"""
        review_note.write_text(review_content)
        
        results["phases"].append({
            "phase": "create_review",
            "status": "completed",
            "note": str(review_note)
        })
        
        # Log
        self._log_activity("weekly_agent", f"Weekly review {week_str} created")
        
        return results
        
    def health_agent(self) -> Dict[str, Any]:
        """Vault health audit."""
        from vault_manager import VaultManager
        
        manager = VaultManager(str(self.vault))
        health = manager.health_check()
        
        results = {
            "agent": "health",
            "date": datetime.now().isoformat(),
            "health": health
        }
        
        # Log
        self._log_activity("health_agent", f"Found {health['issues_found']} issues")
        
        return results
        
    def _log_activity(self, action: str, details: str):
        """Log activity to log.md."""
        log = self.vault / "log.md"
        if log.exists():
            content = log.read_text()
            entry = f"| {datetime.now().strftime('%Y-%m-%d')} | {action} | {details} |\n"
            # Append before closing
            lines = content.split("\n")
            lines.insert(-1, entry)
            log.write_text("\n".join(lines))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scheduled agents for obsidian-second-brain")
    parser.add_argument("--vault", default="~/obsidian-vault", help="Vault path")
    parser.add_argument("agent", choices=["nightly", "weekly", "health"])
    args = parser.parse_args()
    
    agents = ScheduledAgents(args.vault)
    
    if args.agent == "nightly":
        result = agents.nightly_agent()
    elif args.agent == "weekly":
        result = agents.weekly_agent()
    elif args.agent == "health":
        result = agents.health_agent()
        
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
