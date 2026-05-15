#!/usr/bin/env python3
"""
Template: Nightly Batch Narrative Generator for Local Models
- Provider: ollama-local (gemma4:e4b, llama3, etc.)
- Use case: Cron job running overnight when user is asleep
- Output: Markdown files ready for TTS (text-to-speech)

SETUP:
  python3 -m venv /tmp/hermes-run-venv
  /tmp/hermes-run-venv/bin/pip install python-dotenv openai anthropic \
      httpx rich tenacity pyyaml requests jinja2 pydantic prompt_toolkit

RUN:
  cd /mnt/c/Users/User/hermes-agent && \
    /tmp/hermes-run-venv/bin/python /home/user/.hermes/scripts/nightly_batch.py
"""

import re
import sys
from datetime import datetime
from pathlib import Path

# ─── CONFIG ───
HERMES_AGENT = Path("/mnt/c/Users/User/hermes-agent")
sys.path.insert(0, str(HERMES_AGENT))

from run_agent import AIAgent

OUTPUT_DIR = Path.home() / ".hermes" / "narratives" / "news"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── MOCK NEWS (replace with real fetch via searxng, RSS, etc.) ───
NEWS_CONTEXT = """[1] ดาราสาวชื่อดังโพสต์ภาพคู่กับนักธุรกิจหนุ่ม...
[2] รัฐบาลประกาศมาตรการใหม่เรื่องภาษีดิจิทัล...
[3] นักฟุตบอลทีมชาติไทยยิงประตูชัยนาทีสุดท้าย..."""

# ─── PROMPT TEMPLATES ───

STANDARD_NEWS = """คุณคือผู้อำนวยการผลิตสารคดีเชิงสืบสวนระดับโลก...

CRITICAL RULES:
1. แหล่งข่าวที่เชื่อถือได้ (VERIFIED REFERENCES ONLY)
2. ความสดใหม่: ข้อมูลต้องเป็นเหตุการณ์ที่เกิดขึ้นภายใน 24 ชั่วโมงที่ผ่านมา
3. ห้ามมีคำนำหรือคำลงท้าย: เริ่มรันเนื้อหา [SCRIPT] ทันที
4. บทพูดภาษาพูดล้วนๆ (PURE SPOKEN LANGUAGE)
5. ห้ามใช้วงเล็บและเลขอ้างอิง
6. ความยาว: ประมาณ 2500-2700 ตัวอักษร

ข่าวที่ต้องนำเสนอ:
{news_content}

เขียนบทพูดเป็นภาษาไทย สไตล์รายการข่าวมืออาชีพ:"""

FRIEND_TO_FRIEND = """คุณคือเพื่อนสนิทที่กำลังเล่าเรื่องให้เพื่อนฟัง...

STORYTELLING STYLE & LANGUAGE:
- ใช้ภาษาเพื่อการพูดแบบเป็นธรรมชาติมากๆ
- มีการแสดงความรู้สึกตื่นเต้น เป็นห่วง หรือสงสัยใคร่รู้
- ให้ใช้คำพูดเกริ่นนำอารมณ์ประเภท 'แกรู้เรื่องนี้ยัง...'
- ให้แยกระหว่างสิ่งที่ 'ชาวเน็ตเม้าท์กัน' กับสิ่งที่ 'แหล่งข่าวยืนยันแล้ว'
- ใช้ PURE SPOKEN TEXT และห้ามใส่วงเล็บกำกับใดๆ เด็ดขาด
- ความยาว: ประมาณ 2500-2700 ตัวอักษร

ข่าวที่ต้องเล่า:
{news_content}

เขียนบทพูดเป็นภาษาไทย สไตล์เพื่อนเล่าให้เพื่อนฟัง:"""

EXPERT_DEEP_DIVE = """คุณคือสุดยอดผู้ช่วยวิจัยและทีมรวมผู้เชี่ยวชาญระดับโลก...

วิเคราะห์ข่าวต่อไปนี้อย่างลึกซึ้ง:
{news_content}

จากนั้นเขียนบทพูดสไตล์ Expert Deep Dive:
- ถักทอมุมมองของผู้เชี่ยวชาญแต่ละด้านเข้าด้วยกันให้เป็นเนื้อเดียว
- ใช้เทคนิคการเล่าเรื่อง: มีท่อนฮุค (Hook) ที่ทรงพลัง
- โทนเสียง: ต้องเป็นผู้ทรงภูมิปัญญา เข้าถึงได้ง่าย
- ห้ามใส่วงเล็บ อ้างอิง หรือคำอธิบายเอฟเฟกต์ภาพใดๆ
- ความยาว: ประมาณ 2500-2700 ตัวอักษร

เขียนบทพูดเป็นภาษาไทย สไตล์ผู้เชี่ยวชาญวิเคราะห์เชิงลึก:"""

# ─── UTILS ───

def clean_for_tts(text):
    """Remove stage directions and meta commentary for TTS output."""
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'#{1,6}\s*คำแนะนำ.*?(?=---|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'\*\*💡.*?(?=---|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'\[SCRIPT\]\s*', '', text)
    return text.strip()

def save_narrative(content, style_name, date_str):
    filename = f"{date_str}_{style_name.replace(' ', '_')}.md"
    filepath = OUTPUT_DIR / filename
    clean = clean_for_tts(content)
    md = f"""# ข่าวดังประจำวันที่ {date_str} — {style_name}

> สร้างโดย AI (gemma4:e4b) เมื่อ {datetime.now().strftime('%H:%M:%S')}
> สไตล์: {style_name}

---

{clean}

---

*สร้างอัตโนมัติโดยระบบ Nightly News Narrative Generator*
"""
    filepath.write_text(md, encoding='utf-8')
    print(f"Saved: {filepath} ({len(clean)} chars)")
    return filepath

# ─── MAIN ───

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"=== Nightly News Narrative Generator ===")
    print(f"Date: {date_str}")
    
    print("\n[1/4] Initializing AI agent (gemma4:e4b)...")
    agent = AIAgent(
        provider="ollama-local",
        model="gemma4:e4b",
        max_iterations=2,
        quiet_mode=True,
    )
    print("Agent ready")
    
    styles = [
        ("Standard News", STANDARD_NEWS),
        ("Friend to Friend", FRIEND_TO_FRIEND),
        ("Expert Deep Dive", EXPERT_DEEP_DIVE),
    ]
    
    files = []
    for i, (name, template) in enumerate(styles, 2):
        print(f"\n[{i}/4] Generating {name}...")
        prompt = template.format(news_content=NEWS_CONTEXT)
        try:
            result = agent.chat(prompt)
            filepath = save_narrative(result, name, date_str)
            files.append(filepath)
        except Exception as e:
            print(f"Error generating {name}: {e}")
    
    print(f"\n=== DONE ===")
    print(f"Generated {len(files)} files in {OUTPUT_DIR}")
    return files

if __name__ == "__main__":
    main()
