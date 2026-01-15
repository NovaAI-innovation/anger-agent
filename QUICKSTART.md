# Quick Start: 5 Minutes to Your First Agent

This guide gets you from zero to running an agent in 5 minutes.

---

## Step 1: Install (1 minute)

```bash
# Clone the repo (if you haven't already)
cd agent-framework

# Run setup script
./scripts/setup.sh
```

This creates directories and installs dependencies.

---

## Step 2: Run Example Agent (2 minutes)

```bash
# Start the file validator agent
./scripts/run.sh examples/file_validator
```

You should see:
```
2025-01-15 10:30:45 | INFO | Agent starting: file_validator
2025-01-15 10:30:45 | INFO | Watching: /tmp/agent_inbox
2025-01-15 10:30:45 | INFO | Ready for events...
```

The agent is now **watching `/tmp/agent_inbox` for JSON files**.

---

## Step 3: Test It (2 minutes)

**In another terminal:**

### Create a valid file:
```bash
echo '{"id": 1, "name": "Alice", "email": "alice@example.com"}' > /tmp/agent_inbox/valid.json
```

**In agent terminal:** You'll see:
```
2025-01-15 10:31:02 | INFO | Event: new file detected /tmp/agent_inbox/valid.json
2025-01-15 10:31:02 | INFO | Executing workflow: validate_and_process
2025-01-15 10:31:02 | INFO | Step: read_file → success
2025-01-15 10:31:02 | INFO | Step: parse_json → success
2025-01-15 10:31:02 | INFO | Step: validate → success (valid)
2025-01-15 10:31:02 | INFO | Moving valid.json → /tmp/agent_processed/
2025-01-15 10:31:02 | INFO | Workflow complete ✓
```

**Check results:**
```bash
ls /tmp/agent_processed/
# Output: valid.json
```

### Create an invalid file:
```bash
echo '{"id": 1, "name": "Bob"}' > /tmp/agent_inbox/invalid.json
# Missing 'email' field - violates schema
```

**In agent terminal:** You'll see:
```
2025-01-15 10:31:15 | INFO | Event: new file detected /tmp/agent_inbox/invalid.json
2025-01-15 10:31:15 | INFO | Executing workflow: validate_and_process
2025-01-15 10:31:15 | INFO | Step: read_file → success
2025-01-15 10:31:15 | INFO | Step: parse_json → success
2025-01-15 10:31:15 | INFO | Step: validate → FAILED (missing email field)
2025-01-15 10:31:15 | WARNING | Validation failed - logging to errors
2025-01-15 10:31:15 | INFO | Workflow complete ✗
```

**Check results:**
```bash
cat /tmp/agent_errors/invalid.json.log
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
      4. If valid: Move to /tmp/agent_processed/
      5. If invalid: Log errors to /tmp/agent_errors/
```

**Zero Python code.** Everything is YAML.

---

## Step 4: Customize It (Bonus - not in 5 min)

Now that you understand how it works, you can customize:

### Edit the workflow:
```bash
vim agents/examples/file_validator/config.yaml
```

Change anything:
- Add more workflow steps
- Modify validation logic
- Change output directories

### Edit the documentation:
```bash
vim agents/examples/file_validator/AGENTS.md
```

Describe what your agent does.

### Run it again:
```bash
./scripts/run.sh examples/file_validator
```

Changes take effect immediately.

---

## Create Your Own Agent

```bash
./scripts/new_agent.sh my_first_agent
```

This creates:
```
agents/my_first_agent/
├── config.yaml          ← Edit this (define behavior)
├── AGENTS.md            ← Edit this (document purpose)
├── schema.json          ← Edit this (change validation)
└── run.py               ← Don't edit (entry point)
```

Edit `config.yaml` to define your agent's triggers and workflows.

Run it:
```bash
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
```bash
./scripts/setup.sh
```

### Directories not created
```bash
mkdir -p /tmp/agent_inbox /tmp/agent_processed /tmp/agent_errors
```

### Logs not appearing
```bash
tail -f /tmp/file_validator.log
```

---

**Congratulations!** You've built and tested an agent without writing a single line of Python code.

Next: `./scripts/new_agent.sh my_agent` to create your own.
