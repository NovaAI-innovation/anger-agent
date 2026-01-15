# Agent: File Validator

## Purpose
Validates JSON data files against a schema and organizes them into appropriate directories.

## What This Agent Does

This agent monitors a file directory (by default `/tmp/agent_inbox`) for new JSON files.

When a file appears:

1. **Reads** the file contents
2. **Parses** it as JSON
3. **Validates** it against a schema (`schema.json`)
4. **If valid:**
   - Moves file to `/tmp/agent_processed/`
   - Logs success to output log
5. **If invalid:**
   - Writes error details to `/tmp/agent_errors/`
   - Logs validation errors for review

## Example Workflow

### Valid File

```
File appears: user.json
Contents: {"id": 1, "name": "Alice", "email": "alice@example.com"}

Agent processes:
├─ Read: ✓ Success
├─ Parse JSON: ✓ Success
├─ Validate: ✓ Success (all required fields present)
├─ Move to /tmp/agent_processed/user.json
└─ Log: ✓ Validated successfully
```

### Invalid File

```
File appears: incomplete.json
Contents: {"id": 1, "name": "Bob"}
(Missing 'email' field)

Agent processes:
├─ Read: ✓ Success
├─ Parse JSON: ✓ Success
├─ Validate: ✗ Failed (missing required field: email)
├─ Log error: /tmp/agent_errors/incomplete.json.log
└─ Log: ✗ Validation failed
```

## Configuration

See `config.yaml` for detailed settings:

- **Watched directory:** `INBOX_PATH` environment variable (default: `/tmp/agent_inbox`)
- **File patterns:** Configured to watch `*.json` files
- **Validation schema:** `schema.json` in this directory

## Tools Used

This agent uses the following built-in tools:

- **`file.read`** - Read file contents
- **`json.parse`** - Parse JSON string
- **`json.validate`** - Validate JSON against schema
- **`file.move`** - Move file to processed directory
- **`log`** - Write status to logs

See `docs/TOOLS.md` for full tool documentation.

## Schema Definition

The agent validates all JSON files against `schema.json`, which specifies:

- **Required fields:** `id`, `name`, `email`
- **Field types:**
  - `id`: integer
  - `name`: string
  - `email`: string (email format)

You can modify `schema.json` to validate different structures.

## How to Test

### 1. Start the Agent

```bash
cd agents/examples/file_validator
python run.py
```

### 2. Test with Valid Data

In another terminal:

```bash
echo '{"id": 1, "name": "Test User", "email": "test@example.com"}' > /tmp/agent_inbox/valid.json
```

Agent output:
```
INFO | Step[read_file] file.read → success
INFO | Step[parse_json] json.parse → success
INFO | Step[validate] json.validate → success
INFO | Moving valid.json → /tmp/agent_processed/
```

Check result:
```bash
ls /tmp/agent_processed/
# Output: valid.json
```

### 3. Test with Invalid Data

```bash
echo '{"id": 1, "name": "Test"}' > /tmp/agent_inbox/invalid.json
```

Agent output:
```
INFO | Step[read_file] file.read → success
INFO | Step[parse_json] json.parse → success
WARNING | Step[validate] json.validate → failed
INFO | Logging errors to /tmp/agent_errors/invalid.json.log
```

Check result:
```bash
cat /tmp/agent_errors/invalid.json.log
# Output: ["Missing required field: email"]
```

## Customization (No Python Code Needed!)

You can customize this agent by editing `config.yaml`:

### Change the Watched Directory

```yaml
environment:
  INBOX_PATH: "/your/path/here"
```

### Add More Workflow Steps

Edit `workflows.validate_and_process.steps` to add additional processing:

```yaml
workflows:
  validate_and_process:
    steps:
      # ... existing steps ...
      - id: "send_notification"
        action: "message.send"
        params:
          recipient: "admin"
          message: "File validated: ${trigger.file_name}"
```

### Modify Validation Schema

Edit `schema.json` to change what fields are required:

```json
{
  "required": ["id", "name"],
  "properties": {
    "id": {"type": "integer"},
    "name": {"type": "string"}
  }
}
```

**No Python changes needed!** Agent behavior is entirely driven by config.yaml.

## Design Principles

This agent demonstrates key framework principles:

1. **Configuration-driven:** All behavior in `config.yaml`
2. **Documentation-first:** `AGENTS.md` explains what agent does
3. **No code changes needed:** Customize via YAML only
4. **Composable workflows:** Steps combine simple tools
5. **Audit trail:** All actions logged

## Performance

- Agent startup: < 1 second
- File detection: < 500ms
- Validation: < 100ms
- Typical file processing: 50-200ms

## Troubleshooting

### Agent won't start

Check that directories exist:
```bash
mkdir -p /tmp/agent_inbox /tmp/agent_processed /tmp/agent_errors
```

### Files not being processed

Check that agent is still running:
```bash
ps aux | grep file_validator
```

Check logs:
```bash
tail -f /tmp/file_validator.log
```

### Validation always fails

Review `schema.json` to ensure it matches your data structure.

Check validation errors:
```bash
cat /tmp/agent_errors/*.log
```

## Next Steps

1. **Explore:** Try different JSON data to understand validation
2. **Customize:** Edit `config.yaml` to add more workflow steps
3. **Extend:** Create your own schema for different data
4. **Create Agent:** Use `./scripts/new_agent.sh` to create similar agent for different purpose

---

**Ready to create your own agent?** Copy this to a new directory and customize!
