#!/usr/bin/env python3
"""
Progressive context loader for obsidian-second-brain.
Loads L0-L3 context levels to avoid token burn.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class ContextLoader:
    """Loads vault context progressively (L0-L3)."""
    
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path).expanduser()
        
    def load_l0_identity(self) -> Dict[str, Any]:
        """L0: Identity (~170 tokens)."""
        context = {
            "level": "L0",
            "files_loaded": [],
            "identity": {},
            "tokens_estimate": 0
        }
        
        # SOUL.md
        soul = self.vault / "SOUL.md"
        if soul.exists():
            content = soul.read_text()
            context["identity"]["soul"] = self._extract_frontmatter(content)
            context["files_loaded"].append("SOUL.md")
            context["tokens_estimate"] += len(content.split())
            
        # CRITICAL_FACTS.md
        cf = self.vault / "CRITICAL_FACTS.md"
        if cf.exists():
            content = cf.read_text()
            context["identity"]["critical_facts"] = self._extract_frontmatter(content)
            context["files_loaded"].append("CRITICAL_FACTS.md")
            context["tokens_estimate"] += len(content.split())
            
        # PINNED.md
        pinned = self.vault / "PINNED.md"
        if pinned.exists():
            content = pinned.read_text()
            if len(content) > 100:  # Only if has content
                context["identity"]["pinned"] = content
                context["files_loaded"].append("PINNED.md")
                context["tokens_estimate"] += len(content.split())
                
        return context
        
    def load_l1_navigation(self) -> Dict[str, Any]:
        """L1: Navigation (~1-2K tokens)."""
        context = {
            "level": "L1",
            "files_loaded": [],
            "navigation": {},
            "tokens_estimate": 0
        }
        
        # index.md
        index = self.vault / "index.md"
        if index.exists():
            content = index.read_text()
            context["navigation"]["index"] = content[:2000]  # First 2K chars
            context["files_loaded"].append("index.md")
            context["tokens_estimate"] += len(content.split())
            
        # log.md (last 10 entries)
        log = self.vault / "log.md"
        if log.exists():
            content = log.read_text()
            lines = content.split("\n")
            # Find last 10 table rows
            table_rows = [l for l in lines if l.startswith("|") and "Date" not in l]
            recent = table_rows[-10:] if len(table_rows) > 10 else table_rows
            context["navigation"]["recent_activity"] = "\n".join(recent)
            context["files_loaded"].append("log.md")
            context["tokens_estimate"] += len(recent) * 10
            
        return context
        
    def load_l2_current_state(self) -> Dict[str, Any]:
        """L2: Current State (~2-5K tokens)."""
        context = {
            "level": "L2",
            "files_loaded": [],
            "state": {},
            "tokens_estimate": 0
        }
        
        # Dashboard/Home
        for name in ["Dashboard.md", "Home.md"]:
            dash = self.vault / name
            if dash.exists():
                content = dash.read_text()
                context["state"]["dashboard"] = content[:3000]
                context["files_loaded"].append(name)
                context["tokens_estimate"] += len(content.split())
                break
                
        # Today's daily note
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        daily = self.vault / "wiki" / "daily" / f"{today}.md"
        if daily.exists():
            content = daily.read_text()
            context["state"]["today"] = content[:2000]
            context["files_loaded"].append(f"wiki/daily/{today}.md")
            context["tokens_estimate"] += len(content.split())
            
        # Last 3 daily notes
        daily_dir = self.vault / "wiki" / "daily"
        if daily_dir.exists():
            dailies = sorted(daily_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
            recent = []
            for d in dailies[:3]:
                content = d.read_text()
                recent.append({
                    "date": d.stem,
                    "preview": content[:500]
                })
            context["state"]["recent_dailies"] = recent
            
        # Active boards
        boards_dir = self.vault / "boards"
        if boards_dir.exists():
            boards = []
            for b in boards_dir.glob("*.md"):
                content = b.read_text()
                if "in-progress" in content.lower() or "active" in content.lower():
                    boards.append({
                        "name": b.stem,
                        "preview": content[:1000]
                    })
            context["state"]["active_boards"] = boards
            
        return context
        
    def load_l3_deep_context(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """L3: Deep Context (~5-20K tokens, on demand)."""
        context = {
            "level": "L3",
            "files_loaded": [],
            "deep": {},
            "tokens_estimate": 0
        }
        
        # Active projects
        projects_dir = self.vault / "wiki" / "projects"
        if projects_dir.exists():
            active_projects = []
            for p in projects_dir.glob("*.md"):
                content = p.read_text()
                if "status: active" in content.lower():
                    active_projects.append({
                        "name": p.stem,
                        "content": content[:3000]
                    })
                    context["tokens_estimate"] += len(content.split())
            context["deep"]["active_projects"] = active_projects[:5]
            
        # Topic-specific research
        if topic:
            research_dir = self.vault / "Research"
            if research_dir.exists():
                matches = []
                for r in research_dir.rglob("*.md"):
                    content = r.read_text()
                    if topic.lower() in content.lower():
                        matches.append({
                            "path": str(r.relative_to(self.vault)),
                            "preview": content[:1500]
                        })
                context["deep"]["research_matches"] = matches[:5]
                
        return context
        
    def load_full(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Load all levels L0-L3."""
        return {
            "L0": self.load_l0_identity(),
            "L1": self.load_l1_navigation(),
            "L2": self.load_l2_current_state(),
            "L3": self.load_l3_deep_context(topic),
            "total_tokens_estimate": (
                self.load_l0_identity()["tokens_estimate"] +
                self.load_l1_navigation()["tokens_estimate"] +
                self.load_l2_current_state()["tokens_estimate"] +
                self.load_l3_deep_context(topic)["tokens_estimate"]
            )
        }
        
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown."""
        if not content.startswith("---"):
            return {}
            
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}
            
        fm = parts[1].strip()
        result = {}
        for line in fm.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip().strip('"').strip("'")
                
        return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Progressive context loader")
    parser.add_argument("--vault", default="~/obsidian-vault", help="Vault path")
    parser.add_argument("--level", choices=["L0", "L1", "L2", "L3", "all"], default="all")
    parser.add_argument("--topic", help="Topic for L3 deep context")
    args = parser.parse_args()
    
    loader = ContextLoader(args.vault)
    
    if args.level == "L0":
        result = loader.load_l0_identity()
    elif args.level == "L1":
        result = loader.load_l1_navigation()
    elif args.level == "L2":
        result = loader.load_l2_current_state()
    elif args.level == "L3":
        result = loader.load_l3_deep_context(args.topic)
    else:
        result = loader.load_full(args.topic)
        
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
