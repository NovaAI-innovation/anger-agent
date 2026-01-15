# Quick Start: 5 Minutes to Your First Agent

This guide gets you from zero to running an agent in 5 minutes.

---

## Step 1: Install (1 minute)

Choose your platform:

### Windows (Command Prompt)
```cmd
cd agent-framework
scripts\setup.bat
```

### Windows (PowerShell)
```powershell
cd agent-framework
.\scripts\setup.bat
```

### Linux / macOS
```bash
cd agent-framework
./scripts/setup.sh
```

This creates directories and installs dependencies.

---

## Step 2: Run Example Agent (2 minutes)

Choose your platform:

### Windows (Command Prompt)
```cmd
scripts\run.bat examples\file_validator
```

### Windows (PowerShell)
```powershell
.\scripts\run.bat examples\file_validator
```

### Linux / macOS
```bash
./scripts/run.sh examples/file_validator
```

You should see:
```
2025-01-15 10:30:45 | INFO | Agent starting: file_validator
2025-01-15 10:30:45 | INFO | Watching: ./data/inbox
2025-01-15 10:30:45 | INFO | Ready for events...
```

The agent is now **watching `./data/inbox` for JSON files**.

---

## Step 3: Test It (2 minutes)

**Open another terminal (keep the agent running in the first one):**

### Create a valid file:

=== "Windows (Command Prompt)"
    ```cmd
    echo {"id": 1, "name": "Alice", "email": "alice@example.com"} > data\inbox\valid.json
    ```

=== "Windows (PowerShell)"
    ```powershell
    '{"id": 1, "name": "Alice", "email": "alice@example.com"}' | Out-File -Encoding UTF8 data\inbox\valid.json
    ```

=== "Linux / macOS"
    ```bash
    echo '{"id": 1, "name": "Alice", "email": "alice@example.com"}' > data/inbox/valid.json
    ```

**In agent terminal:** You'll see:
```
2025-01-15 10:31:02 | INFO | Event: new file detected ./data/inbox/valid.json
2025-01-15 10:31:02 | INFO | Executing workflow: validate_and_process
2025-01-15 10:31:02 | INFO | Step: read_file → success
2025-01-15 10:31:02 | INFO | Step: parse_json → success
2025-01-15 10:31:02 | INFO | Step: validate → success (valid)
2025-01-15 10:31:02 | INFO | Moving valid.json → ./data/processed/
2025-01-15 10:31:02 | INFO | Workflow complete ✓
```

**Check results:**

=== "Windows"
    ```cmd
    dir data\processed\
    REM Output: valid.json
    ```

=== "Linux / macOS"
    ```bash
    ls data/processed/
    # Output: valid.json
    ```

### Create an invalid file:

=== "Windows (Command Prompt)"
    ```cmd
    echo {"id": 1, "name": "Bob"} > data\inbox\invalid.json
    REM Missing 'email' field - violates schema
    ```

=== "Windows (PowerShell)"
    ```powershell
    '{"id": 1, "name": "Bob"}' | Out-File -Encoding UTF8 data\inbox\invalid.json
    ```

=== "Linux / macOS"
    ```bash
    echo '{"id": 1, "name": "Bob"}' > data/inbox/invalid.json
    # Missing 'email' field - violates schema
    ```

**In agent terminal:** You'll see:
```
2025-01-15 10:31:15 | INFO | Event: new file detected ./data/inbox/invalid.json
2025-01-15 10:31:15 | INFO | Executing workflow: validate_and_process
2025-01-15 10:31:15 | INFO | Step: read_file → success
2025-01-15 10:31:15 | INFO | Step: parse_json → success
2025-01-15 10:31:15 | INFO | Step: validate → FAILED (missing email field)
2025-01-15 10:31:15 | WARNING | Validation failed - logging to errors
2025-01-15 10:31:15 | INFO | Workflow complete ✗
```

**Check results:**

=== "Windows"
    ```cmd
    type data\errors\invalid.json.log
    REM Output: Validation errors: ['Missing required field: email']
    ```

=== "Linux / macOS"
    ```bash
    cat data/errors/invalid.json.log
    # Output: Validation errors: ['Missing required field: email']
    ```

---

## What Just Happened?

The agent executed this workflow (defined in `config.yaml`):

```yaml
workflows:
  validate_and_process:
    steps:
      1. Read the file
      2. Parse JSON
      3. Validate against schema
      4. If valid: Move to ./data/processed/
      5. If invalid: Log errors to ./data/errors/
```

**Zero Python code.** Everything is YAML.

---

## Step 4: Customize It (Bonus - not in 5 min)

Now that you understand how it works, you can customize:

### Edit the workflow configuration:

=== "Windows"
    ```cmd
    notepad agents\examples\file_validator\config.yaml
    REM Or with VS Code:
    code agents\examples\file_validator\config.yaml
    ```

=== "Linux / macOS"
    ```bash
    vim agents/examples/file_validator/config.yaml
    # Or:
    code agents/examples/file_validator/config.yaml
    ```

Change anything:
- Add more workflow steps
- Modify validation logic
- Change output directories (in `.env` file)

### Edit the environment configuration:

=== "Windows"
    ```cmd
    notepad agents\examples\file_validator\.env
    ```

=== "Linux / macOS"
    ```bash
    nano agents/examples/file_validator/.env
    ```

Customize paths and logging settings.

### Edit the documentation:

=== "Windows"
    ```cmd
    notepad agents\examples\file_validator\AGENTS.md
    ```

=== "Linux / macOS"
    ```bash
    vim agents/examples/file_validator/AGENTS.md
    ```

Describe what your agent does.

### Run it again:

=== "Windows"
    ```cmd
    scripts\run.bat examples\file_validator
    ```

=== "Linux / macOS"
    ```bash
    ./scripts/run.sh examples/file_validator
    ```

Changes take effect immediately (restart the agent to apply).

---

## Create Your Own Agent

=== "Windows"
    ```cmd
    scripts\new_agent.bat my_first_agent
    ```

=== "Linux / macOS"
    ```bash
    ./scripts/new_agent.sh my_first_agent
    ```

This creates:
```
agents/my_first_agent/
├── config.yaml          ← Edit this (define behavior)
├── AGENTS.md            ← Edit this (document purpose)
├── .env.example         ← Copy to .env, customize
├── setup.sh/.bat        ← Run to initialize
└── run.py               ← Don't edit (entry point)
```

Set up your agent:

=== "Windows"
    ```cmd
    cd agents\my_first_agent
    setup.bat
    notepad config.yaml
    ```

=== "Linux / macOS"
    ```bash
    cd agents/my_first_agent
    ./setup.sh
    vim config.yaml
    ```

Run it:

=== "Windows"
    ```cmd
    cd ../..
    scripts\run.bat my_first_agent
    ```

=== "Linux / macOS"
    ```bash
    cd ../..
    ./scripts/run.sh my_first_agent
    ```

---

## Key Takeaway

**Configuration-driven design means:**
- ✅ Change behavior by editing YAML
- ✅ No Python code changes needed
- ✅ Non-coders can customize agents
- ✅ Easy to understand what agent does
- ✅ Easy to version control changes

---

## Next: Deep Dive

Once you're comfortable, explore:

1. **How workflows work:** `docs/WORKFLOWS.md`
2. **Available tools:** `docs/TOOLS.md`
3. **System architecture:** `docs/ARCHITECTURE.md`
4. **Design decisions:** `docs/DESIGN_REASONING.md`

---

## Troubleshooting

### Agent won't start

Run setup again:

=== "Windows"
    ```cmd
    scripts\setup.bat
    ```

=== "Linux / macOS"
    ```bash
    ./scripts/setup.sh
    ```

### Directories not created

Create manually:

=== "Windows"
    ```cmd
    mkdir data\inbox data\processed data\errors
    mkdir logs
    ```

=== "Linux / macOS"
    ```bash
    mkdir -p data/{inbox,processed,errors} logs
    ```

### Logs not appearing

Check log file:

=== "Windows"
    ```cmd
    type logs\file_validator.log
    REM Or use tail-like tool:
    Get-Content -Wait logs\file_validator.log
    ```

=== "Linux / macOS"
    ```bash
    tail -f logs/file_validator.log
    ```

### More help

- **Windows Setup**: See `docs/SETUP_WINDOWS.md`
- **Linux/macOS Setup**: See `docs/SETUP_LINUX.md`
- **Path Reference**: See `docs/PATH_REFERENCE.md`
- **Agent Configuration**: See `docs/AGENT_SETUP.md`

---

**Congratulations!** You've built and tested an agent without writing a single line of Python code.

Next: `./scripts/new_agent.sh my_agent` to create your own.
