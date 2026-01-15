# Path Reference Guide - Windows vs Linux

Quick reference for paths and file separators across different operating systems.

---

## Quick Summary

| Feature | Windows | Linux/macOS |
|---------|---------|------------|
| **Separator** | `\` (backslash) | `/` (forward slash) |
| **Absolute Path Example** | `C:\Users\alice\data` | `/home/alice/data` |
| **Relative Path Example** | `.\data\inbox` | `./data/inbox` |
| **Universal** (works both) | ✓ `/` works | ✓ `/` works |
| **Home Directory** | `C:\Users\alice` or `%USERPROFILE%` | `/home/alice` or `~` |
| **Temp Directory** | `C:\Users\alice\AppData\Local\Temp` or `%TEMP%` | `/tmp` |

---

## Absolute Paths (Full Paths)

Use absolute paths when you need to specify exact file locations.

### Windows

```yaml
# Windows absolute paths
AGENT_INBOX_PATH: C:\Users\alice\documents\inbox
AGENT_PROCESSED_PATH: C:\Users\alice\documents\processed

# With environment variable
AGENT_INBOX_PATH: "%USERPROFILE%\documents\inbox"

# UNC network path
AGENT_INBOX_PATH: \\server\share\inbox
```

### Linux / macOS

```yaml
# Linux absolute paths
AGENT_INBOX_PATH: /home/alice/documents/inbox
AGENT_PROCESSED_PATH: /home/alice/documents/processed

# With home directory variable
AGENT_INBOX_PATH: ~/documents/inbox

# With absolute path
AGENT_INBOX_PATH: /var/agent-data/inbox
```

---

## Relative Paths (Preferred)

Relative paths are portable - they work the same on Windows and Linux. Use these in config files when possible.

### Both Windows and Linux

```yaml
# These work IDENTICALLY on Windows and Linux
AGENT_INBOX_PATH: ./data/inbox
AGENT_PROCESSED_PATH: ./data/processed
AGENT_ERRORS_PATH: ./data/errors
AGENT_LOGS_PATH: ./logs

# Nested relative paths
SCHEMA_PATH: ./schemas/validation.json

# Parent directory reference
TEMP_PATH: ../temp

# Current directory (same as .)
SCRIPT_PATH: ./scripts/helper.py
```

**Why use relative paths?**
- ✅ Works on Windows, Linux, macOS identically
- ✅ Portable - can move project folder and paths still work
- ✅ Simpler to read and understand
- ✅ No absolute paths to expose in version control

---

## Path Separators

### ❌ Don't Mix Separators

```yaml
# ❌ WRONG - mixed separators
AGENT_INBOX_PATH: C:\Users\alice/documents\inbox

# ✅ CORRECT - consistent separators
AGENT_INBOX_PATH: C:\Users\alice\documents\inbox
AGENT_INBOX_PATH: C:/Users/alice/documents/inbox
AGENT_INBOX_PATH: ./documents/inbox
```

### Forward Slashes Work Everywhere

The safest approach: use forward slashes (`/`) in all config files. Both Windows and modern Linux support them:

```yaml
# Works on Windows, Linux, macOS
AGENT_INBOX_PATH: ./data/inbox
SCHEMA_PATH: ./schemas/validation.json

# Also works on Windows
LOG_FILE: C:/Users/alice/logs/agent.log

# But prefer relative paths
LOG_FILE: ./logs/agent.log
```

---

## Environment Variable Syntax

### Windows

#### Command Prompt (CMD)
```cmd
set AGENT_INBOX_PATH=C:\data\inbox
echo %AGENT_INBOX_PATH%
```

#### PowerShell
```powershell
$env:AGENT_INBOX_PATH = "C:\data\inbox"
echo $env:AGENT_INBOX_PATH
```

#### In Config Files (YAML)
```yaml
environment:
  INBOX_PATH: "${AGENT_INBOX_PATH:C:\data\inbox}"

  # Or with default
  INBOX_PATH: "${AGENT_INBOX_PATH:./data/inbox}"
```

### Linux / macOS

#### Bash/Shell
```bash
export AGENT_INBOX_PATH=/data/inbox
echo $AGENT_INBOX_PATH
```

#### In Config Files (YAML)
```yaml
environment:
  INBOX_PATH: "${AGENT_INBOX_PATH:/data/inbox}"

  # Or with default
  INBOX_PATH: "${AGENT_INBOX_PATH:./data/inbox}"
```

---

## Common Paths

### Home Directory

| OS | Variable | Path | Example |
|---|---|---|---|
| Windows | `%USERPROFILE%` | `C:\Users\username` | `C:\Users\alice` |
| Windows | `%HOMEDRIVE%%HOMEPATH%` | `C:\Users\username` | `C:\Users\alice` |
| Linux | `$HOME` or `~` | `/home/username` | `/home/alice` |
| macOS | `$HOME` or `~` | `/Users/username` | `/Users/alice` |

**In config files:**
```yaml
# Windows
DATA_PATH: "%USERPROFILE%\agent-data"

# Linux/macOS
DATA_PATH: "~/agent-data"

# Universal (best)
DATA_PATH: "./data"
```

### Temp/Temporary Directory

| OS | Variable | Path |
|---|---|---|
| Windows | `%TEMP%` | `C:\Users\username\AppData\Local\Temp` |
| Linux | `$TMPDIR` or `/tmp` | `/tmp` |
| macOS | `$TMPDIR` | `/var/folders/...` |

**In config files:**
```yaml
# Windows (less portable)
TEMP_PATH: "%TEMP%\agent"

# Linux/macOS (less portable)
TEMP_PATH: "/tmp/agent"

# Best: use relative path
TEMP_PATH: "./temp"
```

---

## .env File Examples

### Windows User's .env File

```env
# File: agents/examples/file_validator/.env (Windows)

# Option 1: Relative paths (RECOMMENDED)
AGENT_INBOX_PATH=./data/inbox
AGENT_PROCESSED_PATH=./data/processed
AGENT_ERRORS_PATH=./data/errors

# Option 2: Absolute Windows paths
# AGENT_INBOX_PATH=C:\Users\alice\agent-data\inbox
# AGENT_PROCESSED_PATH=C:\Users\alice\agent-data\processed
# AGENT_ERRORS_PATH=C:\Users\alice\agent-data\errors

# Option 3: With environment variable
# AGENT_INBOX_PATH=%USERPROFILE%\agent-data\inbox

LOG_LEVEL=info
LOG_FILE=./logs/file_validator.log
```

### Linux User's .env File

```env
# File: agents/examples/file_validator/.env (Linux/macOS)

# Option 1: Relative paths (RECOMMENDED)
AGENT_INBOX_PATH=./data/inbox
AGENT_PROCESSED_PATH=./data/processed
AGENT_ERRORS_PATH=./data/errors

# Option 2: Absolute paths
# AGENT_INBOX_PATH=/home/alice/agent-data/inbox
# AGENT_PROCESSED_PATH=/home/alice/agent-data/processed
# AGENT_ERRORS_PATH=/home/alice/agent-data/errors

# Option 3: With home directory variable
# AGENT_INBOX_PATH=~/agent-data/inbox

LOG_LEVEL=info
LOG_FILE=./logs/file_validator.log
```

---

## Paths in Python Code

If you write custom tools, handle paths correctly:

### Windows Safe Code

```python
import pathlib

# Recommended: use pathlib (OS-independent)
inbox = pathlib.Path("./data/inbox")
file_path = inbox / "document.json"  # Automatically uses correct separator

# Or manual handling
import os
inbox = os.path.join("data", "inbox")
```

### Linux Safe Code

Same as above! Use `pathlib` for cross-platform paths:

```python
import pathlib

inbox = pathlib.Path("./data/inbox")
file_path = inbox / "document.json"  # Works on both Windows and Linux
```

### ❌ Don't Do This

```python
# ❌ BAD - hardcoded Windows path
path = "C:\data\inbox\file.json"  # Won't work on Linux

# ❌ BAD - hardcoded Linux path
path = "/home/user/data/inbox/file.json"  # Won't work on Windows

# ❌ BAD - backslash without 'r' prefix (escape character issues)
path = "C:\data\file.json"  # Might interpret \d as escape

# ✅ GOOD - relative path
path = "./data/inbox/file.json"

# ✅ GOOD - pathlib
import pathlib
path = pathlib.Path("data") / "inbox" / "file.json"

# ✅ GOOD - os.path.join
import os
path = os.path.join("data", "inbox", "file.json")
```

---

## Special Cases

### Network Paths (Windows)

```yaml
# UNC path (network share)
AGENT_INBOX_PATH: \\server\share\inbox

# In double quotes in config files
AGENT_INBOX_PATH: "\\\\server\\share\\inbox"
```

### Spaces in Paths

Always quote paths with spaces:

```yaml
# ✅ CORRECT - quoted
AGENT_INBOX_PATH: "./My Documents/agent data"
AGENT_INBOX_PATH: "C:\Users\John Doe\agent data"

# ❌ WRONG - unquoted won't work
AGENT_INBOX_PATH: ./My Documents/agent data
AGENT_INBOX_PATH: C:\Users\John Doe\agent data
```

### Windows Reserved Characters

Avoid these in filenames/paths:
- `< > : " / \ | ? *`

Example:
```yaml
# ❌ WRONG
LOG_FILE: ./logs/file<validator>.log

# ✅ CORRECT
LOG_FILE: ./logs/file_validator.log
```

---

## Conversion Guide

### Windows → Linux Path Conversion

| Windows | Linux |
|---------|-------|
| `C:\data\inbox` | `/home/user/data/inbox` |
| `.\data\inbox` | `./data/inbox` |
| `%USERPROFILE%\docs` | `~/docs` |
| `C:/Users/alice/file.txt` | `/home/alice/file.txt` |

### Using relative paths works on both:
| Both |
|------|
| `./data/inbox` |
| `./logs/agent.log` |
| `../temp/file.json` |

---

## Debugging Path Issues

### Check if path is correct:

**Windows**
```cmd
dir C:\Users\alice\data\inbox
REM or
dir ./data/inbox
```

**Linux/macOS**
```bash
ls -la /home/alice/data/inbox
# or
ls -la ./data/inbox
```

### Check environment variables:

**Windows**
```cmd
echo %AGENT_INBOX_PATH%
```

**Linux/macOS**
```bash
echo $AGENT_INBOX_PATH
```

### Check .env file:

**Windows**
```cmd
type .env
# or
notepad .env
```

**Linux/macOS**
```bash
cat .env
# or
nano .env
```

---

## Best Practices

1. **Use relative paths** - Portable and simple
2. **Use forward slashes** - Work on all operating systems
3. **Avoid spaces** - If you must use them, always quote
4. **Quote paths** - In YAML and when setting variables
5. **Use pathlib** - In Python code for cross-platform paths
6. **Test on both** - If possible, test on Windows and Linux

---

## Quick Reference Cheatsheet

```yaml
# ✅ GOOD CONFIG EXAMPLES

# Relative paths (portable)
AGENT_INBOX_PATH: ./data/inbox
AGENT_PROCESSED_PATH: ./data/processed
AGENT_ERRORS_PATH: ./data/errors
LOG_FILE: ./logs/agent.log
SCHEMA_PATH: ./schemas/validation.json

# Environment variables with defaults
INBOX_PATH: "${AGENT_INBOX_PATH:./data/inbox}"
LOG_LEVEL: "${LOG_LEVEL:info}"

# Quoted paths with spaces
DATA_DIR: "./My Agent Data"
```

```yaml
# ❌ AVOID

# Hardcoded absolute paths
AGENT_INBOX_PATH: /home/alice/data/inbox  # Won't work on Windows
AGENT_INBOX_PATH: C:\Users\alice\data  # Won't work on Linux

# Unquoted spaces
LOG_FILE: ./logs/my agent.log  # Will fail

# Mixed separators
AGENT_INBOX_PATH: ./data\inbox  # Inconsistent
```

---

**Remember:** When in doubt, use relative paths with forward slashes. They work everywhere!
