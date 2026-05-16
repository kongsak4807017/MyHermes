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
# Full pipeline (trend → script → media → audio → video → SEO)
hermes-news --topic "AI ครองโลก" --mode standard --lang th --all

# Step by step
hermes-news --step trend --category news                    # Find trends
hermes-news --step script --topic "น้ำท่วมกรุงเทพ" --lang th  # Generate script
hermes-news --step media --topic "น้ำท่วม"                   # Search images
hermes-news --step audio --script-file script.md --lang th  # Generate audio
hermes-news --step video --audio-file audio.wav --media-dir ./media  # Assemble video
hermes-news --step seo --topic "น้ำท่วม" --script-file script.md     # YouTube SEO

# Pre-downloaded media workflow
hermes-news --topic "ดาวอังคาร" --mode knowledge --media-dir ~/Pictures/mars --duration 178 --aspect 9:16

# Direct from script
hermes-news --mode direct --script-file myscript.txt --voice gcloud-th-female --duration 178
```

## Generation Modes

| Mode | Description | Best for |
|------|-------------|----------|
| `standard` | Professional news reporting | Daily news, breaking stories |
| `knowledge` | Educational content (นานาสาระ) | Facts, science, history |
| `survival` | Practical survival skills | How-to, emergency preparedness |
| `viral` | Viral-style content | Maximum engagement, TikTok/Shorts |

## Workflow

```
1. TREND RESEARCH → Find hot topics (Gemini + Google Search)
2. SCRIPT → AI writes engaging script with visual cues
3. MEDIA → Search/download images & videos
4. AUDIO → TTS generates voiceover
5. VIDEO → FFmpeg assembles with visualizer + overlays
6. YOUTUBE SEO MAX → Titles, tags, description, thumbnail, community post
```

## Output Structure

```
output/
├── trends.json         # Trending topics
├── script.md           # Generated script
├── script.json         # Script metadata + visual cues
├── media/              # Downloaded images/videos
├── media.json          # Media file list
├── audio.wav           # Voiceover audio
├── video.mp4           # Final video
├── seo.json            # YouTube MAX SEO metadata
└── README.md           # Upload instructions
```

## YouTube SEO MAX Output

```json
{
  "title": "Main title (60 chars)",
  "title_alt": ["Alt 1", "Alt 2"],
  "description": "Full description with timestamps...",
  "tags": ["tag1", "tag2", ...],
  "thumbnail_text": "3-5 words",
  "thumbnail_colors": ["#FF0000", "#FFFFFF"],
  "playlists": ["Playlist 1", "Playlist 2"],
  "end_screen": {
    "videos": ["Related topic 1", "Related topic 2"],
    "subscribe_cta": "Subscribe text"
  },
  "community_post": "Teaser for Community tab"
}
```

## Commands

### Full Pipeline

```bash
# Everything in one command
python3 ~/.hermes/skills/automate-news/scripts/news_pipeline.py \
  --topic "AI ครองโลก" --mode standard --lang th --all

# Shorts/Reels optimized (178 seconds)
python3 ~/.hermes/skills/automate-news/scripts/news_pipeline.py \
  --topic "ดาวอังคาร" --mode knowledge --lang th \
  --duration 178 --aspect 9:16 --voice edge-th-female
```

### Step by Step

```bash
# 1. Find trends
python3 ~/.hermes/skills/automate-news/scripts/news_pipeline.py --step trend --category news

# 2. Generate script
python3 ~/.hermes/skills/automate-news/scripts/news_pipeline.py \
  --step script --topic "น้ำท่วมกรุงเทพ" --mode standard --lang th

# 3. Search media
python3 ~/.hermes/skills/automate-news/scripts/news_pipeline.py \
  --step media --topic "น้ำท่วมกรุงเทพ"

# 4. Generate audio
python3 ~/.hermes/skills/automate-news/scripts/news_pipeline.py \
  --step audio --script-file output/script.md --voice edge-th-female

# 5. Assemble video
python3 ~/.hermes/skills/automate-news/scripts/news_pipeline.py \
  --step video --audio-file output/audio.wav --media-dir output/media \
  --duration 178 --aspect 9:16

# 6. YouTube SEO
python3 ~/.hermes/skills/automate-news/scripts/news_pipeline.py \
  --step seo --topic "น้ำท่วมกรุงเทพ" --script-file output/script.md
```

### Pre-downloaded Media

```bash
# Use your own images/videos
python3 ~/.hermes/skills/automate-news/scripts/news_pipeline.py \
  --topic "ดาวอังคาร" --mode knowledge \
  --media-dir ~/Pictures/mars-photos \
  --duration 178 --aspect 9:16
```

## Environment Variables

```bash
export GEMINI_API_KEY="your-gemini-key"
export GOOGLE_TTS_API_KEY="your-google-tts-key"
export PERPLEXITY_API_KEY="your-perplexity-key"  # Optional
```

## Resources

- Original app: https://github.com/kongsak4807017/Automate-News
- Video assembler: mp3_to_mv_gui_v5.py (FFmpeg-based)
- Gemini API: https://ai.google.dev
- Edge TTS: https://github.com/rany2/edge-tts
