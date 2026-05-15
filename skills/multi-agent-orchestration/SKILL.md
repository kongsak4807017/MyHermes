---
name: multi-agent-orchestration
description: คู่มือ Hermes Agent orchestrator pattern — ใช้ delegate_task + hermes subprocess + tmux spawning เพื่อแบ่งงานให้ sub-agents หลายตัวทำงานขนานกัน แล้วรวมผลกลับมา เหมาะสำหรับงานที่ซับซ้อน ต้องใช้หลายโมเดล หรือรันหลายงานพร้อมกัน
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [orchestration, multi-agent, delegate_task, subagent, workflow, parallel]
    related_skills: [hermes-agent]
---

# Multi-Agent Orchestration Pattern

Hermes เป็น **orchestrator** ที่แบ่งงานให้ sub-agents หลายตัวทำงานขนานกัน แล้วรวมผลกลับมา

## Architecture

```
                    ┌─────────────────┐
                    │   Orchestrator   │
                    │  (Hermes Agent)  │
                    └────────┬────────┘
                             │ บริหารงาน แบ่ง task
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ Sub-Agent A │  │ Sub-Agent B │  │ Sub-Agent C │
     │ (วิเคราะห์) │  │ (เขียนโค้ด)  │  │ (review)   │
     └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
           │               │               │
           └───────────────┼───────────────┘
                           ▼
                    ┌─────────────┐
                    │ รวมผล → ตอบ │
                    └─────────────┘
```

## 3 ระดับการ Orchestrate

### ระดับ 1: `delegate_task` (เร็วที่สุด)
- Spawn sub-agent ใน process เดียวกัน แยก context
- เหมาะสำหรับงานสั้น-กลาง (ไม่กี่นาที)
- รองรับ parallel สูงสุด 3 tasks พร้อมกัน
- **รองรับ provider/model override** — ส่ง subagent ไป provider อื่นได้เลย

```python
# ใน tool call
delegate_task(
    goal="วิเคราะห์โค้ดใน main.py",
    context="โปรเจกต์ Python web app, focus security",
    provider="openrouter",           # <-- เปลี่ยน provider
    model="anthropic/claude-sonnet-4",  # <-- เปลี่ยน model
    toolsets=["terminal", "file"]
)
```

### ระดับ 2: `hermes chat -q` subprocess
- Spawn Hermes instance ใหม่เป็น subprocess
- เลือก model/provider ต่างกัน per task
- เหมาะสำหรับงานยาว (5-15 นาที)

```bash
hermes chat -q -m "anthropic/claude-sonnet-4" "วิเคราะห์โค้ดนี้..."
hermes chat -q -m "moonshot/kimi-k2.6" "เขียน tests..."
```

### ระดับ 3: tmux interactive PTY
- Spawn Hermes instance แบบ interactive
- เหมาะสำหรับงานยาวมาก (ชั่วโมง+)
- ตรวจสอบ progress ได้ระหว่างทาง

```bash
tmux new-session -d -s agent1 'hermes -p coding'
tmux send-keys -t agent1 'Build REST API' Enter
```

## Orchestration Patterns

### Pattern 1: Fan-Out (วิเคราะห์ขนาน)
ส่ง task เดียวกันให้หลาย sub-agents ด้วย model ต่างกัน แล้วเปรียบเทียบผล

```
Hermes → delegate_task (Claude)  → วิเคราะห์ A
       → delegate_task (Gemini)  → วิเคราะห์ B
       → delegate_task (Kimi)    → วิเคราะห์ C
       → รวม 3 ผล → consensus report
```

### Pattern 2: Pipeline (ลำดับขั้น)
งานที่ output ของขั้นก่อนเป็น input ของขั้นถัดไป

```
Hermes → subagent A: อ่าน requirements + design
       → subagent B: เขียนโค้ดตาม design
       → subagent C: เขียน tests + review
       → รวมผล → final deliverable
```

### Pattern 3: Map-Reduce (แบ่งงาน → รวม)
แบ่งข้อมูลชิ้นใหญ่เป็นส่วนย่อย ส่งให้ sub-agents ประมวลผล แล้วรวม

```
ข้อมูล: ไฟล์ 10 ไฟล์
Hermes → subagent A: วิเคราะห์ไฟล์ 1-3
       → subagent B: วิเคราะห์ไฟล์ 4-6
       → subagent C: วิเคราะห์ไฟล์ 7-10
       → รวม → summary report
```

### Pattern 4: Critic Loop (ตรวจ-แก้)
sub-agent หนึ่งทำงาน อีกตัวตรวจ แล้ววนแก้จนผ่าน

```
Hermes → subagent A: เขียนโค้ด
       → subagent B: review + หา bugs
 ถ้ามี bugs → subagent A: แก้ตาม feedback
             → subagent B: review อีกรอบ
 วนจนไม่มี bugs → final
```

## การเลือก Sub-Agent ตามงาน

| งาน | Sub-Agent แนะนำ | เหตุผล |
|-----|----------------|--------|
| วิเคราะห์โค้ด | delegate_task (Claude) | reasoning เก่ง |
| เขียนโค้ดเร็ว | delegate_task (deepseek) | cost-effective |
| เขียน tests | delegate_task (Sonnet) | ละเอียด |
| Research/web | hermes subprocess + web tools | มี browser, search |
| งานยาว/ซับซ้อน | tmux interactive | ตรวจสอบ progress ได้ |
| ตรวจสอบคุณภาพ | delegate_task (Opus) | critic เก่ง |

## Provider Override Quick Reference

ส่ง subagent ไป provider อื่นโดยระบุ `provider` + `model`:

```python
delegate_task(goal="...", provider="openrouter", model="google/gemini-2.5-pro")
delegate_task(goal="...", provider="openrouter", model="anthropic/claude-sonnet-4")
delegate_task(goal="...", provider="gemini", model="gemini-2.5-pro")
delegate_task(goal="...", provider="kimi-coding", model="kimi-for-coding")
```

## Token Distribution Strategy (Avoid Rate Limits)

When the parent model has strict rate limits (e.g., Kimi 5-hour cooldown), distribute token usage across providers:

```yaml
# ~/.hermes/config.yaml
delegation:
  model: google/gemini-2.5-flash-preview:free   # subagent default (free)
  provider: openrouter
  max_concurrent_children: 3
  max_iterations: 50
  fallback_providers:
    - provider: openrouter
      model: huggingfaceh4/zephyr-7b-beta:free  # fallback tier 1
      base_url: https://openrouter.ai/api/v1
      api_key: ${OPENROUTER_API_KEY}
    - provider: openrouter
      model: deepseek/deepseek-chat:free         # fallback tier 2
      base_url: https://openrouter.ai/api/v1
      api_key: ${OPENROUTER_API_KEY}
```

**Result:** Parent uses Kimi for complex work, subagents use free tiers — Kimi limit resets slower.

### Provider Tiers for Token Distribution

| Tier | Provider | Cost | Speed | Quality | Use For |
|------|----------|------|-------|---------|---------|
| **Parent** | Kimi / Claude | Paid | Fast | High | Complex reasoning, coding |
| **Subagent default** | OpenRouter/Gemini free | Free | Medium | Medium | General tasks, research |
| **Fallback 1** | OpenRouter/DeepSeek free | Free | Slow | Medium | Backup when Gemini hits limit |
| **Fallback 2** | HF Pro ($2/day) | Free* | Slow | Low | Emergency fallback |

*HF Pro requires $9/month subscription for $2/day serverless inference quota.

### Auto-Delegate Guidance Injection

To make Hermes spawn subagents **automatically** without explicit user commands, inject guidance into the system prompt:

**1. Add guidance constant in `agent/prompt_builder.py`:**
```python
DELEGATION_GUIDANCE = (
    "You have access to delegate_task — spawn parallel subagents to offload work. "
    "Use it automatically when:\n"
    "- The task has 2+ independent parts that can run in parallel\n"
    "- A subtask is reasoning-heavy and would flood your context with intermediate data\n"
    "- You need to research multiple topics simultaneously\n"
    "- You need to verify your own work by having another agent review it\n"
    "- The task involves file operations across multiple directories\n"
    "Do NOT delegate for: single-step work, trivial tasks, or re-delegating your entire goal.\n"
    "When delegating, pass clear goals and relevant context. Subagents use OpenRouter/Gemini by default."
)
```

**2. Import and hook in `run_agent.py`:**
```python
from agent.prompt_builder import (
    # ... existing imports ...
    DELEGATION_GUIDANCE,
)

# In _build_system_prompt():
if "delegate_task" in self.valid_tool_names:
    tool_guidance.append(DELEGATION_GUIDANCE)
```

**3. Restart Hermes** — guidance now injected automatically when `delegate_task` tool is available.

**Result:** Hermes auto-detects parallelizable work and spawns subagents without user explicitly asking.

### ACP CLI Transport (Claude Code, Codex, OpenCode)

ใช้ CLI tool เป็น subagent ผ่าน ACP protocol:

```python
delegate_task(
    goal="Refactor this function",
    acp_command="claude",           # หรือ "codex", "opencode"
    acp_args=["--acp", "--stdio"],
    provider="copilot-acp",
    toolsets=["terminal", "file"]
)
```

### Credential Inheritance

Subagent inherit API key จาก parent โดยอัตโนมัติ ไม่ต้องส่ง `api_key` เอง ยกเว้นต้องการ override จริงๆ

### Config สำหรับ Delegation

```yaml
# ~/.hermes/config.yaml
delegation:
  max_concurrent_children: 3      # จำนวน subagent พร้อมกัน
  max_iterations: 50              # iteration limit ต่อ subagent
  max_spawn_depth: 2              # ความลึกของ spawn tree
  orchestrator_enabled: true      # เปิดให้ subagent spawn ลูกได้
  subagent_auto_approve: false    # auto-approve dangerous commands
  provider: null                  # default provider สำหรับ subagent
  model: null                     # default model สำหรับ subagent
```

### Depth and Role Rules

- `role="leaf"` (default) — ทำงานเอง ไม่ spawn ลูก
- `role="orchestrator"` — สามารถ spawn subagent ลูกได้
- Grandchildren ของ orchestrator ต้องเป็น leaf เสมอ
- ถ้า `child_depth >= max_spawn_depth` จะถูก force เป็น leaf

## เทคนิค Orchestrator

1. **เขียน goal ให้ชัดเจน** — sub-agent ไม่เห็น context ของ parent
2. **ส่ง context ที่จำเป็น** — file paths, error messages, constraints
3. **จำกัด toolsets** — ให้เฉพาะสิ่งที่จำเป็น ลด overhead
4. **ใช้ parallel ให้คุ้ม** — 3 tasks พร้อมกัน = 3x เร็วขึ้น
5. **รวมผลอย่างมีโครงสร้าง** — ให้ sub-agents output เป็น format ที่รวมง่าย

## ตัวอย่างจริง

### วิเคราะห์โปรเจกต์
```
orchestrator goal:
  "วิเคราะห์ ~/myapp 3 ด้าน
   1. delegate_task: architecture review (toolsets: file)
   2. delegate_task: security scan (toolsets: terminal, file)
   3. delegate_task: code quality (toolsets: file)
   รวม 3 report เป็น dashboard"
```

### พัฒนาฟีเจอร์
```
orchestrator goal:
  "สร้าง auth system
   1. delegate_task: design schema + API (toolsets: file)
   2. delegate_task: implement endpoints (toolsets: terminal, file)
   3. delegate_task: write tests (toolsets: terminal, file)
   รวม code + tests + docs"
```

## ข้อควรระวัง

- **delegate_task ไม่เห็น conversation ปัจจุบัน** — ต้องส่ง context เอง
- **sub-agent ไม่มี memory** — ต้องส่ง state ทั้งหมดที่จำเป็น
- **max_iterations** — ตั้งให้พอดีกับงาน (default 50)
- **token cost** — 3 tasks = 3x cost ใช้ smart routing ถ้า concern
