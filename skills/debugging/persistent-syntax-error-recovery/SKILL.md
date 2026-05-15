---
name: persistent-syntax-error-recovery
title: Recover from Persistent SyntaxError After Failed Patches
description: When repeated patch() calls fail with syntax errors, the file may have accumulated corrupted/duplicate code. Use AST parsing and full rewrite.
trigger: SyntaxError persists after 3+ patch attempts, "unterminated string" errors, duplicate code blocks
tags: [debugging, python, syntax-error, patch-failure]
---

# Recovering from Persistent Syntax Errors

## Problem

After multiple failed `patch()` attempts on a Python file:
- `patch()` keeps failing with "unterminated string literal"
- SyntaxError persists at seemingly random line numbers
- File may have accumulated duplicate code blocks from partial edits

## Solution Workflow

### Step 1: Diagnose with AST

```python
import ast

with open("file.py", "r") as f:
    content = f.read()

try:
    ast.parse(content)
    print("Syntax OK")
except SyntaxError as e:
    print(f"Line {e.lineno}: {e.msg}")
    print(f"Context: {content.splitlines()[e.lineno-1]}")
```

### Step 2: Check for Duplicate Code

```python
# Look for duplicate function definitions or code blocks
lines = content.splitlines()

# Check for odd number of triple-quoted strings
 triple_count = content.count('"""')
print(f"Triple quotes: {triple_count} ({'ODD - problem!' if triple_count % 2 else 'OK'})")

# Find all triple-quote locations
for i, line in enumerate(lines, 1):
    if '"""' in line:
        print(f"  Line {i}: {line.strip()[:60]}")
```

### Step 3: Locate Corrupted Section

Common corruption patterns:
- **Duplicate function bodies** - Same code appears twice
- **Half-completed patches** - Old and new code mixed
- **Missing closing quotes/docstrings**

```python
# Read the problematic area
with open("file.py") as f:
    lines = f.readlines()

# Inspect around error line
for i in range(error_line-5, error_line+5):
    print(f"{i+1}: {repr(lines[i])}")
```

### Step 4: Full Rewrite (When Patching Fails)

If the file is severely corrupted, **rewrite entirely** rather than continue patching:

```python
fixed_content = '''"""Module docstring.

Complete, clean implementation.
"""

# ... full correct code ...

'''

with open("file.py", "w") as f:
    f.write(fixed_content)

# Verify
import ast
ast.parse(fixed_content)
print("Syntax OK")
```

## Prevention

1. **Verify after each patch** in iterative editing:
   ```python
   import ast
   with open(file) as f:
       ast.parse(f.read())  # Ensure valid before next patch
   ```

2. **Use replace mode for complex changes** - Sometimes it's cleaner to rewrite a whole function than patch line-by-line

3. **Read before patching extensively** - Understand the file structure first

## Example: Duplicate Code Blocks (from OMK metrics.py)

**Symptom:** `SyntaxError: unterminated triple-quoted string literal`

**Root Cause:** Multiple patch attempts left duplicate code blocks:
```python
# Lines 73-87 had:
cursor.execute("""
# Recent sessions (last 24h)
cutoff = ...
cursor.execute(...)  # DUPLICATE - should only appear once
```

**Detection:**
```python
# Found 31 triple-quotes (odd number = problem)
# and duplicate SQL queries
```

**Fix:** Extract the function signatures, then rewrite entire functions cleanly:
```python
fixed_content = '''
def get_session_stats() -> Dict[str, Any]:
    """Read session DB stats from SQLite store."""
    # ... clean implementation without duplicates
'''
```

## Special Case: Tool Call Timeouts Creating Duplicate Code

A specific failure mode occurs when `patch()` appears to fail silently or times out:

**Symptom:**
- You make a patch, it seems to fail
- You retry the same patch multiple times
- Eventually you discover the file has MANY duplicate copies of the same code
- SyntaxError appears at end of file (line ~500+)

**What Happened:**
Earlier patch attempts actually succeeded, but the response was lost/delayed. Retrying added more copies.

**Solution:**
Stop patching immediately and do full rewrite:

```python
# After ANY failed patch, verify file state BEFORE retrying
import ast
with open("file.py") as f:
    content = f.read()

# Check line count - if growing, patches are accumulating
current_lines = len(content.splitlines())
print(f"File has {current_lines} lines")

# Compare to expected - if way too big, corruption occurred
if current_lines > expected_lines * 2:
    print("CRITICAL: File likely has duplicate code - FULL REWRITE NEEDED")
```

## When to Use This

| Situation | Action |
|-----------|--------|
| 1-2 patch failures | Try different old_string/new_string |
| 3+ patch failures | Check file with AST |
| Duplicate code visible | Full rewrite recommended |
| File growing unexpectedly | Stop and verify with AST |
| Production file | Make backup first |

## See Also

- `skill_view('systematic-debugging')` - General debugging workflow
- Patch tool documentation - For correct patch syntax
