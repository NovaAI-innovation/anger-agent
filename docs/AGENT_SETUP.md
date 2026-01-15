# Agent Setup Guide

How to configure and run individual agents.

---

## Understanding Agent Setup

Each agent has its own setup process and configuration:

```
agent-framework/
└── agents/
    └── examples/
        └── file_validator/
            ├── setup.sh           ← Unix/Linux/macOS setup
            ├── setup.bat          ← Windows setup
            ├── .env.example       ← Config template
            ├── .env               ← Your custom config (created by setup)
            ├── config.yaml        ← Agent behavior definition
            ├── AGENTS.md          ← Agent documentation
            └── run.py             ← Agent entry point
```

---

## Quick Start: 3 Steps

### Step 1: Run Agent Setup

This creates directories and configures the environment.

=== "Windows (Command Prompt)"
    ```cmd
    cd agents\examples\file_validator
    setup.bat
    ```

=== "Windows (PowerShell)"
    ```powershell
    cd agents\examples\file_validator
    .\setup.bat
    ```

=== "Linux/macOS"
    ```bash
    cd agents/examples/file_validator
    chmod +x setup.sh
    ./setup.sh
    ```

### Step 2: Edit Configuration (Optional)

Customize the `.env` file for your setup:

=== "Windows"
    ```cmd
    notepad .env
    REM Or with VS Code:
    code .env
    ```

=== "Linux/macOS"
    ```bash
    nano .env
    # Or with VS Code:
    code .env
    ```

### Step 3: Run the Agent

From the project root:

=== "Windows"
    ```cmd
    scripts\run.bat examples\file_validator
    ```

=== "Linux/macOS"
    ```bash
    ./scripts/run.sh examples/file_validator
    ```

---

## Understanding .env Files

The `.env` file stores configuration for each agent.

### What is `.env`?

A file that defines environment variables for your agent. Example:

```env
# File: agents/examples/file_validator/.env

AGENT_INBOX_PATH=./data/inbox
AGENT_PROCESSED_PATH=./data/processed
AGENT_ERRORS_PATH=./data/errors
LOG_LEVEL=info
LOG_FILE=./logs/file_validator.log
```

### Creating .env File

#### Automatic (Recommended)

Run the agent's setup script:

=== "Windows"
    ```cmd
    cd agents\examples\file_validator
    setup.bat
    ```

=== "Linux/macOS"
    ```bash
    cd agents/examples/file_validator
    ./setup.sh
    ```

The setup script:
- ✅ Creates necessary directories
- ✅ Copies `.env.example` to `.env`
- ✅ Prompts for customization
- ✅ Validates configuration

#### Manual

```bash
# Copy the template
cp .env.example .env

# Edit it
nano .env  # or your favorite editor
```

### Structure of .env

```env
# Paths
AGENT_INBOX_PATH=./data/inbox              # Where files come in
AGENT_PROCESSED_PATH=./data/processed      # Success output
AGENT_ERRORS_PATH=./data/errors            # Failed files

# Logging
LOG_LEVEL=info                             # debug, info, warning, error
LOG_FILE=./logs/file_validator.log         # Where logs go

# Optional agent-specific settings
SCHEMA_PATH=./schema.json                  # Validation schema
MIN_CONFIDENCE=0.7                         # Confidence threshold
```

---

## Customizing Paths

### Relative Paths (Default)

Best for portability - works on Windows, Linux, macOS:

```env
# Relative paths work everywhere
AGENT_INBOX_PATH=./data/inbox
AGENT_PROCESSED_PATH=./data/processed
AGENT_ERRORS_PATH=./data/errors
LOG_FILE=./logs/agent.log
```

Directory structure:
```
agents/examples/file_validator/
├── data/
│   ├── inbox/
│   ├── processed/
│   └── errors/
├── logs/
└── config.yaml
```

### Absolute Paths

For specific locations or external drives:

**Windows**
```env
AGENT_INBOX_PATH=C:\Users\alice\agent-data\inbox
AGENT_PROCESSED_PATH=C:\Users\alice\agent-data\processed
AGENT_ERRORS_PATH=C:\Users\alice\agent-data\errors
```

**Linux/macOS**
```env
AGENT_INBOX_PATH=/home/alice/agent-data/inbox
AGENT_PROCESSED_PATH=/home/alice/agent-data/processed
AGENT_ERRORS_PATH=/home/alice/agent-data/errors
```

### Shared Across Agents

Put shared data in a common location:

```env
# agents/examples/file_validator/.env
AGENT_INBOX_PATH=../../shared-data/inbox
AGENT_PROCESSED_PATH=../../shared-data/processed

# agents/examples/document_categorizer/.env
AGENT_INBOX_PATH=../../shared-data/inbox
AGENT_PROCESSED_PATH=../../shared-data/processed
```

---

## Environment Variables Reference

### File Validator Agent

These variables control the file validator agent:

```env
# Input/output paths
AGENT_INBOX_PATH=./data/inbox
AGENT_PROCESSED_PATH=./data/processed
AGENT_ERRORS_PATH=./data/errors

# Validation schema
SCHEMA_PATH=./schema.json

# Logging
LOG_LEVEL=info              # debug, info, warning, error
LOG_FILE=./logs/file_validator.log
LOG_MAX_SIZE_MB=100         # Log rotation size
LOG_BACKUP_COUNT=5          # Number of backups

# Monitoring
MONITORING_ENABLED=true
```

### Document Categorizer Agent

Configuration for the document categorizer:

```env
# Input/output paths
AGENT_INBOX_PATH=./data/inbox
AGENT_PROCESSED_PATH=./data/processed
AGENT_ERRORS_PATH=./data/errors
AGENT_REVIEW_PATH=./data/review

# LLM Provider (mock, openai, claude)
LLM_PROVIDER=mock

# OpenAI configuration (if using OpenAI)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# Anthropic configuration (if using Claude)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Categorization settings
MIN_CONFIDENCE=0.7
MAX_DOCUMENT_SIZE_KB=10000

# Logging
LOG_LEVEL=debug
LOG_FILE=./logs/document_categorizer.log
```

---

## Sensitive Configuration

### API Keys

Never commit API keys to version control. They're already in `.gitignore`:

```env
# ✅ SAFE - in .env (not committed)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# ✅ SAFE - can commit
.env.example (without actual keys)
```

### Database Credentials

Same principle:

```env
# ✅ SAFE - in .env (not committed)
DATABASE_URL=postgresql://user:password@localhost/dbname

# ✅ SAFE - can commit
.env.example (without actual credentials)
```

---

## Verifying Configuration

### Check .env File

View your configuration:

=== "Windows"
    ```cmd
    type .env
    ```

=== "Linux/macOS"
    ```bash
    cat .env
    ```

### Test Agent Startup

Try to start the agent. It should validate the config:

=== "Windows"
    ```cmd
    scripts\run.bat examples\file_validator
    ```

=== "Linux/macOS"
    ```bash
    ./scripts/run.sh examples/file_validator
    ```

Expected output:
```
Starting agent: examples/file_validator
Config: agents/examples/file_validator/config.yaml

2025-01-15 10:30:45 | INFO | Agent starting: file_validator
2025-01-15 10:30:45 | INFO | Watching: ./data/inbox
2025-01-15 10:30:45 | INFO | Ready for events...
```

### Check Directories

Verify directories were created:

=== "Windows"
    ```cmd
    dir agents\examples\file_validator\data
    dir agents\examples\file_validator\logs
    ```

=== "Linux/macOS"
    ```bash
    ls -la agents/examples/file_validator/data
    ls -la agents/examples/file_validator/logs
    ```

---

## Troubleshooting

### Issue: "Cannot read .env file"

**Cause**: File doesn't exist or has wrong name

**Solution**:
```bash
# Check if file exists
ls -la .env  # Linux/macOS
dir .env     # Windows

# Verify it's not .env.txt
# Make sure it's exactly ".env"
```

### Issue: "Environment variable not found"

**Cause**: Variable not set in .env or environment

**Solution**:
1. Check `.env` file has the variable
2. Make sure you're in the correct directory
3. Restart the agent after editing `.env`

Example:
```bash
# View current variables
echo $AGENT_INBOX_PATH  # Linux/macOS
echo %AGENT_INBOX_PATH% # Windows

# If empty, add to .env and restart agent
```

### Issue: "Path doesn't exist"

**Cause**: Directory configured in `.env` doesn't exist

**Solution**:
1. Run the setup script - it creates directories
2. Or manually create:
   ```bash
   mkdir -p data/inbox data/processed data/errors  # Linux/macOS
   mkdir data\inbox data\processed data\errors    # Windows
   ```

### Issue: "Permission denied" (Linux/macOS)

**Cause**: Incorrect file permissions

**Solution**:
```bash
# Make setup script executable
chmod +x setup.sh

# Make agent directory writable
chmod -R u+w agents/examples/file_validator/
```

---

## Multiple Agents Configuration

### Separate Data Directories

Keep each agent's data separate:

```env
# agents/examples/file_validator/.env
AGENT_INBOX_PATH=./data/inbox
AGENT_PROCESSED_PATH=./data/processed

# agents/examples/document_categorizer/.env
AGENT_INBOX_PATH=./data/inbox
AGENT_PROCESSED_PATH=./data/processed
```

### Shared Infrastructure

Share some resources:

```env
# agents/examples/file_validator/.env
AGENT_INBOX_PATH=../../shared/inbox
AGENT_PROCESSED_PATH=./data/processed
LOG_FILE=../../shared/logs/file_validator.log

# agents/examples/document_categorizer/.env
AGENT_INBOX_PATH=../../shared/inbox
AGENT_PROCESSED_PATH=./data/processed
LOG_FILE=../../shared/logs/document_categorizer.log
```

---

## Advanced: Custom Environment Variables

Add your own variables to `.env`:

```env
# Standard variables
AGENT_INBOX_PATH=./data/inbox

# Custom variables
CUSTOM_SETTING=value
DATABASE_URL=postgresql://localhost/mydb
API_ENDPOINT=https://api.example.com
TIMEOUT_SECONDS=30
RETRY_COUNT=3
```

Then use in `config.yaml`:

```yaml
environment:
  INBOX_PATH: "${AGENT_INBOX_PATH:./data/inbox}"
  DATABASE_URL: "${DATABASE_URL:sqlite:///agent.db}"
  API_ENDPOINT: "${API_ENDPOINT:https://api.example.com}"
  TIMEOUT: "${TIMEOUT_SECONDS:30}"
```

---

## Environment Variable Syntax in YAML

### Basic Variable

```yaml
# Reads VARIABLE from .env or environment
VAR_NAME: "${VARIABLE}"
```

### With Default Value

```yaml
# Uses default if VARIABLE not set
VAR_NAME: "${VARIABLE:default_value}"
```

### Examples

```yaml
environment:
  # Required (will fail if not set)
  INBOX_PATH: "${AGENT_INBOX_PATH}"

  # Optional (uses default if not set)
  LOG_FILE: "${LOG_FILE:./logs/agent.log}"
  LOG_LEVEL: "${LOG_LEVEL:info}"

  # Custom defaults
  TIMEOUT: "${TIMEOUT_SECONDS:60}"
  RETRIES: "${RETRY_COUNT:3}"
```

---

## Best Practices

1. **Start with setup script**: It handles all initial configuration
2. **Use relative paths**: They're portable across Windows and Linux
3. **Review .env carefully**: Ensure all required variables are set
4. **Never commit actual .env**: Only commit `.env.example`
5. **Test after changes**: Restart agent after editing `.env`
6. **Use meaningful defaults**: Make systems work out-of-box
7. **Document custom variables**: Explain in `.env.example` what each does

---

## Next Steps

- Read `SETUP_WINDOWS.md` for Windows-specific guidance
- Read `SETUP_LINUX.md` for Linux/macOS-specific guidance
- Read `PATH_REFERENCE.md` for path syntax reference
- See `config.yaml` in each agent for detailed behavior config
- Check agent's `AGENTS.md` for agent-specific information

---

## Quick Reference

```bash
# Setup new agent (all platforms)
cd agents/examples/file_validator
./setup.sh              # Linux/macOS
setup.bat              # Windows

# Edit configuration
nano .env              # Linux/macOS
notepad .env           # Windows

# Run agent from project root
./scripts/run.sh examples/file_validator      # Linux/macOS
scripts\run.bat examples\file_validator       # Windows

# Check configuration
cat .env               # Linux/macOS
type .env              # Windows

# Verify directories exist
ls -la data/           # Linux/macOS
dir data\              # Windows
```
