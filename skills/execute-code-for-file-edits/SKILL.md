---
name: execute-code-for-file-edits
description: Use execute_code with Python pathlib for reliable file edits when patch() fails with indentation/syntax issues
category: software-development
---

# Execute Code for File Edits - When Patch Fails

## Purpose
When `patch()` tool repeatedly fails with indentation errors, syntax issues, or "old_string and new_string are identical" errors, use `execute_code` with Python's pathlib for reliable file manipulation.

## When to Use
- Patch tool fails 2+ times on same file
- Indentation errors after patch
- Complex multi-line edits needed
- Need to insert code at specific markers
- File has been partially modified and is in inconsistent state

## Pattern

```python
from pathlib import Path

# Read the file
file_path = Path("/path/to/file.py")
content = file_path.read_text()

# Find insertion point using string marker
marker = "def some_function(self, ...):"
insert_pos = content.find(marker)

if insert_pos == -1:
    print("ERROR: Could not find marker")
    exit(1)

# Create new code to insert
new_code = '''
    def new_method(self):
        # implementation
        pass
'''

# Insert at marker position
new_content = content[:insert_pos] + new_code + content[insert_pos:]

# Write back
file_path.write_text(new_content)
print("✓ File updated successfully")

# Verify syntax
import py_compile
try:
    py_compile.compile(file_path, doraise=True)
    print("✓ Syntax OK")
except py_compile.PyCompileError as e:
    print(f"✗ Syntax error: {e}")
    exit(1)
```

## Advantages Over Patch
- No indentation ambiguity
- Full control over string manipulation
- Can search for markers dynamically
- Atomic write (no partial states)
- Immediate syntax verification
- Works on any file size

## Disadvantages
- No unified diff output
- Overwrites entire file
- Less transparent than patch
- Requires Python execution

## Best Practices

1. **Always verify syntax** after write:
```python
import py_compile
py_compile.compile(file_path, doraise=True)
```

2. **Use unique markers** for insertion points:
```python
marker = "        elif canonical == \"usage\":\n            self._show_usage()"
```

3. **Preserve existing content** by reading first:
```python
content = file_path.read_text()
```

4. **Handle errors gracefully**:
```python
if insert_pos == -1:
    print("ERROR: Marker not found")
    exit(1)
```

5. **For multiple edits**, chain operations:
```python
# Edit 1
content = content.replace(old1, new1)
# Edit 2
content = content.replace(old2, new2)
# Write once
file_path.write_text(content)
```

## Example: Adding a Method to CLI Class

```python
from pathlib import Path

cli_path = Path("/mnt/c/Users/User/hermes-agent/cli.py")
content = cli_path.read_text()

# Find where to insert new method
insert_marker = "    def _show_insights(self, command: str = \"/insights\"):"
insert_pos = content.find(insert_marker)

new_method = '''
    def _show_tokens(self, command: str = "/tokens"):
        """Show detailed token dashboard."""
        if not self.agent:
            print("(._.) No active agent.")
            return
        # ... implementation ...
'''

new_content = content[:insert_pos] + new_method + content[insert_pos:]

# Also add command handler
handler_search = "elif canonical == \"usage\""
handler_pos = new_content.find(handler_search)
line_end = new_content.find("self._show_usage()", handler_pos)
next_elif = new_content.find("        elif canonical ==", line_end)

tokens_handler = "        elif canonical == \"tokens\":\n            self._show_tokens(cmd_original)\n"
new_content = new_content[:next_elif] + tokens_handler + new_content[next_elif:]

cli_path.write_text(new_content)

# Verify
import py_compile
py_compile.compile(cli_path, doraise=True)
```

## When NOT to Use
- Simple single-line changes → use patch()
- When you need diff output for review → use patch()
- When working with binary files → use write_file()
- When file is < 100 lines → patch() is fine

## Recovery from Patch Failures

If patch fails repeatedly:
1. `git checkout file.py` to restore original
2. Use execute_code pattern above
3. Verify syntax
4. Commit changes

## References
- Hermes Agent: `/mnt/c/Users/User/hermes-agent/`
- OMK CLI: `/mnt/c/Users/User/OneDrive/OMK/omk/`
- Token dashboard implementation (April 2026)