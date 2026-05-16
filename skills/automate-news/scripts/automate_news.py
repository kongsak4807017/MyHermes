#!/usr/bin/env python3
"""
Automate News - Content creation pipeline for Hermes.
Generates scripts, audio, and video from topics.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import wave
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


class AutomateNews:
    """Main content creation pipeline."""

    def __init__(self, api_key: Optional[str] = None):
        self.gemini_api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.google_tts_key = os.environ.get("GOOGLE_TTS_API_KEY", "")
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def generate_script(
        self,
        topic: str,
        mode: str = "standard",
        language: str = "th",
        length: str = "3min",
        lens: Optional[str] = None,
        tone: str = "neutral",
    ) -> Dict[str, Any]:
        """Generate script using Gemini API."""
        if not self.gemini_api_key:
            return {"error": "GEMINI_API_KEY not set"}

        # Build prompt based on mode
        prompts = {
            "standard": self._build_news_prompt(topic, language, length, tone),
            "friend": self._build_friend_prompt(topic, language, length, tone),
            "expert": self._build_expert_prompt(topic, language, length, lens, tone),
            "knowledge": self._build_knowledge_prompt(topic, language, length, tone),
            "survival": self._build_survival_prompt(topic, language, length, tone),
        }

        prompt = prompts.get(mode, prompts["standard"])

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview:generateContent?key={self.gemini_api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192,
            },
        }

        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            data = response.json()

            if "candidates" in data:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                # Extract script from markdown code blocks if present
                script = self._extract_script(text)
                citations = self._extract_citations(text)

                return {
                    "topic": topic,
                    "mode": mode,
                    "language": language,
                    "script": script,
                    "citations": citations,
                    "generated_at": datetime.now().isoformat(),
                }
            else:
                return {"error": f"API Error: {data.get('error', 'Unknown error')}"}

        except Exception as e:
            return {"error": str(e)}

    def generate_audio(
        self,
        script: str,
        voice: str = "edge-th-female",
        language: str = "th",
    ) -> Dict[str, Any]:
        """Generate audio using TTS."""
        output_path = self.output_dir / "audio.wav"

        if voice.startswith("edge-"):
            return self._edge_tts(script, voice, str(output_path))
        elif voice.startswith("gcloud-"):
            return self._google_tts(script, voice, str(output_path))
        elif voice == "gemini":
            return self._gemini_tts(script, str(output_path))
        else:
            return {"error": f"Unknown voice: {voice}"}

    def generate_video(
        self,
        audio_path: str,
        visuals_dir: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate video using FFmpeg."""
        if not output_path:
            output_path = str(self.output_dir / "video.mp4")

        # Simple video: black background + audio
        # For advanced: use visuals_dir images
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=1920x1080:r=30",
            "-i", audio_path,
            "-shortest",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            output_path,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return {"video_path": output_path, "status": "success"}
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    def generate_seo(self, topic: str, script: str, language: str = "th") -> Dict[str, Any]:
        """Generate YouTube SEO metadata."""
        if not self.gemini_api_key:
            return {"error": "GEMINI_API_KEY not set"}

        prompt = f"""
Generate YouTube SEO metadata for this video:

Topic: {topic}
Language: {language}
Script excerpt: {script[:500]}...

Generate:
1. Catchy title (max 60 chars)
2. Description (max 500 chars)
3. 10 relevant tags
4. Thumbnail text suggestion

Return as JSON with keys: title, description, tags (array), thumbnail_text
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview:generateContent?key={self.gemini_api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.5},
        }

        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            data = response.json()

            if "candidates" in data:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                # Extract JSON from response
                json_match = re.search(r"\{.*\}", text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return {"title": topic, "description": script[:200], "tags": [topic]}
            return {"error": "Failed to generate SEO"}
        except Exception as e:
            return {"error": str(e)}

    # --- Private methods ---

    def _build_news_prompt(self, topic: str, lang: str, length: str, tone: str) -> str:
        lengths = {"1min": "150 words", "3min": "450 words", "5min": "750 words", "10min": "1500 words"}
        word_count = lengths.get(length, "450 words")

        if lang == "th":
            return f"""
เขียนบทพูดข่าวสำหรับวิดีโอสั้น หัวข้อ: "{topic}"

ข้อกำหนด:
- ความยาว: {word_count}
- โทน: {tone}
- ภาษา: ภาษาไทยที่เป็นทางการแต่เข้าใจง่าย
- โครงสร้าง: Hook → ข้อเท็จจริง → บริบท → ผลกระทบ → สรุป
- ใส่ [VISUAL: คำอธิบายภาพ] ในจุดที่ต้องการภาพประกอบ
- ใส่ [SFX: เสียงประกอบ] ในจุดที่ต้องการเสียงพิเศษ
- ระบุแหล่งที่มาที่น่าเชื่อถือ

เขียนให้น่าสนใจ กระชับ และเหมาะสำหรับการอ่านออกเสียง
"""
        else:
            return f"""
Write a news script for a short video about: "{topic}"

Requirements:
- Length: {word_count}
- Tone: {tone}
- Structure: Hook → Facts → Context → Impact → Summary
- Include [VISUAL: description] for image cues
- Include [SFX: sound effect] for audio cues
- Cite credible sources

Make it engaging, concise, and suitable for voiceover.
"""

    def _build_friend_prompt(self, topic: str, lang: str, length: str, tone: str) -> str:
        lengths = {"1min": "150 words", "3min": "450 words", "5min": "750 words", "10min": "1500 words"}
        word_count = lengths.get(length, "450 words")

        if lang == "th":
            return f"""
เขียนบทสนทนาแบบคุยกับเพื่อน หัวข้อ: "{topic}"

ข้อกำหนด:
- ความยาว: {word_count}
- โทน: {tone} สบายๆ เหมือนคุยกับเพื่อน
- ภาษา: ภาษาพูด ไม่เป็นทางการ
- ใช้คำว่า "เรา" "พวกเรา" เพื่อสร้างความใกล้ชิด
- มีคำถามรhetorical เพื่อดึงความสนใจ
- ใส่อารมณ์ขันเล็กน้อยถ้าเหมาะสม
- ใส่ [VISUAL] และ [SFX] ตามต้องการ
"""
        else:
            return f"""
Write a friendly conversation script about: "{topic}"

Requirements:
- Length: {word_count}
- Tone: {tone}, casual like talking to a friend
- Use "we" "us" to create connection
- Include rhetorical questions
- Add light humor if appropriate
- Include [VISUAL] and [SFX] cues
"""

    def _build_expert_prompt(self, topic: str, lang: str, length: str, lens: Optional[str], tone: str) -> str:
        lengths = {"1min": "150 words", "3min": "450 words", "5min": "750 words", "10min": "1500 words"}
        word_count = lengths.get(length, "450 words")
        lens_text = f" with {lens} perspective" if lens else ""

        if lang == "th":
            return f"""
เขียนบทวิเคราะห์เชิงลึกโดยผู้เชี่ยวชาญ หัวข้อ: "{topic}"{lens_text}

ข้อกำหนด:
- ความยาว: {word_count}
- โทน: {tone} เชิงวิชาการแต่เข้าใจง่าย
- โครงสร้าง: ปัญหา → ข้อมูล → การวิเคราะห์ → ข้อสรุป → คำแนะนำ
- ใช้ข้อมูลเชิงลึก สถิติ ตัวเลข
- วิเคราะห์จากหลายมิติ
- ระบุแหล่งที่มาอ้างอิง
- ใส่ [VISUAL] สำหรับกราฟ แผนภูมิ หรือข้อมูลสำคัญ
"""
        else:
            return f"""
Write an expert analysis script about: "{topic}"{lens_text}

Requirements:
- Length: {word_count}
- Tone: {tone}, authoritative but accessible
- Structure: Problem → Data → Analysis → Conclusion → Recommendations
- Use deep insights, statistics, numbers
- Multi-dimensional analysis
- Cite sources
- Include [VISUAL] for charts and key data
"""

    def _build_knowledge_prompt(self, topic: str, lang: str, length: str, tone: str) -> str:
        lengths = {"1min": "150 words", "3min": "450 words", "5min": "750 words", "10min": "1500 words"}
        word_count = lengths.get(length, "450 words")

        if lang == "th":
            return f"""
เขียนบทความความรู้ (นานาสาระ) หัวข้อ: "{topic}"

ข้อกำหนด:
- ความยาว: {word_count}
- โทน: {tone} สนุก น่าสนใจ ให้ความรู้
- โครงสร้าง: คำถามน่าสนใจ → คำอธิบาย → ตัวอย่าง → ข้อเท็จจริงที่น่าทึ่ง → สรุป
- ใช้ภาษาที่เข้าใจง่าย อธิบายคำยาก
- มีตัวอย่างประกอบ
- ใส่ [VISUAL] สำหรับภาพประกอบการอธิบาย
- จบด้วยคำถามให้คิดต่อ หรือ fun fact
"""
        else:
            return f"""
Write an educational knowledge script about: "{topic}"

Requirements:
- Length: {word_count}
- Tone: {tone}, fun, engaging, educational
- Structure: Interesting question → Explanation → Examples → Amazing facts → Summary
- Use simple language, explain complex terms
- Include examples
- Include [VISUAL] for explanatory images
- End with thought-provoking question or fun fact
"""

    def _build_survival_prompt(self, topic: str, lang: str, length: str, tone: str) -> str:
        lengths = {"1min": "150 words", "3min": "450 words", "5min": "750 words", "10min": "1500 words"}
        word_count = lengths.get(length, "450 words")

        if lang == "th":
            return f"""
เขียนคู่มือเอาตัวรอด หัวข้อ: "{topic}"

ข้อกำหนด:
- ความยาว: {word_count}
- โทน: {tone} จริงจัง ชัดเจน ใช้งานได้จริง
- โครงสร้าง: สถานการณ์ → ขั้นตอนที่ 1 → ขั้นตอนที่ 2 → ... → ข้อควรระวัง → สรุป
- คำแนะนำต้องปฏิบัติได้จริง
- ใช้คำสั่งชัดเจน ("ต้องทำ..." "อย่าลืม...")
- ใส่ [VISUAL] สำหรับภาพประกอบเทคนิค
- ใส่ [SFX] สำหรับเสียงเตือนหรือประกอบ
"""
        else:
            return f"""
Write a survival guide script about: "{topic}"

Requirements:
- Length: {word_count}
- Tone: {tone}, serious, clear, actionable
- Structure: Scenario → Step 1 → Step 2 → ... → Warnings → Summary
- Practical, actionable advice
- Clear commands ("Do this..." "Don't forget...")
- Include [VISUAL] for technique illustrations
- Include [SFX] for warning or ambient sounds
"""

    def _extract_script(self, text: str) -> str:
        """Extract script from markdown code blocks."""
        # Try to find code blocks
        match = re.search(r"```(?:markdown|text)?\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    def _extract_citations(self, text: str) -> List[Dict[str, str]]:
        """Extract citations from text."""
        citations = []
        # Match URL patterns
        urls = re.findall(r"https?://[^\s\)\]\"]+", text)
        for url in urls:
            citations.append({"url": url, "title": "Source"})
        return citations

    def _edge_tts(self, script: str, voice: str, output_path: str) -> Dict[str, Any]:
        """Generate audio using Edge TTS."""
        try:
            from edge_tts import Communicate

            voice_map = {
                "edge-th-female": "th-TH-PremwadeeNeural",
                "edge-th-male": "th-TH-NiwatNeural",
                "edge-en-female": "en-US-AriaNeural",
                "edge-en-male": "en-US-AndrewNeural",
            }

            voice_id = voice_map.get(voice, "th-TH-PremwadeeNeural")

            # Sanitize script for TTS
            clean_script = self._sanitize_for_tts(script)

            communicate = Communicate(clean_script, voice_id)
            communicate.save(output_path)

            return {"audio_path": output_path, "voice": voice_id, "status": "success"}
        except Exception as e:
            return {"error": str(e)}

    def _google_tts(self, script: str, voice: str, output_path: str) -> Dict[str, Any]:
        """Generate audio using Google Cloud TTS."""
        if not self.google_tts_key:
            return {"error": "GOOGLE_TTS_API_KEY not set"}

        try:
            url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.google_tts_key}"

            voice_map = {
                "gcloud-th-female": ("th-TH", "th-TH-Neural2-C"),
                "gcloud-en-female": ("en-US", "en-US-Neural2-F"),
            }

            lang_code, voice_name = voice_map.get(voice, ("th-TH", "th-TH-Neural2-C"))

            clean_script = self._sanitize_for_tts(script)

            payload = {
                "input": {"text": clean_script},
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
                import base64

                audio_data = base64.b64decode(data["audioContent"])
                with open(output_path, "wb") as f:
                    f.write(audio_data)
                return {"audio_path": output_path, "voice": voice_name, "status": "success"}
            else:
                return {"error": data.get("error", "Unknown error")}

        except Exception as e:
            return {"error": str(e)}

    def _gemini_tts(self, script: str, output_path: str) -> Dict[str, Any]:
        """Generate audio using Gemini TTS."""
        if not self.gemini_api_key:
            return {"error": "GEMINI_API_KEY not set"}

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={self.gemini_api_key}"

            clean_script = self._sanitize_for_tts(script)

            payload = {
                "contents": [{"role": "user", "parts": [{"text": clean_script}]}],
                "generationConfig": {"responseModalities": ["AUDIO"]},
            }

            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            data = response.json()

            if "candidates" in data:
                parts = data["candidates"][0]["content"]["parts"]
                for part in parts:
                    if "inlineData" in part:
                        import base64

                        audio_data = base64.b64decode(part["inlineData"]["data"])

                        # Save as WAV (PCM 16-bit, 24kHz)
                        with wave.open(output_path, "wb") as wav:
                            wav.setnchannels(1)
                            wav.setsampwidth(2)
                            wav.setframerate(24000)
                            wav.writeframes(audio_data)

                        return {"audio_path": output_path, "voice": "gemini", "status": "success"}

            return {"error": "No audio in response"}

        except Exception as e:
            return {"error": str(e)}

    def _sanitize_for_tts(self, text: str) -> str:
        """Sanitize script for TTS."""
        return (
            text.replace("[VISUAL:", "")
            .replace("[SFX:", "")
            .replace("]", "")
            .replace("#", "")
            .replace("**", "")
            .replace("*", "")
            .replace("- ", "")
            .strip()
        )


def main():
    parser = argparse.ArgumentParser(description="Automate News - Content creation pipeline")
    parser.add_argument("topic", nargs="?", help="Topic to generate content about")
    parser.add_argument("--mode", "-m", default="standard", choices=["standard", "friend", "expert", "knowledge", "survival", "direct"])
    parser.add_argument("--lang", "-l", default="th", choices=["th", "en"])
    parser.add_argument("--voice", "-v", default="edge-th-female", help="TTS voice")
    parser.add_argument("--length", default="3min", choices=["1min", "3min", "5min", "10min"])
    parser.add_argument("--lens", help="Expert lens (for expert mode)")
    parser.add_argument("--output", "-o", default="output", help="Output directory")
    parser.add_argument("--script-file", help="Input script file (for direct mode)")
    parser.add_argument("--tone", default="neutral", choices=["neutral", "serious", "excited", "calm", "urgent"])
    parser.add_argument("--skip-audio", action="store_true", help="Skip audio generation")
    parser.add_argument("--skip-video", action="store_true", help="Skip video generation")
    parser.add_argument("--api-key", help="Gemini API key")

    args = parser.parse_args()

    # Validate arguments
    if args.mode == "direct" and not args.script_file:
        print("Error: --script-file required for direct mode")
        sys.exit(1)

    if args.mode != "direct" and not args.topic:
        print("Error: topic required for non-direct modes")
        sys.exit(1)

    # Initialize
    news = AutomateNews(api_key=args.api_key)
    news.output_dir = Path(args.output)
    news.output_dir.mkdir(exist_ok=True)

    print(f"🎬 Automate News - Mode: {args.mode}, Lang: {args.lang}")

    # Step 1: Generate or load script
    if args.mode == "direct":
        with open(args.script_file, "r", encoding="utf-8") as f:
            script_data = {
                "topic": "Direct TTS",
                "mode": "direct",
                "language": args.lang,
                "script": f.read(),
                "citations": [],
            }
        print(f"📄 Loaded script from {args.script_file}")
    else:
        print(f"📝 Generating script for: {args.topic}")
        script_data = news.generate_script(
            topic=args.topic,
            mode=args.mode,
            language=args.lang,
            length=args.length,
            lens=args.lens,
            tone=args.tone,
        )

    if "error" in script_data:
        print(f"❌ Error: {script_data['error']}")
        sys.exit(1)

    # Save script
    script_path = news.output_dir / "script.md"
    script_path.write_text(script_data["script"], encoding="utf-8")
    print(f"✅ Script saved to {script_path}")

    # Save metadata
    meta_path = news.output_dir / "metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Metadata saved to {meta_path}")

    # Step 2: Generate audio
    if not args.skip_audio:
        print(f"🔊 Generating audio with voice: {args.voice}")
        audio_result = news.generate_audio(script_data["script"], voice=args.voice, language=args.lang)

        if "error" in audio_result:
            print(f"⚠️ Audio error: {audio_result['error']}")
        else:
            print(f"✅ Audio saved to {audio_result['audio_path']}")

    # Step 3: Generate SEO
    print("📊 Generating YouTube SEO metadata")
    seo_data = news.generate_seo(args.topic or "Direct TTS", script_data["script"], args.lang)

    if "error" not in seo_data:
        seo_path = news.output_dir / "seo.json"
        with open(seo_path, "w", encoding="utf-8") as f:
            json.dump(seo_data, f, ensure_ascii=False, indent=2)
        print(f"✅ SEO metadata saved to {seo_path}")
        print(f"   Title: {seo_data.get('title', 'N/A')}")

    # Step 4: Generate video
    if not args.skip_video and not args.skip_audio:
        audio_file = news.output_dir / "audio.wav"
        if audio_file.exists():
            print("🎥 Generating video")
            video_result = news.generate_video(str(audio_file))

            if "error" in video_result:
                print(f"⚠️ Video error: {video_result['error']}")
            else:
                print(f"✅ Video saved to {video_result['video_path']}")

    print("\n🎉 Done! Check the output directory for results.")


if __name__ == "__main__":
    main()
