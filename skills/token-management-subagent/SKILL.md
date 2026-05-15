---
name: token-management-subagent
description: บริหาร token/cost โดยใช้โมเดลหลักหรือ paid model เฉพาะงานยาก และใช้ free/cheap subAgent สำหรับงานย่อยตรงไปตรงมาและการตรวจงาน
category: productivity
version: 1.0.0
metadata:
  hermes:
    tags: [token-management, cost-control, subagent, verification, ralph-lite]
---

# Token Management SubAgent

ใช้ skill นี้เมื่อผู้ใช้ขอให้ทำงานแบบประหยัด token/cost, ใช้ subAgent, ตรวจงานซ้ำ, ทำงานแบบ Ralph-lite, หรือเมื่อ task มีหลายช่วงที่แยกเป็นงานง่ายได้

## เป้าหมาย

ลดค่าใช้จ่ายและ token โดยให้โมเดลหลักทำเฉพาะงานที่ต้องใช้ reasoning สูง ส่วนงานที่ชัดเจน ตรงไปตรงมา ตรวจซ้ำได้ หรือสรุป evidence ให้ใช้ free/cheap model ผ่าน subAgent แทน

## หลักการตัดสินใจ

1. ใช้โมเดลหลักหรือ paid model เมื่อ:
   - requirement ยังคลุมเครือ
   - ต้องออกแบบ architecture, debugging ยาก, security, migration, data loss risk
   - ต้องตัดสินใจ tradeoff สำคัญ
   - ต้องแก้ conflict หรือ integrate หลายส่วน

2. ใช้ free/cheap subAgent เมื่อ:
   - งานถูกย่อยจน deterministic แล้ว
   - งานเป็น read-only inspection, grep/search, summarize logs, check checklist
   - งานเป็น verification หลัง implementation
   - งานมีขอบเขตไฟล์ชัดเจนและไม่ต้องตัดสินใจ product/architecture ใหม่

3. หลีกเลี่ยงการส่ง context ก้อนใหญ่ให้ subAgent:
   - ส่งเฉพาะ goal, file paths, expected output, และ acceptance criteria
   - ให้ subAgent อ่านไฟล์เองจาก workspace แทนการ paste เนื้อหายาว
   - จำกัด output เป็น findings/evidence ไม่ใช่ essay

## Workflow

### Phase 1: Classify

ก่อนเริ่มงาน ให้จัดประเภท task:

- `hard`: ใช้โมเดลหลักทำเอง
- `medium`: โมเดลหลักวางแผน แล้ว delegate งานย่อยที่ชัดเจน
- `easy`: ใช้ free/cheap subAgent ได้ถ้ามี tool/model พร้อม

ถ้าไม่แน่ใจ ให้โมเดลหลักทำส่วนที่เสี่ยงก่อน แล้วค่อย delegate ส่วนตรวจสอบ

### Phase 2: Minimize Context

ก่อนเรียก subAgent ให้สรุป brief ให้สั้น:

```text
Task:
Check whether <specific claim/change> is correct.

Scope:
- Files: <paths>
- Do not edit files unless explicitly instructed.

Acceptance criteria:
- <criterion 1>
- <criterion 2>

Return:
- PASS/FAIL
- Findings with file/line evidence
- Commands/tests run
```

### Phase 3: Execute With Budget

ใช้ลำดับนี้:

1. โมเดลหลักทำ plan และงาน reasoning-heavy
2. ถ้ามีงานย่อยอิสระ ให้ส่งให้ subAgent ด้วย model free/cheap
3. โมเดลหลักไม่ทำงานซ้ำกับ subAgent ระหว่างรอ ยกเว้นงานคนละ scope
4. เมื่อ subAgent กลับมา ให้ตรวจเฉพาะ evidence และ integrate ผล

### Phase 4: Ralph-Lite Verification

หลังงานสำคัญทุกครั้ง ให้ทำ verifier pass แบบประหยัด:

1. สร้าง checklist จาก requirement เดิม
2. ให้ free/cheap subAgent ตรวจว่า implementation ตรง checklist หรือไม่
3. verifier ต้องรายงาน:
   - `PASS` หรือ `FAIL`
   - missing requirement
   - regression risk
   - tests/commands ที่ควรรันเพิ่ม
4. โมเดลหลักต้องอ่านผล verifier แล้วตัดสินใจเอง ไม่ blindly trust

ถ้าไม่มี subAgent/model free พร้อม ให้ทำ verifier pass ด้วยตัวเองแบบสั้น และบอกผู้ใช้ว่าไม่ได้ใช้ subAgent เพราะ tool/model ไม่พร้อม

## Output Contract

เวลารายงานผู้ใช้ ให้รวมเฉพาะ:

- ทำอะไรแล้ว
- ใช้ paid/free model ตรงไหนถ้ามี
- verification ผ่านไหม
- เหลือ risk อะไร

อย่ารายงาน reasoning ยาวหรือ transcript ของ subAgent เว้นแต่ผู้ใช้ขอ

## Pitfalls

- อย่าส่งทั้ง repository หรือ log ยาวให้ subAgent ถ้าให้มันค้นเองได้
- อย่าใช้ free model กับงานที่ต้องตัดสินใจ irreversible หรือ security-sensitive
- อย่าให้ subAgent แก้ไฟล์เดียวกับโมเดลหลักพร้อมกันถ้าไม่แบ่ง write scope ชัดเจน
- อย่าถือว่า skill ถูกโหลดทันทีใน conversation เดิมเสมอไป ถ้าเพิ่งแก้ skill ให้เริ่ม session ใหม่หรือ reload skills ถ้ามีคำสั่งรองรับ

## Verification Checklist

ก่อนจบงาน ให้ตอบตัวเอง:

- งานถูกแบ่งเป็น hard/easy แล้วหรือยัง
- มีส่วนที่ delegate ได้โดยไม่เพิ่ม token เกินจำเป็นหรือไม่
- มี verifier pass แล้วหรือยัง
- evidence มาจากไฟล์/คำสั่งจริงหรือไม่
- final answer สั้นพอและไม่มี transcript เกินจำเป็นหรือไม่
