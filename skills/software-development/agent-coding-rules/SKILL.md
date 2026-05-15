---
name: agent-coding-rules
description: Behavioral coding rules for AI agents working on OMK, Hermes, and similar Python CLI projects. Reduces over-engineering, prevents scope creep, and enforces surgical changes.
title: Agent Coding Rules — Karpathy-Inspired Behavioral Guidelines
version: 1.0.0
summary: Four core rules — Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution — with OMK/Hermes-specific examples and pre-flight checklists.
alwaysApply: true
---

# Agent Coding Rules

Behavioral guidelines สำหรับ AI agent ที่ทำงานบน OMK CLI, Hermes Agent, และโปรเจค Python CLI ทั่วไป

**Tradeoff:** เน้นความระมัดระวังมากกว่าความเร็ว สำหรับงาน trivial ให้ใช้วิจารณญาณ

---

## Rule 1: Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

ก่อน implement:
- State assumptions ให้ชัดเจน ถ้าไม่แน่ใจ ให้ถาม
- ถ้ามีหลาย interpretation เสนอมา อย่าเลือกเงียบๆ
- ถ้ามีวิธีง่ายกว่า ให้บอก Push back เมื่อจำเป็น
- ถ้ามีอะไรไม่ชัดเจน หยุด บอกว่าอะไร confusing แล้วถาม

### OMK/Hermes Example

ผู้ใช้บอก "แก้ metrics.py ให้แสดง cost ถูกต้อง"

**Wrong:** เปิดไฟล์แล้วแก้ `estimated_cost_usd` ตรงๆ โดยไม่เช็ค schema

**Right:**
```
Assumptions:
1. state.db ใช้ REAL Unix timestamps (ไม่ใช่ ISO string)
2. ฟิลด์ cost อยู่ใน sessions table
3. มี test coverage อยู่แล้ว

คำถาม:
- cutoff time ต้องเป็น float หรือ datetime object?
- ต้อง handle timezone ไหม?
- อยากให้แสดง cost แยกตาม provider หรือรวม?
```

---

## Rule 2: Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- ไม่เพิ่ม feature นอกเหนือจากที่ขอ
- ไม่สร้าง abstraction สำหรับ code ที่ใช้ครั้งเดียว
- ไม่เพิ่ม "flexibility" หรือ "configurability" ที่ไม่ได้ขอ
- ไม่ handle error สำหรับ scenario ที่เป็นไปไม่ได้
- ถ้าเขียน 200 บรรทัด แต่ทำได้ใน 50 บรรทัด ให้ rewrite

ถามตัวเอง: "Senior engineer จะบอกว่า overcomplicated ไหม?" ถ้าใช่ ให้ simplify

### OMK/Hermes Example

**Wrong:**
```python
class AbstractMetricsProvider(ABC):
    @abstractmethod
    def get_cost(self): ...

class SqliteMetricsProvider(AbstractMetricsProvider):
    def get_cost(self): ...

class PostgresMetricsProvider(AbstractMetricsProvider):
    def get_cost(self): ...
```

**Right:**
```python
def get_session_cost(cursor, since: float) -> float:
    cursor.execute(
        "SELECT COALESCE(SUM(estimated_cost_usd), 0.0) FROM sessions WHERE started_at > ?",
        (since,)
    )
    return cursor.fetchone()[0]
```

---

## Rule 3: Surgical Changes

**Touch only what you must. Clean up only your own mess.**

เมื่อแก้ code ที่มีอยู่:
- อย่า "ปรับปรุง" code ข้างเคียง, comments, หรือ formatting
- อย่า refactor ของที่ไม่เสีย
- ให้ match style ที่มีอยู่ ถึงจะทำต่างก็ตาม
- ถ้าเห็น dead code ที่ไม่เกี่ยวข้อง ให้ mention ไว้ อย่าลบ

เมื่อ changes ของคุณสร้าง orphans:
- ลบ imports/variables/functions ที่ YOUR changes ทำให้ unused
- อย่าลบ pre-existing dead code ถ้าไม่ได้ถูกขอ

**The test:** ทุกบรรทัดที่เปลี่ยน ต้อง trace กลับไปหา user request ได้โดยตรง

### OMK/Hermes Example

**Wrong:**
```diff
 def get_metrics(cursor, days=7):
+    # TODO: refactor this later
+    import datetime
     cutoff = time.time() - (days * 86400)
-    cursor.execute("SELECT * FROM sessions WHERE started_at > ?", (cutoff,))
+    cursor.execute("SELECT * FROM sessions WHERE started_at > ? ORDER BY started_at DESC", (cutoff,))
     return cursor.fetchall()
+
+# New helper function for future use
+def format_metrics(metrics):
+    return [dict(row) for row in metrics]
```

**Right:**
```diff
 def get_metrics(cursor, days=7):
     cutoff = time.time() - (days * 86400)
     cursor.execute("SELECT * FROM sessions WHERE started_at > ?", (cutoff,))
     return cursor.fetchall()
```

---

## Rule 4: Goal-Driven Execution

**Define success criteria. Loop until verified.**

แปลง task ให้เป็น verifiable goals:
- "Add validation" → "Write tests สำหรับ invalid inputs, แล้วทำให้ผ่าน"
- "Fix the bug" → "Write test ที่ reproduce bug, แล้วทำให้ผ่าน"
- "Refactor X" → "Ensure tests ผ่านก่อนและหลัง"

สำหรับ multi-step tasks ให้วางแผนสั้นๆ:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Success criteria ที่ strong จะทำให้ loop ได้ independently ส่วน weak criteria ("make it work") ต้องขอ clarification ตลอด

### OMK/Hermes Example

ผู้ใช้บอก "เพิ่ม provider routing ให้ OMKAgent"

**Weak plan:**
```
1. แก้ OMKAgent
2. Test ว่าใช้ได้
```

**Strong plan:**
```
1. Read omk/agent/core.py _init_provider() → verify: เข้าใจ flow เดิม
2. Patch _init_provider() ส่ง provider/model ให้ create_client() → verify: pytest tests/test_agent.py ผ่าน
3. Test with real API: omk run --provider kimi --prompt "hi" → verify: ได้ response จริง
4. Test with real API: omk run --provider openrouter --prompt "hi" → verify: ได้ response จริง
5. Run full suite: pytest tests/ -q → verify: 53 passed
```

---

## Pre-Flight Checklist

ก่อนเริ่มเขียน/แก้ code:

- [ ] อ่าน AGENTS.md / SKILL.md ที่เกี่ยวข้องก่อน
- [ ] เข้าใจ schema (เช็ค PRAGMA table_info ถ้าเป็น SQLite)
- [ ] เข้าใจ file dependency chain (อะไร import อะไร)
- [ ] ระบุ assumption แล้วถามถ้าไม่แน่ใจ
- [ ] วางแผน 3-5 steps พร้อม verify criteria
- [ ] ตรวจสอบว่าไม่ได้เพิ่ม abstraction ที่ไม่จำเป็น

---

## Success Criteria Template

สำหรับทุก task ให้กำหนด criteria ตามรูปแบบนี้:

```markdown
### Task: [ชื่อ]

**Goal:** [อะไร]

**Assumptions:**
- [assumption 1]
- [assumption 2]

**Plan:**
1. [Step 1] → verify: [วิธีเช็ค]
2. [Step 2] → verify: [วิธีเช็ค]
3. [Step 3] → verify: [วิธีเช็ค]

**Done when:**
- [ ] Criteria 1
- [ ] Criteria 2
- [ ] Criteria 3
```

---

## Anti-Patterns ที่ต้องหลีกเลี่ง

| Anti-Pattern | ลักษณะ | แก้ไข |
|--------------|--------|--------|
| **Speculative Generality** | สร้าง abstract class สำหรับ use case เดียว | ใช้ function ธรรมดา |
| **Feature Creep** | เพิ่ม feature ที่ไม่ได้ขอ "เผื่ออนาคต" | ทำเฉพาะที่ขอ |
| **Refactoring Tourist** | แก้ไฟล์อื่นที่ไม่เกี่ยวข้อง | Touch เฉพาะที่จำเป็น |
| **Test-less Fix** | แก้ bug โดยไม่เขียน test reproduce | Write test ก่อน |
| **Assumption Silent** | เลือก interpretation เงียบๆ | ถามหรือบอก assumption |
| **Over-engineering** | 200 บรรทัดทำได้ใน 50 | Simplify |

---

## OMK/Hermes Specific Notes

### Schema Assumptions (สิ่งที่มักผิด)
- `state.db` ใช้ **REAL Unix timestamps** ไม่ใช่ ISO string
- Column ชื่อ `source` ไม่ใช่ `platform`
- Session id คือ `session.id` ไม่ใช่ `session.session_id`

### File Dependency Chain
```
tools/registry.py (no deps)
  ↑
tools/*.py (each calls registry.register())
  ↑
model_tools.py / agent/core.py
  ↑
run_agent.py, cli.py, batch_runner.py
```

### Testing
- ใช้ `scripts/run_tests.sh` ไม่ใช่ `pytest` ตรงๆ
- Hermetic environment: credential vars unset, TZ=UTC, LANG=C.UTF-8
- อย่าเขียน change-detector tests (assert specific model name, config version literal)

### Credentials
- อย่า hardcode API keys
- ใช้ `~/.omk/auth.json` (OMK) หรือ `~/.hermes/auth.json` (Hermes)
- Check `OMK_HOME` env var ถ้าใช้ WSL
