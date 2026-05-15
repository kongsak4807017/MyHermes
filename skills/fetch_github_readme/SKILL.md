---
name: fetch_github_readme
description: Fetch and summarize a GitHub repository's README file when given a repo URL.
category: web
---

Steps:
1. Given a GitHub repo URL (e.g., https://github.com/user/repo), attempt to fetch the raw README.md via `https://raw.githubusercontent.com/user/repo/main/README.md` (or master branch if main fails).
2. Use `browser_navigate` to the raw URL; if timeout or error, fallback to `terminal` with `curl -s` to retrieve content.
3. If the raw fetch fails, try to navigate to the repo's GitHub page and use `browser_snapshot` to locate the README section, then extract text.
4. Once content is obtained, summarize key points: project purpose, installation, usage, core concepts, and any notable features.
5. Provide the summary in the requested language (default Thai if user asks).
6. Optionally, store the summary in memory for future reference.

Pitfalls:
- Some repos may have README in other formats (e.g., README.rst); adjust fetch accordingly.
- Branch may not be main; try both main and master.
- Rate limiting: curl may be blocked; use browser if possible.