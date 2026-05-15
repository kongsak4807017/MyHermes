---
name: openclaw-learnings
description: วิเคราะห์ OpenClaw 2026.4.20-beta.1 release และแนวทางการพัฒนา Hermes Agent ให้ "นิ่งขึ้น" ทั้งระบบ — ครอบคลุม prompt quality, session stability, cost visibility, provider consistency, และ security hardening พร้อม mapping ไปยัง Hermes features ที่สอดคล้อง
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [openclaw, agent-framework, self-hosted, stability, cost-management, prompt-quality, security]
    homepage: https://github.com/openclaw/openclaw/releases/tag/v2026.4.20-beta.1
    related_skills: [hermes-agent, token-management-subagent]
---

# OpenClaw 2026.4.20-beta.1 — Lessons for Hermes Agent

release นี้ไม่ใช่ "ฟีเจอร์โชว์" แต่เป็น "ระบบนิ่งขึ้น" — ทำให้ agent ใช้งานได้จริงในระยะยาว

## 7 แกนหลักจาก OpenClaw และ mapping ไปยัง Hermes

### 1. Agent Prompt และ Decision Making

**สิ่งที่ OpenClaw ทำ:**
- ปรับ default system prompt ให้มี completion bias ชัดเจนขึ้น
- GPT-5 overlay: live-state checking ดีขึ้น, ฟื้นตัวจาก weak results, verify ก่อนตอบสุดท้าย
- เป้าหมาย: ไม่ใช่แค่ "ตอบได้" แต่ "ตอบได้ครบ ตรง ไว้ใจได้"

**Hermes implementation:**
- ระบบ prompt ของ Hermes อยู่ใน `agent/prompt_builder.py` — สามารถปรับ system prompt ให้เน้น verification ได้
- ใช้ `/reasoning [level]` (none|minimal|low|medium|high|xhigh) เพื่อควบคุม depth
- ใช้ `delegate_task` ให้ subagent ตรวจสอบคำตอบก่อนส่งสุดท้าย (self-critique pattern)
- เปิด `display.show_reasoning: true` เพื่อให้เห็น reasoning trace

**การปรับปรุงที่แนะนำ:**
```yaml
# ใน config.yaml เพิ่ม verification step ก่อนตอบสุดท้าย
agent:
  verification_mode: self_check  # หรือ delegate_critic
  max_verification_rounds: 2
```

### 2. Model Cost Visibility และ Tiered Pricing

**สิ่งที่ OpenClaw ทำ:**
- รองรับ tiered model pricing จาก cached catalogs
- เพิ่ม cost estimate ของ Moonshot Kimi K2.6/K2.5 ใน token-usage reports
- ตอบคำถาม "แพงแค่ไหน? คุมต้นทุนได้ไหม? ดู usage ตรงหรือเปล่า?"

**Hermes implementation:**
- เปิด `display.show_cost: true` ใน config.yaml
- ใช้ `smart_model_routing.enabled: true` เพื่อ route งานยากไป paid model, งานง่ายไป cheap model
- ใช้ skill `token-management-subagent` สำหรับการบริหาร cost
- คำสั่ง `/usage` และ `hermes insights --days N` สำหรับติดตาม consumption

**การตั้งค่าที่แนะนำ:**
```yaml
display:
  show_cost: true
  show_token_usage: true
smart_model_routing:
  enabled: true
  cheap_model: openrouter/deepseek/deepseek-chat
  expensive_model: anthropic/claude-sonnet-4
  threshold_tokens: 2000
```

### 3. Session Stability และ Maintenance

**สิ่งที่ OpenClaw ทำ:**
- บังคับใช้ built-in entry cap และ age prune เป็นค่าเริ่มต้น
- Prune store ที่ใหญ่เกินตอนโหลด ป้องกัน OOM จาก cron/executor backlog
- ระบบพร้อมวิ่งยาว ๆ มากขึ้น

**Hermes implementation:**
- Session store อยู่ใน `hermes_state.py` (SQLite + FTS5)
- `compression.enabled: true` ด้วย threshold 0.50 และ target_ratio 0.20
- รัน `hermes sessions prune --older-than N days` เป็นประจำ
- ตั้ง cron job สำหรับ cleanup อัตโนมัติ

**การตั้งค่าที่แนะนำ:**
```yaml
compression:
  enabled: true
  threshold: 0.50
  target_ratio: 0.20
session_store:
  max_entries: 1000
  auto_prune_age_days: 30
  max_size_mb: 500
```

### 4. Moonshot / Kimi Integration

**สิ่งที่ OpenClaw ทำ:**
- ใช้ `kimi-k2.6` เป็นค่าเริ่มต้นสำหรับ web search และ media-understanding
- ยังคง `kimi-k2.5` ไว้สำหรับ compatibility
- `thinking.keep = "all"` ใช้ได้กับ kimi-k2.6 แต่ strip ออกสำหรับรุ่นอื่นหรือ pinned tool_choice

**Hermes implementation:**
- Hermes รองรับ Moonshot/Kimi ผ่าน provider configuration
- ตั้ง moonshot/kimi-k2.6 เป็น default สำหรับงานเฉพาะทาง
- ระวังเรื่องการ pin tool_choice ที่อาจ strip thinking tokens

**การตั้งค่าที่แนะนำ:**
```yaml
model:
  default: anthropic/claude-sonnet-4
  fallback_models:
    - moonshot/kimi-k2.6
    - openrouter/deepseek/deepseek-chat
reasoning:
  thinking_mode: auto  # auto-strip สำหรับ non-thinking models
```

### 5. OpenAI / Codex Transport Consistency

**สิ่งที่ OpenClaw ทำ:**
- Normalize legacy `openai-completions` กลับไปใช้ native Codex Responses transport
- แก้ provider ที่ไม่ใช่ Anthropic ถูก rewrite transport ผิด
- `/think` resolve ตรงกับ reasoning efforts ที่ GPT รองรับจริง

**Hermes implementation:**
- Hermes ใช้ `model_tools.py` สำหรับ tool discovery และ dispatch
- ตรวจสอบ provider routing ว่าไม่มีการ rewrite transport ผิด
- ใช้ native responses API สำหรับ OpenAI/Codex

**การตรวจสอบที่แนะนำ:**
- ทดสอบ switching providers ด้วย `/model` — ตรวจสอบว่า tool usage เหมือนกัน
- ตรวจสอบ `model_tools.py` ว่า provider mapping ถูกต้อง
- ใช้ `hermes doctor` เพื่อตรวจสอบ provider configuration

### 6. Operator Experience Enhancements

**สิ่งที่ OpenClaw ทำ:**
- Onboarding wizard อ่าน security disclaimer ง่ายขึ้น
- Loading spinner ตอน model catalog โหลดครั้งแรก
- แยก cron runtime state ไป `jobs-state.json` (stable jobs.json สำหรับ Git)
- Notice ตอนเริ่ม/จบ context compaction
- Detached executors จัด lifecycle และ cancellation ชัดขึ้น

**Hermes implementation:**
- Hermes มี setup wizard (`hermes setup`) — ปรับปรุง security disclaimer ได้
- Spinner system อยู่ใน `agent/display.py` (KawaiiSpinner)
- Cron jobs ใช้ `cronjob` tool — สามารถแยกรuntime state ได้
- Context compaction สามารถเพิ่ม notice ได้ใน `run_agent.py`

**ฟีเจอร์ที่ Hermes มีอยู่แล้ว:**
- Skin engine สำหรับปรับหน้าตา (`display.skin`)
- Tool preview system แสดงก่อนเรียก tool
- Background process management ผ่าน `process` tool

### 7. Security และ Reliability Hardening

**สิ่งที่ OpenClaw ทำ:**
- SSRF guard ใน upload paths
- `allowRequestSessionKey` gate สำหรับ template-rendered sessionKeys
- Webchat image handling gating ถูกต้องขึ้น
- Cost usage cache จำกัดด้วย FIFO eviction

**Hermes implementation:**
- Browser tool (`browser_tool.py`) ควรมี SSRF protection
- Credential pooling (`auth.json`) — ต้อง enforce session key gate
- Tool approval system สำหรับ dangerous commands
- Cache management ต้องมี eviction policy

**การตั้งค่าที่แนะนำ:**
```yaml
security:
  tirith_enabled: true
  ssrf_protection: true
  max_tool_iterations: 50
  cache_eviction: fifo
  max_cache_size_mb: 100
```

## OMK — Operational Monitoring & Knowledge

OMK ในที่นี้หมายถึง **การติดตามและบันทึก operational knowledge** สำหรับระบบ agent:

### สิ่งที่ต้อง monitor
1. **Token usage** — `/usage`, `hermes insights`
2. **Session health** — ขนาด session store, compression ratio
3. **Model performance** — response time, tool success rate, cost per task
4. **Error rates** — failed tool calls, provider timeouts, OOM events

### สิ่งที่ต้องบันทึก
1. **System prompt versions** — เก็บ history ของการปรับ prompt
2. **Model routing decisions** — log ว่างานไหน route ไป model ไหน
3. **Session pruning events** — เมื่อไหร่ prune, ลบไปกี่ entries
4. **Security events** — blocked SSRF attempts, failed auth

### Dashboard ที่แนะนำ
```bash
#!/bin/bash
echo "=== Hermes Operational Dashboard ==="
echo "Sessions: $(hermes sessions stats | grep total)"
echo "Cost today: $(hermes insights --days 1 | grep cost)"
echo "Skills loaded: $(hermes skills list | wc -l)"
echo "Cron jobs: $(hermes cron list | wc -l)"
echo "Disk usage: $(du -sh ~/.hermes/)"
```

## Best Practices Summary

1. **Stability เหนือฟีเจอร์** — agent ที่ responsive ต่อเนื่อง ชั่วโมง/วัน สำคัญกว่า occasional impressive output
2. **Cost transparency** — user ต้องเห็น token usage และค่าใช้จ่ายชัดเจน
3. **Design for verification** — มี mechanism ให้ agent ตรวจสอบงานตัวเองก่อนตอบ
4. **Plan for long runs** — assume agent จะใช้ยาว — implement pruning, archiving, cleanup
5. **Hardening เป็น ongoing** — security และ reliability ไม่ใช่ one-time check
6. **Learn from sibling projects** — ดู OpenClaw และ frameworks อื่น เพื่อไอเดียที่ดีขึ้น

## Checklist สำหรับ Hermes Operators

- [ ] เปิด `display.show_cost: true`
- [ ] ตั้ง `compression.enabled: true`
- [ ] รัน `hermes sessions prune` เป็นประจำ (หรือตั้ง cron)
- [ ] ตรวจสอบ provider mapping ด้วย `hermes doctor`
- [ ] เปิด `smart_model_routing` ถ้าใช้หลาย models
- [ ] ตั้ง security limits (max iterations, cache size)
- [ ] สร้าง monitoring script สำหรับ daily checks
- [ ] บันทึก system prompt changes ใน Git
- [ ] ทดสอบ switching providers เป็นประจำ
- [ ] review session logs สำหรับ errors

## References

- OpenClaw 2026.4.20-beta.1: https://github.com/openclaw/openclaw/releases/tag/v2026.4.20-beta.1
- Hermes Agent docs: https://hermes-agent.nousresearch.com/docs/
- Skills list: `hermes skills list`
- Config reference: `hermes config edit`
