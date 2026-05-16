---
name: automate-news
description: "Automated content creation for news, knowledge, and expert analysis videos. Generate scripts, audio, and video from topics using Gemini AI, TTS, and FFmpeg."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [python3, ffmpeg, curl]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [News, Content Creation, Video, TTS, Gemini, YouTube, TikTok, Knowledge, Analysis]
---

# automate-news for Hermes

Automated content creation pipeline for Hermes. Transform any topic into a video-ready script with voiceover.

## What's inside

- **6 Generation Modes**: News, Friend-to-Friend, Expert Analysis, Knowledge (นานาสาระ), Survival, Direct TTS
- **Multi-language**: Thai, English
- **TTS Integration**: Edge TTS (free), Google Cloud TTS (pro), Gemini TTS (AI Studio)
- **Video Pipeline**: FFmpeg-based video assembly
- **YouTube SEO**: Auto-generate titles, descriptions, tags

## Quick start

```bash
# Standard news
hermes-news "AI ครองโลก" --mode standard --lang th

# Expert analysis
hermes-news "เศรษฐกิจไทย 2026" --mode expert --lang th --lens economy

# Knowledge (นานาสาระ)
hermes-news "ทำไมท้องฟ้าถึงเป็นสีฟ้า" --mode knowledge --lang th

# Survival
hermes-news "เอาตัวรอดในป่า" --mode survival --lang th

# Direct TTS (paste your own script)
hermes-news --mode direct --script-file myscript.txt --lang th
```

## Generation Modes

| Mode | Description | Best for |
|------|-------------|----------|
| `standard` | Professional news reporting | Daily news, breaking stories |
| `friend` | Casual conversation style | Social media, engaging content |
| `expert` | Deep analysis with expert lenses | Complex topics, investigations |
| `knowledge` | Educational content (นานาสาระ) | Facts, science, history |
| `survival` | Practical survival skills | How-to, emergency preparedness |
| `direct` | Your own script → audio/video | Custom content |

## Expert Lenses (for expert mode)

| Lens | Focus |
|------|-------|
| `economy` | Economic impact, financial analysis |
| `politics` | Political implications, policy analysis |
| `technology` | Tech angle, innovation assessment |
| `social` | Social impact, community effects |
| `environment` | Environmental factors, sustainability |
| `health` | Health implications, medical perspective |
| `legal` | Legal framework, regulatory impact |
| `history` | Historical context, precedent analysis |

## Commands

### Generate Content

```bash
hermes-news <topic> [options]

Options:
  --mode, -m        Generation mode (standard|friend|expert|knowledge|survival|direct)
  --lang, -l        Language (th|en)
  --voice, -v       TTS voice (edge-th-female|edge-th-male|gcloud-th-female|gemini)
  --length          Script length (1min|3min|5min|10min)
  --lens            Expert lens (for expert mode)
  --output, -o      Output directory
  --script-file     Input script file (for direct mode)
  --tone            Emotional tone (neutral|serious|excited|calm|urgent)
```

### Examples

```bash
# Thai news with female voice
hermes-news "น้ำท่วมกรุงเทพ" --mode standard --lang th --voice edge-th-female

# Expert analysis on economy
hermes-news "คริปโตขาลง" --mode expert --lens economy --lang th

# Knowledge video about space
hermes-news "ดาวอังคาร" --mode knowledge --lang th --length 5min

# Survival guide
hermes-news "เอาตัวรอดจากแผ่นดินไหว" --mode survival --lang th

# Direct TTS from file
hermes-news --mode direct --script-file script.txt --voice gcloud-th-female
```

## Workflow

```
1. Research → Gemini searches web for current info
2. Script → AI writes engaging script based on mode
3. Audio → TTS generates voiceover
4. Visuals → Search for relevant images/video clips
5. Video → FFmpeg assembles final video
6. SEO → Generate YouTube title/description/tags
```

## Output Structure

```
output/
├── script.md           # Generated script
├── audio.wav           # Voiceover audio
├── visuals/            # Downloaded images
├── video.mp4           # Final video
├── seo.json            # YouTube metadata
└── citations.json      # Source references
```

## Resources

- Original app: https://github.com/kongsak4807017/Automate-News
- Gemini API: https://ai.google.dev
- Edge TTS: https://github.com/rany2/edge-tts
