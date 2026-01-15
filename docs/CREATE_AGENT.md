# Creating Your First Agent

This guide walks through creating a custom agent from scratch.

---

## Step 1: Generate from Template

```bash
./scripts/new_agent.sh my_data_processor
```

This creates:
```
agents/my_data_processor/
├── config.yaml          (Your agent's configuration)
├── AGENTS.md            (Your agent's documentation)
├── schema.json          (Optional: validation schema)
├── run.py               (Entry point - don't edit)
└── README.md            (Quick reference)
```

---

## Step 2: Define Your Agent (AGENTS.md)

Open `AGENTS.md` and describe your agent in plain English:

```markdown
# Agent: My Data Processor

## Purpose
Process CSV files and convert to JSON

## What This Agent Does

This agent monitors a directory for CSV files.

For each file:
1. Reads the CSV content
2. Parses as CSV
3. Converts to JSON
4. Saves to output directory

## How to Test

1. Start the agent:
   python run.py

2. Drop a CSV file:
   cp data.csv ./data/inbox/

3. Check output:
   ls ./data/processed/
```

---

## Step 3: Configure Your Agent (config.yaml)

Edit `config.yaml` to define behavior:

### 1. Change Agent Identity

```yaml
agent_id: "my_data_processor"   # Change this
agent_type: "task_executor"     # Keep as is
```

### 2. Define Trigger(s)

What events should trigger your agent?

```yaml
triggers:
  - id: "watch_csv"
    type: "file_watch"
    path: "/data/inbox"
    patterns: ["*.csv"]           # Watch for CSV files
    workflow_id: "process_csv"    # Execute this workflow
```

### 3. Define Workflow(s)

What should happen when triggered?

```yaml
workflows:
  process_csv:
    description: "Convert CSV to JSON"
    steps:
      - id: "read"
        action: "file.read"
        params: { path: "${trigger.file_path}" }
        output: "csv_content"

      - id: "parse"
        action: "csv.parse"  # (This tool doesn't exist yet in v0.1)
        params: { content: "${csv_content}" }
        output: "rows"

      - id: "to_json"
        action: "json.stringify"
        params: { data: "${rows}" }
        output: "json_string"

      - id: "save"
        action: "file.write"
        params:
          path: "/data/processed/${trigger.file_stem}.json"
          content: "${json_string}"

      - id: "log"
        action: "log"
        params:
          message: "Converted ${trigger.file_name} to JSON"
```

### 4. Enable Tools

Which built-in tools does your agent need?

```yaml
tools:
  - name: "file.read"
    enabled: true

  - name: "file.write"
    enabled: true

  - name: "json.stringify"
    enabled: true

  - name: "log"
    enabled: true

  - name: "message.send"
    enabled: false     # Not using this one
```

### 5. Set Up Logging

Where should logs go?

```yaml
logging:
  level: "info"
  file: "./my_data_processor.log"
```

---

## Step 4: Test Your Agent

### Start the Agent

```bash
./scripts/run.sh my_data_processor
```

You should see:
```
==================================================
Starting agent: my_data_processor
Config: agents/my_data_processor/config.yaml
==================================================

2025-01-15 10:30:45 | INFO | Agent starting: my_data_processor
2025-01-15 10:30:45 | INFO | Watching: /data/inbox for patterns: ['*.csv']
2025-01-15 10:30:45 | INFO | Ready for events...
```

### Trigger It

In another terminal:

```bash
# Create a test CSV file
cat > /data/inbox/test.csv << 'EOF'
name,age,email
Alice,30,alice@example.com
Bob,25,bob@example.com
EOF
```

### Check Results

Back in agent terminal, you should see:
```
2025-01-15 10:30:51 | INFO | Event: new file detected /data/inbox/test.csv
2025-01-15 10:30:51 | INFO | Executing workflow: process_csv
2025-01-15 10:30:51 | INFO | Step[read] file.read → success
2025-01-15 10:30:51 | INFO | Step[parse] csv.parse → success
2025-01-15 10:30:51 | INFO | Step[to_json] json.stringify → success
2025-01-15 10:30:51 | INFO | Step[save] file.write → success
2025-01-15 10:30:51 | INFO | Converted test.csv to JSON
```

Check output file:
```bash
cat /data/processed/test.json
```

---

## Step 5: Iterate and Improve

### Add More Workflow Steps

Want to process the data further?

```yaml
workflows:
  process_csv:
    steps:
      # ... existing steps ...

      - id: "enrich"
        action: "custom.enrich_data"
        params: { data: "${json_string}" }
        output: "enriched"

      - id: "save_enriched"
        action: "file.write"
        params:
          path: "/data/enriched/${trigger.file_stem}_enriched.json"
          content: "${enriched}"
```

### Add Conditional Logic

Want to handle different file types?

```yaml
workflows:
  process_csv:
    steps:
      # ... read step ...

      - id: "check_size"
        action: "conditional"
        condition: "${content_size} > 10000"
        if_true:
          - id: "log_large"
            action: "log"
            params:
              level: "warning"
              message: "Large file: ${trigger.file_name}"
        if_false:
          - id: "log_small"
            action: "log"
            params: { message: "Small file processed" }
```

### Add Custom Tools

Want to use custom Python logic?

```python
# agents/my_data_processor/tools.py
def enrich_data(params):
    """Add computed fields to data"""
    data = params.get("data")
    # Your custom logic here
    return enriched_data
```

Then register in config.yaml:

```yaml
tools:
  - name: "custom.enrich_data"
    enabled: true
    custom_module: "tools"
    custom_function: "enrich_data"
```

---

## Common Patterns

### Pattern 1: Validate File Before Processing

```yaml
workflows:
  process_file:
    steps:
      - id: "read"
        action: "file.read"
        params: { path: "${trigger.file_path}" }
        output: "content"

      - id: "validate"
        action: "json.validate"
        params:
          data: "${content}"
          schema_path: "/schemas/data.json"
        output: "validation"

      - id: "check_valid"
        action: "conditional"
        condition: "${validation.valid} == true"
        if_true:
          - id: "process"
            action: "log"
            params: { message: "Processing valid file" }
        if_false:
          - id: "reject"
            action: "log"
            params:
              level: "warning"
              message: "Invalid file: ${validation.errors}"
```

### Pattern 2: Organize Files by Status

```yaml
workflows:
  organize:
    steps:
      # ... validation ...
      - id: "organize"
        action: "conditional"
        condition: "${validation.valid} == true"
        if_true:
          - id: "move_valid"
            action: "file.move"
            params:
              source: "${trigger.file_path}"
              dest: "/valid/${trigger.file_name}"
        if_false:
          - id: "move_invalid"
            action: "file.move"
            params:
              source: "${trigger.file_path}"
              dest: "/invalid/${trigger.file_name}"
```

### Pattern 3: Process and Notify

```yaml
workflows:
  process_and_notify:
    steps:
      # ... processing ...
      - id: "notify_success"
        action: "message.send"
        params:
          recipient: "admin"
          message:
            event: "file_processed"
            file: "${trigger.file_name}"
            status: "success"
```

---

## Troubleshooting

### Agent Won't Start

**Check logs:**
```bash
tail -f ./my_data_processor.log
```

**Verify config:**
```bash
cat agents/my_data_processor/config.yaml
```

**Check Python installation:**
```bash
python3 --version
```

### Workflow Never Executes

**Verify trigger path exists:**
```bash
mkdir -p /data/inbox
```

**Check file pattern matches:**
```bash
# If pattern is "*.csv", file must end in .csv
# Correct: mydata.csv
# Incorrect: mydata.CSV (case sensitive on Linux)
```

### Tool Execution Fails

**Check tool is enabled:**
```yaml
tools:
  - name: "tool_name"
    enabled: true  # Must be true
```

**Check tool parameters:**
```yaml
# Compare with TOOLS.md documentation
- id: "step"
  action: "file.read"
  params:
    path: "/path"  # Required parameter
```

### Variables Undefined

**Check variable spelling:**
```yaml
# Correct: ${trigger.file_name}
# Incorrect: ${trigger.filename}  (underscore matters)
```

**Check variable exists:**
- Is there a previous step with `output: "variable_name"`?
- Is the step ID correct? `${step_id.output_var}`

---

## Next Steps

1. **Explore examples:** Look at `agents/examples/file_validator/`
2. **Read WORKFLOWS.md:** Understand workflow syntax better
3. **Read TOOLS.md:** See what tools are available
4. **Add custom tools:** Extend with Python for domain logic
5. **Create more agents:** Build agents for different purposes

---

## Quick Reference

**File structure:**
```
agents/my_agent/
├── config.yaml      ← Edit this
├── AGENTS.md        ← Edit this
├── schema.json      ← Create if needed
├── run.py           ← Don't edit
└── tools/           ← Create if needed
    └── __init__.py
```

**Config sections:**
- `agent_id` - Your agent's name
- `triggers` - What events trigger workflows
- `workflows` - What to do when triggered
- `tools` - Which tools to enable
- `logging` - Where to log output

**Workflow structure:**
- `steps` - List of actions
- `id` - Step identifier
- `action` - Tool name or "conditional"
- `params` - Tool parameters
- `output` - Store result in variable
- `on_error` - How to handle failure

**Variable references:**
- `${trigger.*}` - Event data
- `${step_id.output_var}` - Step output
- `${environment.VAR}` - Environment vars
- `${config.*}` - Config values

---

**Need more help?** See:
- WORKFLOWS.md - Workflow syntax
- TOOLS.md - Available tools
- ARCHITECTURE.md - How framework works
- DESIGN_REASONING.md - Why design is this way
