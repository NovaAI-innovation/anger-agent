# Agent Framework Setup Guide - Windows

This guide walks you through setting up the Agent Framework on Windows 10/11.

---

## Prerequisites

Before you begin, make sure you have:

1. **Python 3.9 or higher**
   - Download: https://www.python.org/downloads/
   - ✅ Verify: Open Command Prompt/PowerShell and run:
     ```cmd
     python --version
     ```
   - Should show: `Python 3.9.x` or higher

2. **Git** (recommended for cloning the repo)
   - Download: https://git-scm.com/download/win
   - ✅ Verify:
     ```cmd
     git --version
     ```

3. **A Text Editor** (for editing .env and config files)
   - Visual Studio Code (recommended): https://code.visualstudio.com/
   - Or use built-in Notepad, but VS Code is better

---

## Step 1: Clone or Download the Repository

### Option A: Using Git (Recommended)

```cmd
git clone https://github.com/your-repo/agent-framework.git
cd agent-framework
```

### Option B: Download ZIP

1. Go to the repository on GitHub
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open Command Prompt and navigate to the folder:
   ```cmd
   cd path\to\agent-framework
   ```

---

## Step 2: Run Setup

Choose your preferred method:

### Option 1: Using Batch File (Recommended for CMD)

```cmd
scripts\setup.bat
```

This will:
- ✅ Create necessary directories (`data\inbox`, `data\processed`, etc.)
- ✅ Install Python dependencies
- ✅ Verify the installation

### Option 2: Using PowerShell

First, enable script execution (one-time only):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then run:

```powershell
.\scripts\setup.ps1
```

### Option 3: Manual Setup

If the scripts don't work, do this manually:

```cmd
REM Create directories
mkdir data\inbox
mkdir data\processed
mkdir data\errors
mkdir logs

REM Install dependencies
python -m pip install -r requirements.txt
```

---

## Step 3: Verify Installation

Check that everything is working:

```cmd
REM Test Python runtime
python -c "from runtime import Agent; print('✓ Runtime works')"

REM List example agents
dir agents\examples
```

You should see:
- `agents\examples\file_validator\`
- `agents\examples\document_categorizer\`

---

## Step 4: Run Your First Agent

### Run the File Validator Example

**Terminal 1: Start the Agent**
```cmd
scripts\run.bat examples\file_validator
```

You should see:
```
Starting agent: examples\file_validator
Config: agents\examples\file_validator\config.yaml

2025-01-15 10:30:45 | INFO | Agent starting: file_validator
2025-01-15 10:30:45 | INFO | Watching: ./data/inbox
2025-01-15 10:30:45 | INFO | Ready for events...
```

**Terminal 2: Test the Agent**

Create a test file:

```cmd
REM Create test directory
mkdir data\inbox

REM Create a valid JSON file
echo {"id": 1, "name": "Alice", "email": "alice@example.com"} > data\inbox\valid.json
```

**Back in Terminal 1:** You should see the agent process the file:
```
2025-01-15 10:31:02 | INFO | Event: new file detected ./data/inbox/valid.json
2025-01-15 10:31:02 | INFO | Step: validate → success (valid)
2025-01-15 10:31:02 | INFO | ✓ Validated and processed: valid.json
```

**Check output:**
```cmd
dir data\processed
REM Should show: valid.json
```

---

## Step 5: Configure Your Agent

Each example agent has environment variables you can customize. Edit the `.env` file:

### File Validator Configuration

```cmd
cd agents\examples\file_validator
```

Copy the template:
```cmd
copy .env.example .env
```

Edit with your text editor:
```cmd
notepad .env
```

Or with VS Code:
```cmd
code .env
```

The `.env` file contains:
```env
# Paths (relative paths work on Windows and Linux)
AGENT_INBOX_PATH=./data/inbox
AGENT_PROCESSED_PATH=./data/processed
AGENT_ERRORS_PATH=./data/errors

# Logging
LOG_LEVEL=info
LOG_FILE=./logs/file_validator.log
```

---

## Directory Structure on Windows

After setup, your file structure looks like:

```
agent-framework\
├── scripts\                    (automation scripts)
│   ├── setup.bat              (Windows setup)
│   ├── setup.ps1              (PowerShell setup)
│   ├── run.bat                (run any agent)
│   └── new_agent.bat          (create new agent)
│
├── agents\                     (agents)
│   ├── examples\
│   │   ├── file_validator\
│   │   │   ├── setup.bat      (agent-specific setup)
│   │   │   ├── .env           (agent configuration)
│   │   │   ├── config.yaml    (agent behavior)
│   │   │   └── run.py         (agent entry point)
│   │   │
│   │   └── document_categorizer\
│   │       ├── setup.bat
│   │       ├── .env
│   │       ├── config.yaml
│   │       └── run.py
│   │
│   └── _template\             (copy to create new agents)
│       ├── setup.bat
│       ├── .env.example
│       └── config.yaml
│
├── data\                       (created at runtime)
│   ├── inbox\                 (incoming files)
│   ├── processed\             (success output)
│   └── errors\                (failed files)
│
├── logs\                       (agent logs)
│
├── .env.example               (framework config template)
├── requirements.txt           (Python dependencies)
└── README.md                  (overview)
```

---

## Path Reference: Windows vs Linux

When editing config files or .env files, remember the path differences:

| Purpose | Windows | Linux/macOS |
|---------|---------|------------|
| **Inbox** | `C:\Users\user\data\inbox` or `.\data\inbox` | `/home/user/data/inbox` or `./data/inbox` |
| **Separator** | `\` (backslash) | `/` (forward slash) |
| **Relative Path** | `.\data\inbox` | `./data/inbox` |
| **Home Folder** | `%USERPROFILE%` or `C:\Users\User` | `~` or `/home/user` |
| **Temp Folder** | `%TEMP%` or `C:\Users\User\AppData\Local\Temp` | `/tmp` |

**Tip**: Forward slashes (`/`) work on both Windows and Linux, so use `./data/inbox` in config files.

---

## Common Issues & Solutions

### Issue: "Python not found"

**Error:**
```
[ERROR] Python not found. Please install Python 3.9+
```

**Solution:**
1. Install Python 3.9+ from https://www.python.org/downloads/
2. Make sure to check "Add Python to PATH" during installation
3. Restart Command Prompt/PowerShell
4. Verify: `python --version`

---

### Issue: "scripts\setup.bat not found"

**Error:**
```
'scripts\setup.bat' is not recognized
```

**Causes & Solutions:**
- Make sure you're in the `agent-framework` directory
- Try the PowerShell version: `.\scripts\setup.ps1`
- Or run manually with `python -m pip install -r requirements.txt`

---

### Issue: Agent won't start / "run.py not found"

**Error:**
```
Error: No run.py found in agents\examples\file_validator
```

**Solution:**
- Make sure you're in the agent-framework root directory
- Check the agent name: `scripts\run.bat examples\file_validator`
- List available agents: `dir agents\examples\`

---

### Issue: `.env` file not being read

**Solution:**
1. Make sure the file is named exactly `.env` (not `.env.txt`)
2. Make sure it's in the agent's directory, not somewhere else
3. Restart the agent after editing `.env`

---

## Environment Variables Explained

### What are they?

Environment variables are like "settings" that your agent reads when it starts.

### Where do I put them?

In the `.env` file in your agent's directory. For example:

**File**: `agents\examples\file_validator\.env`

```env
AGENT_INBOX_PATH=./data/inbox
LOG_LEVEL=debug
```

### How does the agent use them?

The agent reads `config.yaml` which references environment variables:

```yaml
environment:
  INBOX_PATH: "${AGENT_INBOX_PATH:./data/inbox}"
  LOG_LEVEL: "${LOG_LEVEL:info}"
```

Syntax: `${VARIABLE_NAME:default_value}`
- `${AGENT_INBOX_PATH}` - reads from .env or environment
- `${AGENT_INBOX_PATH:./data/inbox}` - uses default if not set

---

## Using Command Line Environment Variables

If you prefer not to use `.env` files, you can set variables in the command line:

### Command Prompt (CMD)

```cmd
set AGENT_INBOX_PATH=C:\my\custom\path
scripts\run.bat examples\file_validator
```

### PowerShell

```powershell
$env:AGENT_INBOX_PATH = "C:\my\custom\path"
.\scripts\run.bat examples\file_validator
```

---

## Creating Your First Custom Agent

```cmd
REM Create new agent from template
scripts\new_agent.bat my_validator

REM Setup the agent
cd agents\my_validator
setup.bat

REM Configure it
notepad config.yaml
notepad .env

REM Run it
cd ..\..\
scripts\run.bat my_validator
```

---

## Troubleshooting PowerShell Execution Policy

If you get an error like:
```
cannot be loaded because running scripts is disabled on this system
```

Run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then run setup again:
```powershell
.\scripts\setup.ps1
```

---

## Next Steps

1. ✅ **Understand the framework**: Read `README.md`
2. ✅ **Run examples**: Try `file_validator` and `document_categorizer`
3. ✅ **Customize**: Edit `.env` files to change paths
4. ✅ **Create agents**: Use `scripts\new_agent.bat my_agent`
5. ✅ **Learn workflows**: Read `docs/WORKFLOWS.md`

---

## Getting Help

- **Framework overview**: See `README.md`
- **Detailed examples**: See `agents/examples/README.md`
- **Workflow syntax**: See `docs/WORKFLOWS.md`
- **Available tools**: See `docs/TOOLS.md`
- **Creating agents**: See `docs/CREATE_AGENT.md`

---

## Tips for Windows Users

1. **Use VS Code**: It's free and great for editing YAML files
2. **PowerShell is modern**: Use `.\scripts\setup.ps1` instead of `.bat` if possible
3. **Forward slashes work**: In config files, use `/` instead of `\`
4. **Relative paths are portable**: Use `./data/inbox` instead of `C:\...`
5. **Watch for .txt extensions**: Make sure `.env` isn't saved as `.env.txt`

---

**Ready to build your first agent? Start with `scripts\setup.bat`!**
