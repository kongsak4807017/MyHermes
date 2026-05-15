# Install MyHermes Skills to New Machine

## Quick Install

```bash
# 1. Clone repo
git clone https://github.com/kongsak4807017/MyHermes.git
cd MyHermes

# 2. Copy skills to Hermes directory
cp -r skills/* ~/.hermes/skills/

# 3. Verify
find ~/.hermes/skills/ -name "SKILL.md" | wc -l
# Expected: 148
```

## Symlink Install (Recommended for Development)

```bash
git clone https://github.com/kongsak4807017/MyHermes.git
cd MyHermes

# Create symlinks instead of copying
for dir in skills/*/; do
    ln -sf "$(pwd)/$dir" ~/.hermes/skills/
done
```

## Update Existing Skills

```bash
cd MyHermes
git pull
# Skills auto-update if using symlink
# If copied, re-run: cp -r skills/* ~/.hermes/skills/
```

## Requirements

- Hermes Agent installed
- Python 3.10+ (for skills with scripts)
- API keys for relevant providers (OpenAI, Google, etc.)

## Optional Dependencies

| Skill Group | Dependencies |
|-------------|-------------|
| mlops | PyTorch, transformers, datasets |
| creative | ComfyUI, Stable Diffusion |
| paperbanana | openai, google-generativeai |
| productivity | gws, notion-client |

Install per skill as needed — no global requirements.
