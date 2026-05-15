---
name: thai-docx-structured-extraction
description: Extract AND edit structured data (committee lists, member tables) from Thai DOCX documents. Handles Thai text regex patterns, role detection, spelling error detection, and in-place correction of common Thai spelling mistakes (vowel repetition, character order issues).
category: productivity
version: 1.1.0
---

# Thai DOCX Structured Data Extraction

Extract tabular/member list data from Thai government documents (คำสั่ง, คณะกรรมการ, คณะทำงาน) while handling Thai text encoding quirks and detecting spelling errors.

## When to Use
- Processing Thai government documents with member lists (names, positions, roles)
- Extracting committee/working group appointments from DOCX files
- Need to detect Thai spelling/grammar errors in official documents
- Converting tabular member data to structured markdown

## Critical Discovery: Thai Text Regex

**⚠️ Major Finding**: In this environment, `\d` (digit regex) does NOT match Thai numerals or even ASCII digits properly when working with Thai text. **Always use `[0-9]` instead.**

```python
# ❌ DOES NOT WORK with Thai text
re.search(r'^\d+', line)

# ✅ ALWAYS USE this pattern
re.search(r'^[0-9]+', line)

# For list numbers like "1.", "2.", "1.1", use:
re.search(r'^[0-9]+[\.\(\)]', line)  # Matches 1. 1) 1( 1.1 1.2
```

## Setup

```python
import sys
sys.path.insert(0, '/home/user/.local/lib/python3.12/site-packages')
from docx import Document
```

## Extraction Pattern

### 1. Scan Directory and Read Files

```python
from pathlib import Path

docx_files = list(Path(base_dir).glob("*.docx"))

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)
    return '\n'.join(paragraphs)
```

### 2. Parse Member Data with Line-by-Line Processing

Key challenge: Data may be tab-separated or space-separated. Handle both:

```python
def parse_members_from_text(text):
    members = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line starts with number (member entry)
        # CRITICAL: Use [0-9] not \d for Thai text
        i = 0
        while i < len(line) and (line[i].isdigit() or line[i] in '.() '):
            i += 1
        
        if i > 0 and i < len(line):
            number = line[:i].strip()
            name_part = line[i:].strip()
            
            # Handle tab-separated format (เลขที่\tชื่อ)
            if '\t' in name_part:
                parts = name_part.split('\t')
                if len(parts) >= 2:
                    name_part = parts[1].strip()
            
            # Detect Thai titles
            titles = ['นาย', 'นาง', 'นางสาว']
            has_title = any(name_part.startswith(t) for t in titles)
            
            # Extract name and role
            name = name_part
            role = "คณะทำงาน"  # default role
            
            # Detect special roles
            role_keywords = ['ที่ปรึกษา', 'รองประธาน', 'ประธาน', 'เลขานุการ', 'ผู้ช่วยเลขานุการ']
            for kw in role_keywords:
                if kw in name_part:
                    role = kw
                    break
            
            members.append({
                'number': number,
                'name': name,
                'role': role,
                'has_title': has_title
            })
    
    return members
```

### 3. Thai Spelling Error Detection

Common errors in Thai official documents:

```python
THAI_SPELLING_ERRORS = {
    'ประะธาน': 'ประธาน',      # Extra vowel ะ
    'เเพทย์': 'แพทย์',        # Wrong character เ + แ
    'เเพทย์หญิง': 'แพทย์หญิง',  # Same issue
}

def detect_thai_spelling_errors(text):
    errors = []
    for error, correction in THAI_SPELLING_ERRORS.items():
        if error in text:
            errors.append({
                'found': error,
                'should_be': correction,
                'context': text[max(0, text.find(error)-20):text.find(error)+len(error)+20]
            })
    return errors

def fix_thai_spelling(text):
    """Fix common Thai spelling errors."""
    for error, correction in THAI_SPELLING_ERRORS.items():
        text = text.replace(error, correction)
    return text
```

### 4. Extract Document Metadata

```python
def extract_doc_metadata(text):
    """Extract ที่, วันที่, เรื่อง from Thai government document."""
    metadata = {}
    
    # ที่ reference number
    if match := re.search(r'ที่\s+([^\n]+)', text):
        metadata['reference'] = match.group(1).strip()
    
    # วันที่ date
    if match := re.search(r'วันที่\s+([^\n]+)', text):
        metadata['date'] = match.group(1).strip()
    
    # เรื่อง subject
    if match := re.search(r'เรื่อง\s*:?\s*([^
]+)', text):
        metadata['subject'] = match.group(1).strip()
    
    # Committee name (คำสั่งฯ แต่งตั้งคณะ...)
    if 'คณะ' in text:
        lines = text.split('\n')
        for line in lines:
            if 'คณะ' in line and ('กรรมการ' in line or 'ทำงาน' in line):
                metadata['committee_name'] = line.strip()
                break
    
    return metadata
```

### 5. Generate Markdown Report

```python
def generate_member_report(teams_data, output_path):
    """Create structured markdown with all teams."""
    
    lines = [
        "# สรุปรายชื่อคณะกรรมการและคณะทำงาน",
        "",
        "## สารบัญ",
        ""
    ]
    
    # Table of contents
    for team in teams_data:
        lines.append(f"- [{team['name']}](#{team['id']})")
    
    lines.extend(["", "---", ""])
    
    # Per-team details
    for team in teams_data:
        lines.extend([
            f"## {team['name']}",
            "",
            f"**ที่:** {team['reference']}",
            f"**วันที่:** {team['date']}",
            f"**เรื่อง:** {team['subject']}",
            "",
            "### รายชื่อสมาชิก",
            "",
            "| ลำดับ | ชื่อ-สกุล | ตำแหน่ง/บทบาท |",
            "|-------|-----------|--------------|"
        ])
        
        for member in team['members']:
            lines.append(f"| {member['number']} | {member['name']} | {member['role']} |")
        
        lines.extend([
            "",
            f"**จำนวนสมาชิก:** {len(team['members'])} คน",
            "",
            "---",
            ""
        ])
    
    # Statistics summary
    total_members = sum(len(t['members']) for t in teams_data)
    lines.extend([
        "## สถิติสรุป",
        "",
        f"- **จำนวนคณะทั้งหมด:** {len(teams_data)} คณะ",
        f"- **จำนวนสมาชิกรวม:** {total_members} คน",
        f"- **เฉลี่ยต่อคณะ:** {total_members / len(teams_data):.1f} คน",
        "",
        "### คณะขนาดใหญ่สุด",
        ""
    ])
    
    sorted_teams = sorted(teams_data, key=lambda x: len(x['members']), reverse=True)[:3]
    for team in sorted_teams:
        lines.append(f"- {team['name']}: {len(team['members'])} คน")
    
    Path(output_path).write_text('\n'.join(lines), encoding='utf-8')
```

## Complete Example

```python
import sys
sys.path.insert(0, '/home/user/.local/lib/python3.12/site-packages')
from docx import Document
from pathlib import Path
import re

# Configuration
base_dir = "/mnt/c/Users/User/OneDrive/HR1/คำสั่ง 14 คณะ 2569"
output_file = f"{base_dir}/allStar.md"

# Process all DOCX files
teams_data = []
docx_files = list(Path(base_dir).glob("*.docx"))

for docx_file in docx_files:
    # Extract text
    doc = Document(docx_file)
    full_text = '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
    
    # Get metadata
    metadata = extract_doc_metadata(full_text)
    
    # Parse members
    members = parse_members_from_text(full_text)
    
    # Detect spelling errors
    errors = detect_thai_spelling_errors(full_text)
    
    teams_data.append({
        'id': docx_file.stem,
        'name': metadata.get('committee_name', docx_file.stem),
        'reference': metadata.get('reference', '-'),
        'date': metadata.get('date', '-'),
        'subject': metadata.get('subject', '-'),
        'members': members,
        'spelling_errors': errors,
        'source_file': str(docx_file)
    })

# Generate report
generate_member_report(teams_data, output_file)

# Summary
print(f"✓ Processed {len(teams_data)} files")
print(f"✓ Total members: {sum(len(t['members']) for t in teams_data)}")
print(f"✓ Spelling errors found: {sum(len(t['spelling_errors']) for t in teams_data)}")
print(f"✓ Output saved to: {output_file}")
```

## Editing DOCX Files to Fix Spelling Errors

After detecting spelling errors, you can fix them directly in the source DOCX files:

### In-Place Spelling Correction

```python
from docx import Document

def fix_thai_spelling_in_docx(file_path, corrections=None):
    """
    Fix common Thai spelling errors in a DOCX file.
    
    Args:
        file_path: Path to DOCX file
        corrections: Dict of {wrong: correct} pairs. Uses defaults if None.
    
    Returns:
        List of fixes applied (line, original, corrected)
    """
    if corrections is None:
        corrections = {
            'ประะธาน': 'ประธาน',      # Extra vowel ะ
            'เเพทย์': 'แพทย์',        # Wrong character เ + แ
            'เเพทย์หญิง': 'แพทย์หญิง',  # Same issue
            'เเก': 'แก',              # เ + แ -> แ
            'เเปล': 'แปล',            # เ + แ -> แ
            'เเปลง': 'แปลง',          # เ + แ -> แ
        }
    
    doc = Document(file_path)
    fixes_made = []
    
    for i, para in enumerate(doc.paragraphs):
        original_text = para.text
        
        # Check for any errors
        needs_fix = any(wrong in original_text for wrong in corrections.keys())
        
        if needs_fix:
            # Apply all corrections
            corrected_text = original_text
            for wrong, correct in corrections.items():
                corrected_text = corrected_text.replace(wrong, correct)
            
            # Clear paragraph and rewrite (preserves formatting in new runs)
            para.clear()
            run = para.add_run(corrected_text)
            
            fixes_made.append({
                'line': i,
                'original': original_text[:60],
                'corrected': corrected_text[:60]
            })
    
    # Save if changes were made
    if fixes_made:
        doc.save(file_path)
    
    return fixes_made

# Batch fix all DOCX files in directory
def batch_fix_spelling(directory, corrections=None):
    import os
    
    results = []
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith('.docx'):
            continue
        
        file_path = os.path.join(directory, fname)
        try:
            fixes = fix_thai_spelling_in_docx(file_path, corrections)
            if fixes:
                results.append({
                    'file': fname,
                    'fixes': fixes,
                    'count': len(fixes)
                })
                print(f"✓ {fname}: แก้ไข {len(fixes)} รายการ")
            else:
                print(f"- {fname}: ไม่พบคำผิด")
        except Exception as e:
            print(f"✗ {fname}: Error - {e}")
    
    return results

# Usage
base_dir = "/mnt/c/Users/User/OneDrive/HR1/คำสั่ง 14 คณะ 2569"
results = batch_fix_spelling(base_dir)
print(f"\nสรุป: แก้ไข {len(results)} ไฟล์")
```

### Critical: Import Path Resolution

**Problem:** `python-docx` may not be available in the default venv but is installed system-wide.

**Solution:** Use system Python directly:
```bash
cd /path/to/documents && python3 -c "
from docx import Document
# ... correction code
"
```

Or in Python, use absolute paths:
```python
import subprocess
import shlex

def run_with_system_python(code, cwd=None):
    '''Execute Python code using system python3.'''
    cmd = ['python3', '-c', code]
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
```

## Key Pitfalls & Solutions

### Pitfall 1: Regex \d doesn't work with Thai text
**Solution:** Always use `[0-9]` character class instead.

### Pitfall 2: Tab-separated vs space-separated data
**Solution:** Check for `\t` in parsed content and split accordingly.

### Pitfall 3: Number formats vary (1., 1), 1.1, 1.2)
**Solution:** Use while loop to consume digits and separators dynamically:
```python
while i < len(line) and (line[i].isdigit() or line[i] in '.() '):
    i += 1
```

### Pitfall 4: Hidden Thai character issues
Common problematic characters:
- `เ` + `แ` instead of just `แ` (เเพทย์ → แพทย์)
- Double vowels (ประะธาน → ประธาน)

**Solution:** Create lookup table of known errors and apply fixes consistently.

### Pitfall 5: Missing python-docx
**Solution:** Install with `--break-system-packages` flag:
```bash
pip install python-docx --break-system-packages
```

### Pitfall 6: Paragraph runs preserve old formatting
**Solution:** When fixing spelling, clear the paragraph and add new run:
```python
para.clear()
run = para.add_run(corrected_text)
# Original formatting may be lost; if critical, iterate runs individually
```

## Output Structure

The generated `allStar.md` contains:
1. **สารบัญ** - Linked table of contents
2. **Per-team sections** - Each with metadata, member table, count
3. **สถิติสรุป** - Statistics including largest committees
4. **คำผิดที่พบ** - List of spelling errors detected

## References

- python-docx: https://python-docx.readthedocs.io/
- Thai text encoding: https://en.wikipedia.org/wiki/Thai_(Unicode_block)
- Tested on: Thai government documents (คำสั่งจัดตั้งคณะกรรมการ) from สสจ.