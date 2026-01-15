# Agent Framework v0.1: Task Executor Base

A lightweight, configuration-driven agent framework where agent behavior is defined entirely through AGENTS.md (documentation) and config.yaml (behavior specification).

**Key Idea:** Non-coders customize agent behavior by editing YAML and Markdown files—no Python code changes needed.

---

## What Is This?

An agent is a runtime service that:
1. **Listens** for events (file changes, messages, schedules)
2. **Triggers** workflows when events occur
3. **Executes** workflow steps in sequence
4. **Logs** what it did

All of this is defined in your `config.yaml`. No Python modifications required.

---

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
./scripts/setup.sh
```

### 2. Run the Example Agent
```bash
./scripts/run.sh examples/file_validator
```

### 3. Test It
```bash
# In another terminal:
echo '{"id": 1, "name": "Test User", "email": "test@example.com"}' > /tmp/agent_inbox/valid.json

# Watch the agent process it:
# ✓ Valid file moves to /tmp/agent_processed/
# Check: ls -la /tmp/agent_processed/

# Now try invalid data:
echo '{"id": 1, "name": "Test User"}' > /tmp/agent_inbox/invalid.json

# Invalid file logged to errors:
# Check: cat /tmp/agent_errors/invalid.json.log
```

### 4. Create Your Own Agent
```bash
./scripts/new_agent.sh my_awesome_agent
# Edit agents/my_awesome_agent/config.yaml
# Edit agents/my_awesome_agent/AGENTS.md
./scripts/run.sh my_awesome_agent
```

---

## How It Works

### 1. **AGENTS.md** - The Soul
Plain English documentation of what your agent does:

```markdown
# Agent: File Validator

## Purpose
Validates JSON files against a schema

## What This Agent Does
- Watches /tmp/agent_inbox for new files
- Validates against schema
- Moves valid → /tmp/agent_processed
- Logs invalid → /tmp/agent_errors
```

### 2. **config.yaml** - The Brain
Declarative definition of behavior (triggers + workflows):

```yaml
agent_id: "file_validator"
agent_type: "task_executor"

triggers:
  - id: "new_json_file"
    type: "file_watch"
    path: "/tmp/agent_inbox"
    patterns: ["*.json"]
    workflow_id: "validate_and_process"

workflows:
  validate_and_process:
    steps:
      - id: "read_file"
        action: "file.read"
        params: {path: "${trigger.file_path}"}
        output: "content"

      - id: "validate"
        action: "json.validate"
        params:
          data: "${content}"
          schema_path: "./schema.json"
        output: "result"

      - id: "handle_result"
        action: "conditional"
        condition: "${result.valid} == true"
        if_true:
          - action: "file.move"
            params:
              source: "${trigger.file_path}"
              dest: "/tmp/agent_processed/${trigger.file_name}"
        if_false:
          - action: "log"
            params:
              message: "Invalid: ${result.errors}"
```

**That's it.** No Python code. Everything is YAML + Markdown.

---

## Project Structure

```
agent-framework/
├── README.md                          ← You are here
├── QUICKSTART.md                      (Detailed getting started)
├── requirements.txt                   (Python dependencies)
│
├── runtime/                           (Core agent runtime)
│   ├── __init__.py
│   ├── agent.py                       (Main event loop)
│   ├── config.py                      (Load/validate config.yaml)
│   ├── triggers.py                    (File watching, triggering)
│   ├── workflows.py                   (Workflow execution engine)
│   ├── tools.py                       (Tool registry + implementations)
│   ├── hub.py                         (Hub connector - stub)
│   ├── logger.py                      (Structured logging)
│   └── schemas/
│       └── config_schema.json         (Config validation)
│
├── agents/                            (Example agents + templates)
│   ├── _template/                     (Copy this to create new agent)
│   │   ├── config.yaml
│   │   ├── AGENTS.md
│   │   ├── schema.json
│   │   ├── tools/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   └── examples/
│       └── file_validator/            (Working example)
│           ├── config.yaml
│           ├── AGENTS.md
│           ├── schema.json
│           └── run.py
│
├── scripts/                           (User-friendly helpers)
│   ├── setup.sh                       (One-time setup)
│   ├── run.sh                         (Run any agent)
│   └── new_agent.sh                   (Generate new agent)
│
├── tests/                             (Test suite)
│   ├── test_config.py
│   ├── test_tools.py
│   ├── test_workflows.py
│   └── test_integration.py
│
├── docs/                              (Detailed documentation)
│   ├── ARCHITECTURE.md
│   ├── CREATE_AGENT.md
│   ├── WORKFLOWS.md
│   ├── TOOLS.md
│   ├── DESIGN_REASONING.md            (Why we made each decision)
│   └── FAQ.md
│
└── data/                              (Runtime data - created at startup)
    ├── inbox/
    ├── processed/
    └── errors/
```

---

## Core Concepts

### Triggers
Events that cause workflows to run:
- **File watch:** Detects new/modified files
- **Message:** Receives from other agents (future)
- **Schedule:** Runs on cron schedule (future)

### Workflows
Sequences of steps that execute when triggered:
```yaml
steps:
  - action: "tool_name"
    params: {...}
    output: "variable_name"
```

### Tools
Reusable capabilities agents can invoke:
- **file.read** - Read file contents
- **file.write** - Write to file
- **file.move** - Move file
- **json.parse** - Parse JSON
- **json.validate** - Validate against schema
- **log** - Write to log
- Custom tools (Python functions)

### Variables
Dynamic data available in workflows:
- `${trigger.file_path}` - Triggering event data
- `${step_output}` - Previous step results
- `${environment.VAR_NAME}` - Environment variables

---

## Example Use Cases

### 1. Data Processing Pipeline
Watch folder → Parse CSV → Transform → Load to DB

### 2. File Validation
Watch folder → Validate format → Move to appropriate directory

### 3. Data Enrichment
Receive message → Look up data → Enrich → Forward

### 4. Scheduled Cleanup
Run daily → Find old files → Delete → Log results

---

## Key Design Decisions

See `docs/DESIGN_REASONING.md` for detailed explanations of:
- Why configuration-driven (not code-driven)
- Why YAML for workflows (not Python DSL)
- Why variable interpolation with `${...}` syntax
- Why built-in tools system
- Why Task Executor first (not LLM)
- Why structured JSON logging

---

## Next Steps

1. **Run the example:** `./scripts/run.sh examples/file_validator`
2. **Read QUICKSTART.md:** 5-minute deep dive
3. **Create an agent:** `./scripts/new_agent.sh my_agent`
4. **Explore:** Edit config.yaml, see behavior change
5. **Learn:** Read docs/WORKFLOWS.md and docs/TOOLS.md

---

## Architecture at a Glance

```
Agent Startup
    ↓
Load config.yaml + validate
    ↓
Load AGENTS.md
    ↓
Initialize triggers (file watcher, etc.)
    ↓
EVENT LOOP
    ├─ Wait for trigger
    ├─ Match trigger to definition
    ├─ Fetch workflow
    ├─ FOR each step:
    │  ├─ Interpolate variables
    │  ├─ Execute tool
    │  ├─ Store output
    │  └─ Handle errors
    └─ Log result, return to waiting
```

---

## For Developers

### Adding Custom Tools
Create a Python function, register in config.yaml:

```python
# tools/my_custom_tool.py
def analyze_data(data):
    return {"score": len(data)}
```

```yaml
tools:
  - name: "custom.analyze_data"
    enabled: true
    custom_module: "tools.my_custom_tool"
    custom_function: "analyze_data"
```

### Extending the Runtime
The runtime is modular:
- `tools.py` - Add tool types
- `workflows.py` - Add action types
- `triggers.py` - Add trigger types

---

## Requirements

- Python 3.9+
- pyyaml
- watchdog
- python-json-logger

---

## Status

**v0.1 - Task Executor Base**
- ✅ File watching triggers
- ✅ Workflow execution
- ✅ Built-in tools
- ⏳ Message triggers (v0.2)
- ⏳ LLM Inference (v0.2)
- ⏳ Hub connectivity (v0.5)

---

## Documentation

- `QUICKSTART.md` - Get running in 5 minutes
- `docs/ARCHITECTURE.md` - System design
- `docs/WORKFLOWS.md` - How to write workflows
- `docs/TOOLS.md` - Available tools reference
- `docs/DESIGN_REASONING.md` - Why each decision was made
- `docs/CREATE_AGENT.md` - Create a new agent

---

## Get Help

- Read `docs/FAQ.md` for common questions
- Check `agents/examples/file_validator/` for a working example
- Review `agents/_template/README.md` for template guide

---

**Ready to build your first agent? Start with `./scripts/setup.sh`**
