#!/usr/bin/env python3
"""
Vault manager for obsidian-second-brain.
Handles initialization, health checks, synthesis, and reconciliation.
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class VaultManager:
    """Manages an obsidian-second-brain vault."""
    
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path).expanduser()
        self.wiki = self.vault / "wiki"
        self.daily = self.wiki / "daily"
        self.entities = self.wiki / "entities"
        self.concepts = self.wiki / "concepts"
        self.projects = self.wiki / "projects"
        self.tasks = self.wiki / "tasks"
        self.decisions = self.wiki / "decisions"
        self.logs = self.wiki / "logs"
        self.reviews = self.wiki / "reviews"
        self.boards = self.vault / "boards"
        self.raw = self.vault / "raw"
        self.research = self.vault / "Research"
        
    def init_vault(self) -> Dict[str, Any]:
        """Initialize a new vault with required structure."""
        dirs = [
            self.raw / "urls", self.raw / "pdfs", self.raw / "audio", self.raw / "images",
            self.entities, self.concepts, self.projects, self.daily,
            self.logs, self.reviews, self.tasks, self.decisions,
            self.boards, self.boards / "projects",
            self.vault / "templates",
            self.research / "Web", self.research / "X",
            self.research / "YouTube", self.research / "NotebookLM",
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            
        files_created = []
        
        # _HERMES.md
        hermes_md = self.vault / "_HERMES.md"
        if not hermes_md.exists():
            hermes_md.write_text(self._hermes_template())
            files_created.append("_HERMES.md")
            
        # index.md
        index_md = self.vault / "index.md"
        if not index_md.exists():
            index_md.write_text(self._index_template())
            files_created.append("index.md")
            
        # log.md
        log_md = self.vault / "log.md"
        if not log_md.exists():
            log_md.write_text(self._log_template())
            files_created.append("log.md")
            
        # SOUL.md
        soul_md = self.vault / "SOUL.md"
        if not soul_md.exists():
            soul_md.write_text(self._soul_template())
            files_created.append("SOUL.md")
            
        # CRITICAL_FACTS.md
        cf_md = self.vault / "CRITICAL_FACTS.md"
        if not cf_md.exists():
            cf_md.write_text(self._critical_facts_template())
            files_created.append("CRITICAL_FACTS.md")
            
        # PINNED.md
        pinned_md = self.vault / "PINNED.md"
        if not pinned_md.exists():
            pinned_md.write_text("---\ndate: {}\ntype: pinned\ntags: [pinned]\nai-first: true\n---\n\n## For future Hermes\nSession-specific pinned context. Cleared when task done.\n".format(datetime.now().strftime("%Y-%m-%d")))
            files_created.append("PINNED.md")
            
        return {
            "vault_path": str(self.vault),
            "directories_created": len(dirs),
            "files_created": files_created,
            "status": "initialized"
        }
        
    def health_check(self) -> Dict[str, Any]:
        """Run vault health audit."""
        issues = {
            "critical": [],
            "warnings": [],
            "info": []
        }
        
        # Check for contradictions
        contradictions = self._find_contradictions()
        issues["critical"].extend(contradictions)
        
        # Check for stale claims (older than 90 days)
        stale = self._find_stale_claims(days=90)
        issues["warnings"].extend(stale)
        
        # Check for orphan notes
        orphans = self._find_orphans()
        issues["info"].extend(orphans)
        
        # Check for broken links
        broken = self._find_broken_links()
        issues["warnings"].extend(broken)
        
        # Check for missing frontmatter
        missing_fm = self._find_missing_frontmatter()
        issues["warnings"].extend(missing_fm)
        
        return {
            "vault_path": str(self.vault),
            "issues_found": len(issues["critical"]) + len(issues["warnings"]) + len(issues["info"]),
            "critical": issues["critical"],
            "warnings": issues["warnings"],
            "info": issues["info"],
            "status": "completed"
        }
        
    def synthesize(self, days: int = 30) -> Dict[str, Any]:
        """Find patterns across recent notes and create synthesis pages."""
        patterns = []
        cutoff = datetime.now() - timedelta(days=days)
        
        # Scan recent notes
        recent_notes = []
        for path in self.wiki.rglob("*.md"):
            if path.stat().st_mtime > cutoff.timestamp():
                recent_notes.append(path)
                
        # Simple pattern detection: count word frequency
        word_counts = {}
        for note in recent_notes:
            content = note.read_text().lower()
            words = re.findall(r'\b[a-z]{4,}\b', content)
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
                
        # Find words that appear frequently across different notes
        common_words = {w: c for w, c in word_counts.items() 
                       if c >= 3 and len(recent_notes) >= 2}
        
        for word, count in sorted(common_words.items(), key=lambda x: -x[1])[:10]:
            patterns.append({
                "pattern": word,
                "mentions": count,
                "notes": len(recent_notes)
            })
            
        return {
            "patterns_found": len(patterns),
            "patterns": patterns,
            "notes_scanned": len(recent_notes),
            "status": "completed"
        }
        
    def reconcile(self) -> Dict[str, Any]:
        """Find and resolve contradictions."""
        contradictions = self._find_contradictions()
        resolved = []
        
        for contradiction in contradictions:
            # Mark as needing manual review
            resolved.append({
                "type": contradiction["type"],
                "notes": contradiction["notes"],
                "resolution": "manual_review_required",
                "suggestion": contradiction.get("suggestion", "")
            })
            
        return {
            "contradictions_found": len(contradictions),
            "resolved": resolved,
            "status": "completed"
        }
        
    def _find_contradictions(self) -> List[Dict]:
        """Find contradictions across notes."""
        contradictions = []
        
        # Check person notes for role conflicts
        person_notes = list(self.entities.glob("*.md"))
        person_roles = {}
        
        for note in person_notes:
            content = note.read_text()
            name = note.stem
            role_match = re.search(r'role:\s*"?([^"\n]+)"?', content)
            if role_match:
                role = role_match.group(1).strip()
                if name in person_roles and person_roles[name] != role:
                    contradictions.append({
                        "type": "entity_conflict",
                        "entity": name,
                        "notes": [str(note) for note in person_notes if name in str(note)],
                        "suggestion": f"Person '{name}' has conflicting roles"
                    })
                person_roles[name] = role
                
        return contradictions
        
    def _find_stale_claims(self, days: int = 90) -> List[Dict]:
        """Find claims older than threshold."""
        stale = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for path in self.wiki.rglob("*.md"):
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if mtime < cutoff:
                stale.append({
                    "note": str(path.relative_to(self.vault)),
                    "last_modified": mtime.strftime("%Y-%m-%d"),
                    "suggestion": "Review for outdated information"
                })
                
        return stale[:20]  # Limit to first 20
        
    def _find_orphans(self) -> List[Dict]:
        """Find notes with no incoming links."""
        orphans = []
        all_notes = list(self.wiki.rglob("*.md"))
        all_content = ""
        
        for note in all_notes:
            all_content += note.read_text()
            
        for note in all_notes:
            note_name = note.stem
            if f"[[{note_name}" not in all_content and note_name not in ["index", "log"]:
                orphans.append({
                    "note": str(note.relative_to(self.vault)),
                    "suggestion": "Add links from other notes or review if still needed"
                })
                
        return orphans[:20]
        
    def _find_broken_links(self) -> List[Dict]:
        """Find wikilinks pointing to non-existent notes."""
        broken = []
        all_notes = {n.stem for n in self.wiki.rglob("*.md")}
        
        for note in self.wiki.rglob("*.md"):
            content = note.read_text()
            links = re.findall(r'\[\[([^\]|]+)', content)
            for link in links:
                link_name = link.split("/")[-1].strip()
                if link_name not in all_notes and link_name not in ["", " "]:
                    broken.append({
                        "source": str(note.relative_to(self.vault)),
                        "broken_link": link,
                        "suggestion": f"Create note '{link_name}' or fix link"
                    })
                    
        return broken[:20]
        
    def _find_missing_frontmatter(self) -> List[Dict]:
        """Find notes without proper frontmatter."""
        missing = []
        
        for note in self.wiki.rglob("*.md"):
            content = note.read_text()
            if not content.startswith("---"):
                missing.append({
                    "note": str(note.relative_to(self.vault)),
                    "suggestion": "Add YAML frontmatter with type, date, tags, ai-first"
                })
                
        return missing[:20]
        
    def _hermes_template(self) -> str:
        return """---
date: {date}
type: meta
tags: [meta, hermes]
ai-first: true
---

## For future Hermes
Operating manual for this vault. Read this FIRST before any operation.

## Commands
- /hermes-save — Save conversation to vault
- /hermes-world — Load identity + state
- /hermes-ingest — Ingest external source
- /hermes-synthesize — Find patterns across notes
- /hermes-reconcile — Resolve contradictions
- /hermes-daily — Create/update daily note
- /hermes-health — Vault audit
- /hermes-challenge — Vault argues against idea
- /hermes-emerge — Surface unnamed patterns

## Structure
- wiki/entities/ — People, companies, tools
- wiki/concepts/ — Ideas, frameworks, synthesis
- wiki/projects/ — Active work
- wiki/daily/ — Daily notes
- wiki/logs/ — Work sessions
- wiki/reviews/ — Weekly/monthly
- wiki/tasks/ — Task notes
- wiki/decisions/ — ADRs
- boards/ — Kanban boards
- Research/ — Research outputs

## AI-First Rules
1. Self-contained notes
2. "For future Hermes" preamble
3. Rich frontmatter (type, date, tags, ai-first: true)
4. Recency markers per claim (as of YYYY-MM, source.com)
5. Sources preserved verbatim
6. Mandatory [[wikilinks]]
7. Confidence levels (stated/high/medium/speculation)
""".format(date=datetime.now().strftime("%Y-%m-%d"))
        
    def _index_template(self) -> str:
        return """---
date: {date}
type: meta
tags: [meta, index]
ai-first: true
---

## For future Hermes
Catalog of all vault pages. Read this to know what exists.

## Entities
<!-- Auto-generated from wiki/entities/ -->

## Concepts
<!-- Auto-generated from wiki/concepts/ -->

## Projects
<!-- Auto-generated from wiki/projects/ -->

## Daily Notes
<!-- Auto-generated from wiki/daily/ -->

## Recent Activity
<!-- Last 10 entries from log.md -->
""".format(date=datetime.now().strftime("%Y-%m-%d"))
        
    def _log_template(self) -> str:
        return """---
date: {date}
type: meta
tags: [meta, log]
ai-first: true
---

## For future Hermes
Activity timeline. Last 10 entries loaded at L1.

## Entries
| Date | Action | Notes |
|------|--------|-------|
| {date} | Vault initialized | - |
""".format(date=datetime.now().strftime("%Y-%m-%d"))
        
    def _soul_template(self) -> str:
        return """---
date: {date}
type: meta
tags: [meta, soul]
ai-first: true
---

## For future Hermes
Identity file. Who the user is, communication style, thinking preferences.

## Who I Am
- Name:
- Role:
- Company:
- Location:
- Timezone:

## Communication Style
- Preferred tone:
- Detail level:
- Decision style:

## Thinking Preferences
- Analytical vs intuitive:
- Risk tolerance:
- Innovation vs stability:

## Core Values
1.
2.
3.

## Non-negotiables
-

## Goals
- Short term:
- Long term:
""".format(date=datetime.now().strftime("%Y-%m-%d"))
        
    def _critical_facts_template(self) -> str:
        return """---
date: {date}
type: meta
tags: [meta, critical-facts]
ai-first: true
---

## For future Hermes
~120 tokens of always-needed context. Loaded at L0 every session.

## Facts
- Timezone:
- Manager/Team:
- Location:
- Company:
- Role:
- Key preferences:
""".format(date=datetime.now().strftime("%Y-%m-%d"))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Vault manager for obsidian-second-brain")
    parser.add_argument("--vault", default="~/obsidian-vault", help="Vault path")
    parser.add_argument("command", choices=["init", "health", "synthesize", "reconcile"])
    args = parser.parse_args()
    
    manager = VaultManager(args.vault)
    
    if args.command == "init":
        result = manager.init_vault()
    elif args.command == "health":
        result = manager.health_check()
    elif args.command == "synthesize":
        result = manager.synthesize()
    elif args.command == "reconcile":
        result = manager.reconcile()
        
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
