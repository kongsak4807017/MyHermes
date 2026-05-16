#!/usr/bin/env python3
"""
Automate News Pipeline — Full workflow: Trend → Images → Audio → Video → YouTube SEO
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.parse
import wave
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests


class NewsPipeline:
    """Complete news video pipeline."""

    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "")
        self.google_tts_key = os.environ.get("GOOGLE_TTS_API_KEY", "")
        self.perplexity_key = os.environ.get("PERPLEXITY_API_KEY", "")
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        self.ffmpeg_bin = self._find_ffmpeg()

    # ==================== STEP 1: TREND RESEARCH ====================

    def get_trending_topics(self, category: str = "all", language: str = "th", count: int = 5) -> List[Dict[str, Any]]:
        """Get trending topics using Gemini with Google Search."""
        if not self.gemini_key:
            return [{"error": "GEMINI_API_KEY not set"}]

        cat_prompts = {
            "news": "breaking news and current events",
            "knowledge": "interesting educational topics and science facts",
            "survival": "survival skills and emergency preparedness",
            "entertainment": "viral entertainment and celebrity news",
            "technology": "latest technology trends and innovations",
            "all": "trending topics across all categories",
        }

        prompt = f"""
You are a Trend Intelligence Analyst. Find {count} trending topics right now.

Focus: {cat_prompts.get(category, "trending topics")}
Language: {language}
Current date: {datetime.now().isoformat()}

Requirements:
1. Use Google Search to find REAL trending topics from the last 24-48 hours
2. For each topic provide:
   - title (engaging headline)
   - description (2-3 sentences)
   - why_trending (reason for popularity)
   - suggested_angle (unique perspective for video)
   - keywords (10 tags for search)
   - target_audience (who cares about this)

Return as JSON array.
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview:generateContent?key={self.gemini_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "responseMimeType": "application/json",
            },
        }

        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
            data = response.json()

            if "candidates" in data:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                # Extract JSON
                json_match = re.search(r'\[.*\]', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            return [{"error": "Failed to parse trends"}]
        except Exception as e:
            return [{"error": str(e)}]

    # ==================== STEP 2: SCRIPT GENERATION ====================

    def generate_script(
        self,
        topic: str,
        mode: str = "standard",
        language: str = "th",
        length: str = "3min",
        tone: str = "neutral",
    ) -> Dict[str, Any]:
        """Generate video script."""
        if not self.gemini_key:
            return {"error": "GEMINI_API_KEY not set"}

        length_words = {"1min": 150, "3min": 450, "5min": 750, "10min": 1500}
        word_count = length_words.get(length, 450)

        prompts = {
            "standard": self._build_news_prompt(topic, language, word_count, tone),
            "knowledge": self._build_knowledge_prompt(topic, language, word_count, tone),
            "survival": self._build_survival_prompt(topic, language, word_count, tone),
            "viral": self._build_viral_prompt(topic, language, word_count, tone),
        }

        prompt = prompts.get(mode, prompts["standard"])

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview:generateContent?key={self.gemini_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192},
        }

        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
            data = response.json()

            if "candidates" in data:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                script = self._extract_script(text)
                visual_cues = self._extract_visual_cues(script)

                return {
                    "topic": topic,
                    "mode": mode,
                    "language": language,
                    "script": script,
                    "visual_cues": visual_cues,
                    "word_count": len(script.split()),
                    "generated_at": datetime.now().isoformat(),
                }
            return {"error": "Failed to generate script"}
        except Exception as e:
            return {"error": str(e)}

    # ==================== STEP 3: IMAGE/VIDEO SEARCH ====================

    def search_media(self, query: str, media_type: str = "image", count: int = 5) -> List[Dict[str, str]]:
        """Search for media using web search or APIs."""
        # Try Perplexity first if available
        if self.perplexity_key:
            return self._search_perplexity_media(query, media_type, count)

        # Fallback: Use Gemini to find image URLs
        return self._search_gemini_media(query, media_type, count)

    def _search_perplexity_media(self, query: str, media_type: str, count: int) -> List[Dict[str, str]]:
        """Search media via Perplexity API."""
        url = "https://api.perplexity.ai/chat/completions"

        prompt = f"""Find {count} high-quality {media_type} URLs for: {query}
Return as JSON array with: url, title, source, description.
Only include directly accessible URLs (not search result pages)."""

        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "sonar-pro",
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            data = response.json()

            if "choices" in data:
                text = data["choices"][0]["message"]["content"]
                json_match = re.search(r'\[.*\]', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            return []
        except Exception:
            return []

    def _search_gemini_media(self, query: str, media_type: str, count: int) -> List[Dict[str, str]]:
        """Search media via Gemini with Google Search."""
        if not self.gemini_key:
            return []

        prompt = f"""Find {count} {media_type} sources for: {query}
Return as JSON array with: url (direct link), title, source.
Focus on freely usable sources like Wikimedia Commons, Unsplash, Pexels, Pixabay."""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview:generateContent?key={self.gemini_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.5, "responseMimeType": "application/json"},
        }

        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
            data = response.json()

            if "candidates" in data:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                json_match = re.search(r'\[.*\]', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            return []
        except Exception:
            return []

    def download_media(self, media_list: List[Dict[str, str]], output_dir: Path) -> List[str]:
        """Download media files."""
        downloaded = []

        for i, item in enumerate(media_list):
            url = item.get("url", "")
            if not url:
                continue

            # Determine extension
            ext = ".jpg"
            if ".mp4" in url.lower():
                ext = ".mp4"
            elif ".png" in url.lower():
                ext = ".png"
            elif ".webp" in url.lower():
                ext = ".webp"

            output_path = output_dir / f"media_{i:03d}{ext}"

            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as response:
                    with open(output_path, "wb") as f:
                        f.write(response.read())
                downloaded.append(str(output_path))
            except Exception as e:
                print(f"  ⚠️ Failed to download {url}: {e}")

        return downloaded

    # ==================== STEP 4: AUDIO GENERATION ====================

    def generate_audio(self, script: str, voice: str = "edge-th-female", language: str = "th") -> Dict[str, Any]:
        """Generate audio using TTS."""
        output_path = self.output_dir / "audio.wav"

        # Clean script for TTS
        clean_script = self._sanitize_for_tts(script)

        if voice.startswith("edge-"):
            return self._edge_tts(clean_script, voice, str(output_path))
        elif voice.startswith("gcloud-"):
            return self._google_tts(clean_script, voice, str(output_path))
        elif voice == "gemini":
            return self._gemini_tts(clean_script, str(output_path))
        else:
            return {"error": f"Unknown voice: {voice}"}

    # ==================== STEP 5: VIDEO ASSEMBLY ====================

    def assemble_video(
        self,
        audio_path: str,
        media_paths: List[str],
        output_path: str,
        duration: float = 178.0,
        aspect: str = "9:16",
        add_visualizer: bool = True,
        text_overlay: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Assemble video from audio and media."""
        if not self.ffmpeg_bin:
            return {"error": "FFmpeg not found"}

        # Get audio duration
        audio_dur = self._get_audio_duration(audio_path)
        if not audio_dur:
            return {"error": "Could not get audio duration"}

        # Calculate speed adjustment if needed
        speed = 1.0
        if audio_dur > duration:
            speed = audio_dur / duration
            target_dur = duration
        else:
            target_dur = audio_dur

        # Dimensions
        dims = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)}
        w, h = dims.get(aspect, (1080, 1920))

        # Build FFmpeg command
        cmd = [self.ffmpeg_bin, "-y"]

        # Add media inputs
        for media in media_paths:
            cmd.extend(["-loop", "1", "-i", media])

        # Add audio
        cmd.extend(["-i", audio_path])

        # Build filter complex
        filters = []
        n_media = len(media_paths)

        if n_media == 0:
            # Black background
            filters.append(f"color=c=black:s={w}x{h}:d={target_dur}[vout]")
        elif n_media == 1:
            # Single image with zoom/pan
            filters.append(f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease,setsar=1,zoompan=z='min(zoom+0.0015,1.5)':d={int(target_dur * 30)}:s={w}x{h}[vout]")
        else:
            # Multiple images with crossfade
            segment_dur = target_dur / n_media
            xfade_dur = min(1.0, segment_dur * 0.2)

            current = "[0:v]"
            for i in range(1, n_media):
                out_label = f"v{i}"
                filters.append(f"{current}[{i}:v]xfade=transition=fade:duration={xfade_dur}:offset={segment_dur * i - xfade_dur * (i-1)}[{out_label}]")
                current = f"[{out_label}]"

            # Scale final output
            filters.append(f"{current}scale={w}:{h}:force_original_aspect_ratio=decrease,setsar=1[vout]")

        # Add visualizer if requested
        if add_visualizer:
            vis_h = h // 4
            audio_input = f"[{n_media}:a]"
            filters.append(f"{audio_input}showwaves=s={w}x{vis_h}:mode=line:colors=cyan@0.7,format=rgba[vis]")
            filters.append(f"[vout][vis]overlay=x=0:y=H-h:shortest=1[final]")
            vout_label = "[final]"
        else:
            vout_label = "[vout]"

        # Speed adjustment
        if speed != 1.0:
            atempo = min(2.0, max(0.5, speed))
            filters.append(f"[{n_media}:a]atempo={atempo}[aout]")
            aout_label = "[aout]"
        else:
            aout_label = f"[{n_media}:a]"

        # Add filter complex
        filter_str = ";".join(filters)
        cmd.extend(["-filter_complex", filter_str])

        # Output
        cmd.extend([
            "-map", vout_label,
            "-map", aout_label,
            "-t", str(target_dur),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            output_path,
        ])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return {
                    "video_path": output_path,
                    "duration": target_dur,
                    "speed_adjustment": speed if speed != 1.0 else None,
                    "status": "success",
                }
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    # ==================== STEP 6: YOUTUBE SEO MAX ====================

    def generate_youtube_seo_max(self, topic: str, script: str, language: str = "th") -> Dict[str, Any]:
        """Generate YouTube SEO optimized for MAX reach."""
        if not self.gemini_key:
            return {"error": "GEMINI_API_KEY not set"}

        prompt = f"""
You are a YouTube SEO Expert with 10+ years experience. Generate MAXIMUM REACH metadata.

Topic: {topic}
Language: {language}
Script excerpt: {script[:800]}...

Generate:

1. **TITLE** (3 variants):
   - Main: Click-worthy, includes numbers/power words, under 60 chars
   - Alternative 1: Curiosity gap style
   - Alternative 2: How-to/Question style

2. **DESCRIPTION** (optimized):
   - First 2 lines: Hook with keywords
   - Timestamps (suggest 5-7 chapters)
   - Hashtags (15-20 relevant)
   - Links section
   - Call to action
   - Total: 300-500 words

3. **TAGS** (30 tags):
   - Mix of broad (1-2 words) and long-tail (3-5 words)
   - Include trending variations
   - Competitor channel names (if relevant)

4. **THUMBNAIL TEXT**:
   - Main text (3-5 words, high contrast)
   - Sub text (if needed)
   - Color scheme suggestion

5. **PLAYLIST SUGGESTIONS**:
   - 3 playlist names this video fits

6. **END SCREEN SUGGESTIONS**:
   - 2 video topics to link
   - Subscribe CTA text

7. **COMMUNITY POST**:
   - Short teaser text for Community tab

Return as JSON with all fields.
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview:generateContent?key={self.gemini_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.6, "responseMimeType": "application/json"},
        }

        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
            data = response.json()

            if "candidates" in data:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            return {"error": "Failed to generate SEO"}
        except Exception as e:
            return {"error": str(e)}

    # ==================== PRIVATE HELPERS ====================

    def _build_news_prompt(self, topic: str, lang: str, words: int, tone: str) -> str:
        if lang == "th":
            return f"""เขียนบทพูดข่าวสั้นๆ สำหรับวิดีโอ TikTok/Shorts หัวข้อ: "{topic}"
- ความยาว ~{words} คำ
- โทน: {tone}
- โครงสร้าง: Hook ดึงดูด → ข้อเท็จจริง 3-4 ข้อ → ผลกระทบ → สรุป + CTA
- ใส่ [VISUAL: คำอธิบายภาพ] ทุก 15-20 วินาที
- ภาษาพูด ไม่เป็นทางการมาก แต่น่าเชื่อถือ
- จบด้วยคำถามหรือชวนคอมเมนต์"""
        else:
            return f"""Write a short news script for TikTok/Shorts about: "{topic}"
- Length: ~{words} words
- Tone: {tone}
- Structure: Hook → 3-4 facts → Impact → Summary + CTA
- Include [VISUAL: description] every 15-20 seconds
- Conversational but credible
- End with question or comment CTA"""

    def _build_knowledge_prompt(self, topic: str, lang: str, words: int, tone: str) -> str:
        if lang == "th":
            return f"""เขียนบทความความรู้สั้นๆ หัวข้อ: "{topic}"
- ความยาว ~{words} คำ
- โทน: {tone} สนุก น่าสนใจ
- โครงสร้าง: คำถามน่าสนใจ → คำตอบ → ตัวอย่าง → Fun Fact → สรุป
- ใส่ [VISUAL: คำอธิบาย] ทุก 15-20 วินาที
- อธิบายคำยากให้เข้าใจง่าย
- จบด้วยคำถามให้คิดต่อ"""
        else:
            return f"""Write a short educational script about: "{topic}"
- Length: ~{words} words
- Tone: {tone}, fun and engaging
- Structure: Interesting question → Answer → Examples → Fun Fact → Summary
- Include [VISUAL: description] every 15-20 seconds
- Explain complex terms simply
- End with thought-provoking question"""

    def _build_survival_prompt(self, topic: str, lang: str, words: int, tone: str) -> str:
        if lang == "th":
            return f"""เขียนคู่มือเอาตัวรอดสั้นๆ หัวข้อ: "{topic}"
- ความยาว ~{words} คำ
- โทน: {tone} จริงจัง ชัดเจน
- โครงสร้าง: สถานการณ์ → ขั้นตอนที่ 1-2-3 → ข้อควรระวัง → สรุป
- ใส่ [VISUAL: คำอธิบายเทคนิค] ทุกขั้นตอน
- คำสั่งชัดเจน ทำตามได้จริง"""
        else:
            return f"""Write a short survival guide about: "{topic}"
- Length: ~{words} words
- Tone: {tone}, serious and clear
- Structure: Scenario → Step 1-2-3 → Warnings → Summary
- Include [VISUAL: technique illustration] for each step
- Clear commands, actionable"""

    def _build_viral_prompt(self, topic: str, lang: str, words: int, tone: str) -> str:
        if lang == "th":
            return f"""เขียนบทพูดแบบไวรัล หัวข้อ: "{topic}"
- ความยาว ~{words} คำ
- โทน: {tone} ดึงดูด น่าติดตาม
- ใช้เทคนิค: Curiosity Gap, Pattern Interrupt, Open Loop
- โครงสร้าง: Hook แรงๆ → เปิดประเด็น → สร้างแรงกดดัน → คำตอบ → CTA แรงๆ
- ใส่ [VISUAL: คำอธิบาย] ทุก 10-15 วินาที
- ภาษาพูด ใกล้ชิด ราวกับคุยกับเพื่อน"""
        else:
            return f"""Write a viral-style script about: "{topic}"
- Length: ~{words} words
- Tone: {tone}, attention-grabbing
- Techniques: Curiosity Gap, Pattern Interrupt, Open Loop
- Structure: Strong hook → Open loop → Build tension → Payoff → Strong CTA
- Include [VISUAL: description] every 10-15 seconds
- Conversational, like talking to a friend"""

    def _extract_script(self, text: str) -> str:
        match = re.search(r'```(?:markdown|text)?\n(.*?)\n```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    def _extract_visual_cues(self, script: str) -> List[str]:
        cues = re.findall(r'\[VISUAL:\s*([^\]]+)\]', script, re.IGNORECASE)
        return [c.strip() for c in cues]

    def _sanitize_for_tts(self, text: str) -> str:
        return (text
                .replace("[VISUAL:", "")
                .replace("[SFX:", "")
                .replace("]", "")
                .replace("#", "")
                .replace("**", "")
                .replace("*", "")
                .replace("- ", "")
                .strip())

    def _find_ffmpeg(self) -> Optional[str]:
        candidates = [
            Path.cwd() / "ffmpeg" / "ffmpeg.exe",
            Path.cwd() / "ffmpeg" / "bin" / "ffmpeg.exe",
        ]
        for c in candidates:
            if c.exists():
                return str(c)
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return "ffmpeg"
        except Exception:
            pass
        return None

    def _get_audio_duration(self, path: str) -> Optional[float]:
        try:
            cmd = [self.ffmpeg_bin, "-hide_banner", "-i", path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            match = re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)', result.stderr)
            if match:
                h, m, s = map(float, match.groups())
                return h * 3600 + m * 60 + s
        except Exception:
            pass
        return None

    def _edge_tts(self, script: str, voice: str, output_path: str) -> Dict[str, Any]:
        try:
            from edge_tts import Communicate

            voice_map = {
                "edge-th-female": "th-TH-PremwadeeNeural",
                "edge-th-male": "th-TH-NiwatNeural",
                "edge-en-female": "en-US-AriaNeural",
                "edge-en-male": "en-US-AndrewNeural",
            }
            voice_id = voice_map.get(voice, "th-TH-PremwadeeNeural")

            communicate = Communicate(script, voice_id)
            communicate.save(output_path)

            return {"audio_path": output_path, "voice": voice_id, "status": "success"}
        except Exception as e:
            return {"error": str(e)}

    def _google_tts(self, script: str, voice: str, output_path: str) -> Dict[str, Any]:
        if not self.google_tts_key:
            return {"error": "GOOGLE_TTS_API_KEY not set"}

        try:
            url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.google_tts_key}"

            voice_map = {
                "gcloud-th-female": ("th-TH", "th-TH-Neural2-C"),
                "gcloud-en-female": ("en-US", "en-US-Neural2-F"),
            }
            lang_code, voice_name = voice_map.get(voice, ("th-TH", "th-TH-Neural2-C"))

            payload = {
                "input": {"text": script},
                "voice": {
                    "languageCode": lang_code,
                    "name": voice_name,
                    "ssmlGender": "FEMALE",
                },
                "audioConfig": {"audioEncoding": "MP3"},
            }

            response = requests.post(url, json=payload)
            data = response.json()

            if "audioContent" in data:
                audio_data = base64.b64decode(data["audioContent"])
                with open(output_path, "wb") as f:
                    f.write(audio_data)
                return {"audio_path": output_path, "voice": voice_name, "status": "success"}
            return {"error": data.get("error", "Unknown error")}
        except Exception as e:
            return {"error": str(e)}

    def _gemini_tts(self, script: str, output_path: str) -> Dict[str, Any]:
        if not self.gemini_key:
            return {"error": "GEMINI_API_KEY not set"}

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={self.gemini_key}"

            payload = {
                "contents": [{"role": "user", "parts": [{"text": script}]}],
                "generationConfig": {"responseModalities": ["AUDIO"]},
            }

            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            data = response.json()

            if "candidates" in data:
                parts = data["candidates"][0]["content"]["parts"]
                for part in parts:
                    if "inlineData" in part:
                        audio_data = base64.b64decode(part["inlineData"]["data"])
                        with wave.open(output_path, "wb") as wav:
                            wav.setnchannels(1)
                            wav.setsampwidth(2)
                            wav.setframerate(24000)
                            wav.writeframes(audio_data)
                        return {"audio_path": output_path, "voice": "gemini", "status": "success"}

            return {"error": "No audio in response"}
        except Exception as e:
            return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Automate News Pipeline — Full workflow")
    parser.add_argument("--step", choices=["trend", "script", "media", "audio", "video", "seo", "all"], default="all")
    parser.add_argument("--topic", help="Topic for content generation")
    parser.add_argument("--mode", default="standard", choices=["standard", "knowledge", "survival", "viral"])
    parser.add_argument("--lang", default="th", choices=["th", "en"])
    parser.add_argument("--voice", default="edge-th-female")
    parser.add_argument("--length", default="3min", choices=["1min", "3min", "5min", "10min"])
    parser.add_argument("--duration", type=float, default=178.0, help="Target video duration in seconds")
    parser.add_argument("--aspect", default="9:16", choices=["16:9", "9:16", "1:1"])
    parser.add_argument("--output", default="output")
    parser.add_argument("--media-dir", help="Directory with pre-downloaded media")
    parser.add_argument("--script-file", help="Use existing script file")
    parser.add_argument("--audio-file", help="Use existing audio file")
    parser.add_argument("--category", default="all", help="Trend category")

    args = parser.parse_args()

    pipeline = NewsPipeline()
    pipeline.output_dir = Path(args.output)
    pipeline.output_dir.mkdir(exist_ok=True)

    print(f"🎬 Automate News Pipeline")
    print(f"   Step: {args.step}")
    print(f"   Output: {args.output}")
    print()

    # Step 1: Get trends (if no topic provided)
    if args.step in ["trend", "all"] and not args.topic:
        print("📈 Finding trending topics...")
        trends = pipeline.get_trending_topics(args.category, args.lang)
        if "error" not in trends[0]:
            print(f"   Found {len(trends)} trends:")
            for i, t in enumerate(trends[:5], 1):
                print(f"   {i}. {t.get('title', 'N/A')}")
            # Save trends
            with open(pipeline.output_dir / "trends.json", "w", encoding="utf-8") as f:
                json.dump(trends, f, ensure_ascii=False, indent=2)
        else:
            print(f"   ⚠️ {trends[0].get('error')}")
        print()

    # Step 2: Generate script
    script_data = None
    if args.step in ["script", "all"]:
        if args.script_file:
            print(f"📄 Loading script from {args.script_file}")
            with open(args.script_file, "r", encoding="utf-8") as f:
                script_data = {
                    "topic": args.topic or "Custom",
                    "script": f.read(),
                    "visual_cues": [],
                }
        elif args.topic:
            print(f"📝 Generating script for: {args.topic}")
            script_data = pipeline.generate_script(
                topic=args.topic,
                mode=args.mode,
                language=args.lang,
                length=args.length,
            )
            if "error" not in script_data:
                # Save script
                with open(pipeline.output_dir / "script.md", "w", encoding="utf-8") as f:
                    f.write(script_data["script"])
                with open(pipeline.output_dir / "script.json", "w", encoding="utf-8") as f:
                    json.dump(script_data, f, ensure_ascii=False, indent=2)
                print(f"   ✅ Script saved ({script_data.get('word_count', 0)} words)")
                print(f"   🎨 Visual cues: {len(script_data.get('visual_cues', []))}")
            else:
                print(f"   ❌ {script_data['error']}")
        print()

    # Step 3: Search/download media
    media_paths = []
    if args.step in ["media", "all"]:
        if args.media_dir:
            print(f"📁 Using media from: {args.media_dir}")
            media_dir = Path(args.media_dir)
            media_paths = [str(p) for p in media_dir.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".mp4")]
            print(f"   Found {len(media_paths)} media files")
        elif script_data and script_data.get("visual_cues"):
            print("🔍 Searching for media...")
            cues = script_data["visual_cues"][:5]  # Top 5 cues
            for cue in cues:
                print(f"   Searching: {cue}")
                results = pipeline.search_media(cue, "image", 2)
                if results:
                    downloaded = pipeline.download_media(results, pipeline.output_dir / "media")
                    media_paths.extend(downloaded)
            print(f"   ✅ Downloaded {len(media_paths)} media files")

        # Save media list
        with open(pipeline.output_dir / "media.json", "w", encoding="utf-8") as f:
            json.dump(media_paths, f, indent=2)
        print()

    # Step 4: Generate audio
    audio_path = None
    if args.step in ["audio", "all"]:
        if args.audio_file:
            print(f"🔊 Using audio: {args.audio_file}")
            audio_path = args.audio_file
        elif script_data:
            print("🔊 Generating audio...")
            result = pipeline.generate_audio(
                script=script_data["script"],
                voice=args.voice,
                language=args.lang,
            )
            if "error" not in result:
                audio_path = result["audio_path"]
                print(f"   ✅ Audio saved: {audio_path}")
            else:
                print(f"   ❌ {result['error']}")
        print()

    # Step 5: Assemble video
    video_path = None
    if args.step in ["video", "all"] and audio_path:
        print("🎥 Assembling video...")
        video_file = str(pipeline.output_dir / "video.mp4")
        result = pipeline.assemble_video(
            audio_path=audio_path,
            media_paths=media_paths,
            output_path=video_file,
            duration=args.duration,
            aspect=args.aspect,
        )
        if "error" not in result:
            video_path = result["video_path"]
            print(f"   ✅ Video saved: {video_path}")
            print(f"   ⏱️ Duration: {result['duration']:.1f}s")
            if result.get("speed_adjustment"):
                print(f"   ⚡ Speed adjusted: {result['speed_adjustment']:.2f}x")
        else:
            print(f"   ❌ {result['error']}")
        print()

    # Step 6: YouTube SEO
    if args.step in ["seo", "all"] and script_data:
        print("📊 Generating YouTube SEO (MAX)...")
        seo = pipeline.generate_youtube_seo_max(
            topic=script_data["topic"],
            script=script_data["script"],
            language=args.lang,
        )
        if "error" not in seo:
            with open(pipeline.output_dir / "seo.json", "w", encoding="utf-8") as f:
                json.dump(seo, f, ensure_ascii=False, indent=2)
            print(f"   ✅ SEO saved")
            if "title" in seo:
                print(f"   📝 Title: {seo['title']}")
            if "tags" in seo:
                print(f"   🏷️ Tags: {len(seo['tags'])} tags")
        else:
            print(f"   ❌ {seo['error']}")
        print()

    print("🎉 Pipeline complete!")
    print(f"   Output directory: {args.output}")
    if video_path:
        print(f"   Video: {video_path}")


if __name__ == "__main__":
    main()
