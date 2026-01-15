# Agent Framework Setup Guide - Linux/macOS

This guide walks you through setting up the Agent Framework on Linux (Ubuntu, Fedora, etc.) or macOS.

---

## Prerequisites

Before you begin, make sure you have:

1. **Python 3.9 or higher**
   - **Ubuntu/Debian**:
     ```bash
     sudo apt-get update
     sudo apt-get install python3.9 python3-pip python3-venv
     ```
   - **Fedora/RHEL**:
     ```bash
     sudo dnf install python3.9 python3-pip
     ```
   - **macOS** (using Homebrew):
     ```bash
     brew install python@3.9
     ```
   - ✅ Verify:
     ```bash
     python3 --version
     ```

2. **Git** (for cloning the repo)
   - **Ubuntu/Debian**:
     ```bash
     sudo apt-get install git
     ```
   - **Fedora/RHEL**:
     ```bash
     sudo dnf install git
     ```
   - **macOS** (already included, or via Homebrew):
     ```bash
     brew install git
     ```
   - ✅ Verify:
     ```bash
     git --version
     ```

3. **A Text Editor** (for editing .env and config files)
   - Included: `nano` or `vim`
   - Recommended: Visual Studio Code:
     ```bash
     sudo snap install code --classic  # Ubuntu/Debian
     brew install --cask visual-studio-code  # macOS
     ```

---

## Step 1: Clone or Download the Repository

### Option A: Using Git (Recommended)

```bash
git clone https://github.com/your-repo/agent-framework.git
cd agent-framework
```

### Option B: Download and Extract

```bash
# Download ZIP from GitHub
cd ~/Downloads
unzip agent-framework-main.zip
cd agent-framework-main
```

---

## Step 2: Run Setup

```bash
# Make setup script executable
chmod +x scripts/setup.sh

# Run setup
./scripts/setup.sh
```

This will:
- ✅ Create necessary directories (`data/inbox`, `data/processed`, etc.)
- ✅ Install Python dependencies
- ✅ Verify the installation

**Non-interactive mode** (skip prompts):
```bash
./scripts/setup.sh --quiet
```

---

## Step 3: Verify Installation

Check that everything is working:

```bash
# Test Python runtime
python3 -c "from runtime import Agent; print('✓ Runtime works')"

# List example agents
ls agents/examples/
```

You should see:
```
file_validator  document_categorizer
```

---

## Step 4: Run Your First Agent

### Run the File Validator Example

**Terminal 1: Start the Agent**
```bash
./scripts/run.sh examples/file_validator
```

You should see:
```
Starting agent: examples/file_validator
Config: agents/examples/file_validator/config.yaml

2025-01-15 10:30:45 | INFO | Agent starting: file_validator
2025-01-15 10:30:45 | INFO | Watching: ./data/inbox
2025-01-15 10:30:45 | INFO | Ready for events...
```

**Terminal 2: Test the Agent**

Create a test file:

```bash
# Create test directory (if not already there)
mkdir -p data/inbox

# Create a valid JSON file
echo '{"id": 1, "name": "Alice", "email": "alice@example.com"}' > data/inbox/valid.json
```

**Back in Terminal 1:** You should see the agent process the file:
```
2025-01-15 10:31:02 | INFO | Event: new file detected ./data/inbox/valid.json
2025-01-15 10:31:02 | INFO | Step: validate → success (valid)
2025-01-15 10:31:02 | INFO | ✓ Validated and processed: valid.json
```

**Check output:**
```bash
ls -la data/processed/
# Should show: valid.json
```

---

## Step 5: Configure Your Agent

Each example agent has environment variables you can customize. Edit the `.env` file:

### File Validator Configuration

```bash
cd agents/examples/file_validator
```

Copy the template:
```bash
cp .env.example .env
```

Edit with your favorite editor:
```bash
# Using nano (simplest)
nano .env

# Or using VS Code
code .env

# Or using vim
vim .env
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

## Directory Structure on Linux/macOS

After setup, your file structure looks like:

```
agent-framework/
├── scripts/                    (automation scripts)
│   ├── setup.sh               (Linux/macOS setup)
│   ├── run.sh                 (run any agent)
│   └── new_agent.sh           (create new agent)
│
├── agents/                     (agents)
│   ├── examples/
│   │   ├── file_validator/
│   │   │   ├── setup.sh       (agent-specific setup)
│   │   │   ├── .env           (agent configuration)
│   │   │   ├── config.yaml    (agent behavior)
│   │   │   └── run.py         (agent entry point)
│   │   │
│   │   └── document_categorizer/
│   │       ├── setup.sh
│   │       ├── .env
│   │       ├── config.yaml
│   │       └── run.py
│   │
│   └── _template/             (copy to create new agents)
│       ├── setup.sh
│       ├── .env.example
│       └── config.yaml
│
├── data/                       (created at runtime)
│   ├── inbox/                 (incoming files)
│   ├── processed/             (success output)
│   └── errors/                (failed files)
│
├── logs/                       (agent logs)
│
├── .env.example               (framework config template)
├── requirements.txt           (Python dependencies)
└── README.md                  (overview)
```

---

## Path Reference: Linux vs Windows

When editing config files or .env files, remember the path differences:

| Purpose | Linux/macOS | Windows |
|---------|------------|---------|
| **Inbox** | `/home/user/data/inbox` or `./data/inbox` | `C:\Users\user\data\inbox` or `.\data\inbox` |
| **Separator** | `/` (forward slash) | `\` (backslash) |
| **Relative Path** | `./data/inbox` | `.\data\inbox` or `./data/inbox` |
| **Home Folder** | `~` or `/home/user` | `%USERPROFILE%` or `C:\Users\User` |
| **Temp Folder** | `/tmp` | `%TEMP%` or `C:\Users\User\AppData\Local\Temp` |

**Tip**: Forward slashes (`/`) work on all systems, so prefer `./data/inbox` in config files.

---

## Common Issues & Solutions

### Issue: "Python not found"

**Error:**
```
[ERROR] Python not found. Please install Python 3.9+
```

**Solution:**
1. Install Python 3.9+
   - **Ubuntu**: `sudo apt-get install python3.9 python3-pip`
   - **macOS**: `brew install python@3.9`
2. Verify: `python3 --version`
3. Note: You may need to use `python3` instead of `python`

---

### Issue: "Permission denied" on setup.sh

**Error:**
```
bash: ./scripts/setup.sh: Permission denied
```

**Solution:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

---

### Issue: "Agent won't start"

**Error:**
```
Error: Agent not found: agents/examples/file_validator
```

**Solution:**
- Make sure you're in the agent-framework root directory
- Check the agent name: `./scripts/run.sh examples/file_validator`
- List available agents: `ls agents/examples/`

---

### Issue: `.env` file not being read

**Solution:**
1. Make sure the file is named exactly `.env` (not `.env.txt`)
2. Make sure it's in the agent's directory (e.g., `agents/examples/file_validator/.env`)
3. Restart the agent after editing `.env`
4. Check file permissions: `ls -la .env`

---

## Environment Variables Explained

### What are they?

Environment variables are like "settings" that your agent reads when it starts.

### Where do I put them?

In the `.env` file in your agent's directory. For example:

**File**: `agents/examples/file_validator/.env`

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

## Using Shell Environment Variables

If you prefer not to use `.env` files, you can set variables in the shell:

```bash
# Set for current session only
export AGENT_INBOX_PATH="/home/user/data/inbox"
./scripts/run.sh examples/file_validator

# Or inline (one command)
AGENT_INBOX_PATH="/home/user/data/inbox" ./scripts/run.sh examples/file_validator
```

To make them permanent, add to `~/.bashrc` or `~/.zshrc`:

```bash
export AGENT_INBOX_PATH="/home/user/data/inbox"
export AGENT_PROCESSED_PATH="/home/user/data/processed"
export AGENT_ERRORS_PATH="/home/user/data/errors"
```

Then:
```bash
source ~/.bashrc  # (or ~/.zshrc for macOS with zsh)
```

---

## Creating Your First Custom Agent

```bash
# Create new agent from template
./scripts/new_agent.sh my_validator

# Setup the agent
cd agents/my_validator
chmod +x setup.sh
./setup.sh

# Configure it
nano config.yaml
nano .env

# Run it
cd ../../
./scripts/run.sh my_validator
```

---

## Using Virtual Environments (Recommended)

For development, create a Python virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/macOS
# For Windows PowerShell: venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Now run agents
./scripts/run.sh examples/file_validator
```

---

## Running Agents in Background

Run an agent in the background and capture logs:

```bash
# Run in background
nohup ./scripts/run.sh examples/file_validator > ./agent.log 2>&1 &

# Watch logs in real-time
tail -f ./agent.log

# Or use screen/tmux for better control
screen
./scripts/run.sh examples/file_validator
# Press Ctrl+A then D to detach
```

---

## Systemd Service (Advanced)

For permanent setup, create a systemd service:

**File**: `/etc/systemd/system/file-validator.service`

```ini
[Unit]
Description=File Validator Agent
After=network.target

[Service]
Type=simple
User=agent
WorkingDirectory=/home/agent/agent-framework
ExecStart=/home/agent/agent-framework/scripts/run.sh examples/file_validator
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
# Enable and start
sudo systemctl enable file-validator.service
sudo systemctl start file-validator.service

# Check status
sudo systemctl status file-validator.service

# Watch logs
sudo journalctl -u file-validator.service -f
```

---

## Next Steps

1. ✅ **Understand the framework**: Read `README.md`
2. ✅ **Run examples**: Try `file_validator` and `document_categorizer`
3. ✅ **Customize**: Edit `.env` files to change paths
4. ✅ **Create agents**: Use `./scripts/new_agent.sh my_agent`
5. ✅ **Learn workflows**: Read `docs/WORKFLOWS.md`

---

## Getting Help

- **Framework overview**: See `README.md`
- **Detailed examples**: See `agents/examples/README.md`
- **Workflow syntax**: See `docs/WORKFLOWS.md`
- **Available tools**: See `docs/TOOLS.md`
- **Creating agents**: See `docs/CREATE_AGENT.md`

---

## Tips for Linux/macOS Users

1. **Use VS Code**: Free and great for editing YAML files
2. **Use virtual environments**: `python3 -m venv venv` before setup
3. **Watch logs in real-time**: `tail -f logs/agent.log`
4. **Run multiple agents**: Use `screen` or `tmux` for separate windows
5. **Use systemd**: For production setups, create a systemd service

---

**Ready to build your first agent? Start with `./scripts/setup.sh`!**
