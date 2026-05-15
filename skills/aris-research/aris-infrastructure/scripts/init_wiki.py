#!/usr/bin/env python3
"""Initialize ARIS Research Wiki for Hermes"""
import os, pathlib, sys

wiki_root = pathlib.Path(os.path.expanduser("~/.hermes/aris-wiki"))
wiki_root.mkdir(parents=True, exist_ok=True)

# Create standard directories
for subdir in ["papers", "ideas", "experiments", "claims", "relationships", "styles", "logs"]:
    (wiki_root / subdir).mkdir(exist_ok=True)

# Create index file
index = wiki_root / "index.md"
index.write_text(f"""# ARIS Research Wiki

Initialized: {__import__('datetime').datetime.now().isoformat()}

## Sections
- [Papers](papers/)
- [Ideas](ideas/)
- [Experiments](experiments/)
- [Claims](claims/)
- [Relationships](relationships/)

## Usage
```
python3 ~/.hermes/skills/aris-research/aris-infrastructure/scripts/research_wiki.py init {wiki_root}
```
""", encoding="utf-8")

print(f"Wiki initialized at: {wiki_root}")
print(f"  Papers:      {wiki_root / 'papers'}")
print(f"  Ideas:       {wiki_root / 'ideas'}")
print(f"  Experiments: {wiki_root / 'experiments'}")
print(f"  Claims:      {wiki_root / 'claims'}")
print(f"  Styles:      {wiki_root / 'styles'}")
