#!/usr/bin/env python3
"""
ARIS Research Wiki - Helper utilities for Hermes.

Adapted for Hermes Agent environment:
- Uses ~/.hermes/aris-wiki/ as default wiki root
- Integrates with skill_view for cross-skill queries
- Supports Thai/English/Chinese output
"""
from __future__ import annotations

import os
import sys
import json
import re
import hashlib
import argparse
import textwrap
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# HERMES DEFAULTS
DEFAULT_WIKI_ROOT = os.path.expanduser("~/.hermes/aris-wiki")
HUMAN_LANGUAGES = ["th", "en", "zh"]

_ARXIV_API = "http://export.arxiv.org/api/query?id_list={ids}"
_ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom",
             "arxiv": "http://arxiv.org/schemas/atom"}


def _slugify(title: str) -> str:
    """Create filesystem-safe slug from paper title."""
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip("-")[:80]


def _paper_path(wiki_root: Path, slug: str) -> Path:
    """Return path to paper markdown file."""
    return wiki_root / "papers" / f"{slug}.md"


def _edge_path(wiki_root: Path) -> Path:
    """Return path to edges JSON file."""
    return wiki_root / "relationships" / "edges.json"


def _index_path(wiki_root: Path) -> Path:
    """Return path to index JSON file."""
    return wiki_root / "index.json"


def _query_pack_path(wiki_root: Path) -> Path:
    """Return path to query pack file."""
    return wiki_root / "query-pack.md"


def _log_path(wiki_root: Path) -> Path:
    """Return path to log file."""
    return wiki_root / "logs" / "activity.log"


def _ensure_dirs(wiki_root: Path) -> None:
    """Ensure all wiki directories exist."""
    for subdir in ["papers", "ideas", "experiments", "claims", "relationships", "styles", "logs"]:
        (wiki_root / subdir).mkdir(parents=True, exist_ok=True)


def _fetch_arxiv_metadata(arxiv_ids: list[str]) -> list[dict]:
    """Fetch metadata from arXiv API."""
    if not arxiv_ids:
        return []
    ids_str = ",".join(arxiv_ids)
    url = _ARXIV_API.format(ids=ids_str)
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
    except Exception as e:
        print(f"ERROR: Failed to fetch arXiv metadata: {e}", file=sys.stderr)
        return []

    root = ET.fromstring(data)
    papers = []
    for entry in root.findall("atom:entry", _ARXIV_NS):
        paper = {
            "title": _text(entry, "atom:title"),
            "authors": [a.text for a in entry.findall("atom:author/atom:name", _ARXIV_NS)],
            "summary": _text(entry, "atom:summary"),
            "published": _text(entry, "atom:published"),
            "updated": _text(entry, "atom:updated"),
            "arxiv_id": _text(entry, "atom:id").split("/")[-1],
            "pdf_url": None,
            "primary_category": None,
        }
        for link in entry.findall("atom:link", _ARXIV_NS):
            if link.get("title") == "pdf":
                paper["pdf_url"] = link.get("href")
            elif link.get("rel") == "alternate":
                paper["arxiv_url"] = link.get("href")
        cat = entry.find("arxiv:primary_category", _ARXIV_NS)
        if cat is not None:
            paper["primary_category"] = cat.get("term")
        papers.append(paper)
    return papers


def _text(elem, path: str) -> str:
    """Safely extract text from XML element."""
    e = elem.find(path, _ARXIV_NS)
    return (e.text or "").strip() if e is not None else ""


def _now() -> str:
    """Return ISO timestamp."""
    return datetime.now(timezone.utc).isoformat()


def cmd_init(wiki_root: Path) -> int:
    """Initialize wiki directory structure."""
    _ensure_dirs(wiki_root)
    index = wiki_root / "index.md"
    index.write_text(
        f"# ARIS Research Wiki\\n\\n"
        f"Initialized: {_now()}\\n\\n"
        f"## Sections\\n"
        f"- [Papers](papers/)\\n"
        f"- [Ideas](ideas/)\\n"
        f"- [Experiments](experiments/)\\n"
        f"- [Claims](claims/)\\n"
        f"- [Relationships](relationships/)\\n",
        encoding="utf-8"
    )
    print(f"Wiki initialized at: {wiki_root}")
    return 0


def cmd_slug(title: str, author: Optional[str] = None, year: Optional[int] = None) -> int:
    """Generate slug from paper metadata."""
    parts = [_slugify(title)]
    if author:
        parts.append(author.lower().replace(" ", "-"))
    if year:
        parts.append(str(year))
    print("-".join(parts))
    return 0


def cmd_ingest_paper(
    wiki_root: Path,
    arxiv_id: Optional[str] = None,
    title: Optional[str] = None,
    authors: Optional[str] = None,
    year: Optional[int] = None,
    venue: Optional[str] = None,
    external_id_doi: Optional[str] = None,
    thesis: Optional[str] = None,
    tags: Optional[str] = None,
    update_on_exist: bool = False,
) -> int:
    """Ingest a paper into the wiki."""
    _ensure_dirs(wiki_root)

    if arxiv_id:
        papers = _fetch_arxiv_metadata([arxiv_id])
        if not papers:
            print(f"ERROR: Could not fetch arXiv:{arxiv_id}", file=sys.stderr)
            return 1
        p = papers[0]
        title = p["title"]
        authors = ", ".join(p["authors"])
        year = int(p["published"][:4]) if p["published"] else datetime.now().year
        venue = p["primary_category"] or "arXiv"
        external_id_doi = p.get("arxiv_url", f"https://arxiv.org/abs/{arxiv_id}")
    elif not title:
        print("ERROR: Need --arxiv-id or --title", file=sys.stderr)
        return 1

    slug = _slugify(title)
    paper_file = _paper_path(wiki_root, slug)

    if paper_file.exists() and not update_on_exist:
        print(f"SKIP: {slug} already exists (use --update-on-exist)")
        return 0

    tag_list = [t.strip() for t in (tags or "").split(",") if t.strip()]

    content = f"""---
slug: {slug}
title: {title}
authors: {authors or "Unknown"}
year: {year or ""}
venue: {venue or ""}
doi: {external_id_doi or ""}
tags: {', '.join(tag_list)}
ingested: {_now()}
---

# {title}

**Authors:** {authors or "Unknown"}  
**Year:** {year or ""}  
**Venue:** {venue or ""}  
**DOI/URL:** {external_id_doi or ""}

## One-Line Thesis
{thesis or "(add thesis)"}

## Summary
(add summary)

## Key Claims
- (add claims)

## Related Work
- (add relationships)

## Experiments
- (link to experiments)
"""

    paper_file.write_text(content, encoding="utf-8")
    print(f"Ingested: {paper_file}")

    # Update index
    _rebuild_index(wiki_root)
    return 0


def cmd_add_edge(
    wiki_root: Path,
    from_slug: str,
    to_slug: str,
    edge_type: str,
    evidence: Optional[str] = None,
) -> int:
    """Add relationship edge between two papers."""
    _ensure_dirs(wiki_root)
    edge_file = _edge_path(wiki_root)

    edges = []
    if edge_file.exists():
        try:
            edges = json.loads(edge_file.read_text())
        except json.JSONDecodeError:
            pass

    edges.append({
        "from": from_slug,
        "to": to_slug,
        "type": edge_type,
        "evidence": evidence or "",
        "created": _now(),
    })

    edge_file.write_text(json.dumps(edges, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Edge added: {from_slug} --[{edge_type}]--> {to_slug}")
    return 0


def _rebuild_index(wiki_root: Path) -> None:
    """Rebuild wiki index from papers directory."""
    papers_dir = wiki_root / "papers"
    papers = []
    if papers_dir.exists():
        for f in sorted(papers_dir.iterdir()):
            if f.suffix == ".md":
                content = f.read_text(encoding="utf-8")
                # Extract frontmatter
                fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
                if fm_match:
                    papers.append({
                        "slug": f.stem,
                        "file": str(f.relative_to(wiki_root)),
                    })

    index_file = _index_path(wiki_root)
    index_file.write_text(json.dumps({
        "papers": papers,
        "updated": _now(),
    }, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_rebuild_index(wiki_root: Path) -> int:
    """Rebuild index."""
    _rebuild_index(wiki_root)
    print("Index rebuilt.")
    return 0


def cmd_rebuild_query_pack(wiki_root: Path, max_chars: int = 8000) -> int:
    """Build query pack for LLM context."""
    _ensure_dirs(wiki_root)
    papers_dir = wiki_root / "papers"
    chunks = ["# Research Wiki Query Pack\\n"]
    total = 0

    if papers_dir.exists():
        for f in sorted(papers_dir.iterdir()):
            if f.suffix == ".md":
                content = f.read_text(encoding="utf-8")
                # Skip frontmatter, take first 1000 chars of body
                body = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
                snippet = body[:1000].strip()
                piece = f"\\n## {f.stem}\\n{snippet}\\n"
                if total + len(piece) > max_chars:
                    break
                chunks.append(piece)
                total += len(piece)

    pack_file = _query_pack_path(wiki_root)
    pack_file.write_text("".join(chunks), encoding="utf-8")
    print(f"Query pack rebuilt: {pack_file} ({total} chars)")
    return 0


def cmd_stats(wiki_root: Path) -> int:
    """Show wiki statistics."""
    _ensure_dirs(wiki_root)
    stats = {}
    for subdir in ["papers", "ideas", "experiments", "claims", "relationships"]:
        d = wiki_root / subdir
        if d.exists():
            files = [f for f in d.iterdir() if f.is_file()]
            stats[subdir] = len(files)
        else:
            stats[subdir] = 0

    print(f"Wiki stats for {wiki_root}:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    return 0


def cmd_log(wiki_root: Path, message: str) -> int:
    """Append log entry."""
    _ensure_dirs(wiki_root)
    log_file = _log_path(wiki_root)
    entry = f"[{_now()}] {message}\\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"Logged: {message}")
    return 0


def cmd_sync(wiki_root: Path, arxiv_ids: Optional[str] = None, from_file: Optional[str] = None) -> int:
    """Batch sync papers from arXiv."""
    ids = []
    if arxiv_ids:
        ids = [i.strip() for i in arxiv_ids.split(",") if i.strip()]
    elif from_file:
        p = Path(from_file)
        if p.exists():
            ids = [line.strip() for line in p.read_text().splitlines() if line.strip()]

    if not ids:
        print("ERROR: No arXiv IDs provided", file=sys.stderr)
        return 1

    papers = _fetch_arxiv_metadata(ids)
    for p in papers:
        slug = _slugify(p["title"])
        paper_file = _paper_path(wiki_root, slug)
        if paper_file.exists():
            print(f"SKIP: {slug}")
            continue
        cmd_ingest_paper(
            wiki_root,
            arxiv_id=p["arxiv_id"],
            thesis="(batch sync)",
        )

    _rebuild_index(wiki_root)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ARIS Research Wiki for Hermes")
    parser.add_argument("command", choices=["init", "slug", "ingest_paper", "add_edge", "rebuild_index", "rebuild_query_pack", "stats", "log", "sync"])
    parser.add_argument("wiki_root", nargs="?", default=DEFAULT_WIKI_ROOT)
    parser.add_argument("--arxiv-id")
    parser.add_argument("--title")
    parser.add_argument("--authors")
    parser.add_argument("--year", type=int)
    parser.add_argument("--venue")
    parser.add_argument("--external-id-doi")
    parser.add_argument("--thesis")
    parser.add_argument("--tags")
    parser.add_argument("--update-on-exist", action="store_true")
    parser.add_argument("--from")
    parser.add_argument("--to")
    parser.add_argument("--type")
    parser.add_argument("--evidence")
    parser.add_argument("--max-chars", type=int, default=8000)
    parser.add_argument("--arxiv-ids")
    parser.add_argument("--from-file")
    parser.add_argument("--author")
    args = parser.parse_args()

    wiki_root = Path(args.wiki_root)

    if args.command == "init":
        return cmd_init(wiki_root)
    elif args.command == "slug":
        return cmd_slug(args.title or "", args.author, args.year)
    elif args.command == "ingest_paper":
        return cmd_ingest_paper(wiki_root, args.arxiv_id, args.title, args.authors, args.year, args.venue, args.external_id_doi, args.thesis, args.tags, args.update_on_exist)
    elif args.command == "add_edge":
        return cmd_add_edge(wiki_root, getattr(args, "from"), args.to, args.type, args.evidence)
    elif args.command == "rebuild_index":
        return cmd_rebuild_index(wiki_root)
    elif args.command == "rebuild_query_pack":
        return cmd_rebuild_query_pack(wiki_root, args.max_chars)
    elif args.command == "stats":
        return cmd_stats(wiki_root)
    elif args.command == "log":
        return cmd_log(wiki_root, " ".join(args.wiki_root))
    elif args.command == "sync":
        return cmd_sync(wiki_root, args.arxiv_ids, args.from_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
