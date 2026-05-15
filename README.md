# MyHermes

Personal Hermes Agent skills collection — curated, organized, and ready to use across machines.

## Stats

- **Total Skills**: 148
- **Categories**: 44
- **Total Size**: ~18 MB
- **Total Files**: 843

## Directory Structure

```
skills/
├── aris-research/          # 14 skills — Full research pipeline
├── creative/               # 19 skills — Image, video, music, ASCII, infographics
├── mlops/                  # 22 skills — Training, inference, models, eval, cloud
├── software-development/   # 12 skills — TDD, debug, plan, review
├── github/                 # 7 skills — PR, review, issues, repos
├── productivity/           # 10 skills — Google, Notion, Airtable, PowerPoint
├── vercel-labs/            # 10 skills — Vercel AI SDK, Next.js, Edge, v0
├── research/               # 5 skills — arXiv, blogs, wiki, Polymarket
├── devops/                 # 6 skills — Kanban, SearXNG, webhooks
├── paperbanana/            # 4 skills — Academic figure generation
├── autonomous-ai-agents/   # 4 skills — Claude Code, Codex, OpenCode
├── media/                  # 5 skills — GIFs, Spotify, YouTube, audio
├── apple/                  # 5 skills — Notes, Reminders, FindMy, iMessage
├── ...and more
```

## Quick Start

### Clone to new machine

```bash
git clone https://github.com/kongsak4807017/MyHermes.git
cd MyHermes
```

### Install to Hermes

```bash
# Copy skills to Hermes directory
cp -r skills/* ~/.hermes/skills/

# Or symlink (recommended for development)
ln -s $(pwd)/skills/* ~/.hermes/skills/
```

### Verify installation

```bash
# List all skills
ls ~/.hermes/skills/

# Count skills
find ~/.hermes/skills/ -name "SKILL.md" | wc -l
```

## Categories

### Research & Academic (23 skills)
| Skill | Description |
|-------|-------------|
| aris-research/* | Full ARIS research pipeline: idea discovery, paper writing, experiments, review, rebuttal, grants, patents |
| research/* | arXiv search, blog monitoring, LLM wiki, Polymarket, paper writing |
| paperbanana/* | Academic figure generation: diagrams, plots, evaluation |

### Creative & Media (24 skills)
| Skill | Description |
|-------|-------------|
| creative/* | Image/video/music generation, ASCII art, infographics, pixel art, Manim, p5js |
| media/* | GIF search, Spotify, YouTube, audio analysis, song generation |

### MLOps & AI (22 skills)
| Skill | Description |
|-------|-------------|
| mlops/training/* | Axolotl, TRL, Unsloth, PEFT, PyTorch FSDP |
| mlops/inference/* | vLLM, llama.cpp, GGUF, Guidance, Outlines |
| mlops/models/* | Stable Diffusion, CLIP, SAM, Whisper, AudioCraft |
| mlops/evaluation/* | lm-eval-harness, Weights & Biases |
| mlops/cloud/* | Modal serverless GPU |

### Software Development (23 skills)
| Skill | Description |
|-------|-------------|
| software-development/* | TDD, debugging, planning, code review, skill authoring |
| github/* | PR workflow, code review, issues, repo management |
| autonomous-ai-agents/* | Claude Code, Codex, OpenCode, Hermes Agent config |

### Productivity & Tools (15 skills)
| Skill | Description |
|-------|-------------|
| productivity/* | Google Workspace, Notion, Airtable, PowerPoint, PDF editing |
| apple/* | Notes, Reminders, FindMy, iMessage, macOS control |

### DevOps & Infrastructure (8 skills)
| Skill | Description |
|-------|-------------|
| devops/* | Kanban, SearXNG, webhooks, OMK CLI |
| mcp/* | Native MCP client, mcporter CLI |

### Social & Communication (4 skills)
| Skill | Description |
|-------|-------------|
| social-media/* | X/Twitter |
| email/* | Himalaya CLI |
| yuanbao/* | Yuanbao groups |

### Other (18 skills)
| Skill | Description |
|-------|-------------|
| vercel-labs/* | Vercel AI SDK, Next.js, Edge, v0, chatbot patterns |
| red-teaming/* | LLM jailbreak techniques |
| gaming/* | Minecraft, Pokemon |
| smart-home/* | Philips Hue |
| note-taking/* | Obsidian |
| data-science/* | Jupyter kernel |
| leisure/* | Find nearby places |
| debugging/* | Syntax error recovery |

## License

MIT — Personal collection. Some skills may reference external tools with their own licenses.

## Author

[kongsak4807017](https://github.com/kongsak4807017)
