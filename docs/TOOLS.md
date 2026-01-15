# Tools Reference

Tools are reusable capabilities that workflows can invoke. This document lists all available tools with their parameters and return values.

---

## File Tools

### file.read

Read entire file contents as string.

**Parameters:**
- `path` (string, required) - Path to file to read

**Returns:**
- (string) - File contents

**Example:**
```yaml
- id: "read_file"
  action: "file.read"
  params:
    path: "/path/to/file.txt"
  output: "content"
```

**Error Handling:**
- Fails if file doesn't exist
- Use `on_error: "skip"` if file is optional

---

### file.write

Write content to file (creates if missing, overwrites if exists).

**Parameters:**
- `path` (string, required) - Path to file to write
- `content` (string, required) - Content to write

**Returns:**
```json
{
  "written_bytes": 1234
}
```

**Example:**
```yaml
- id: "write_file"
  action: "file.write"
  params:
    path: "/path/to/output.txt"
    content: "Hello world"
  output: "result"
```

**Notes:**
- Creates parent directories automatically
- Overwrites existing files without warning
- Use `file.move` if you need to preserve original

---

### file.move

Move or rename file from source to destination.

**Parameters:**
- `source` (string, required) - Source file path
- `dest` (string, required) - Destination file path

**Returns:**
```json
{
  "source": "/path/to/old",
  "dest": "/path/to/new"
}
```

**Example:**
```yaml
- id: "organize"
  action: "file.move"
  params:
    source: "${trigger.file_path}"
    dest: "/archive/${trigger.file_name}"
  output: "moved"
```

**Notes:**
- Creates destination directories automatically
- Overwrites destination if it exists
- Use for moving files between folders or renaming

---

### file.find

Find files matching glob pattern.

**Parameters:**
- `path` (string, required) - Directory to search
- `pattern` (string, default: "*") - Glob pattern to match

**Returns:**
```json
[
  "/path/to/file1.txt",
  "/path/to/file2.txt"
]
```

**Example:**
```yaml
- id: "find_logs"
  action: "file.find"
  params:
    path: "/logs"
    pattern: "*.log"
  output: "log_files"
```

**Pattern Syntax:**
- `*` - Match any characters
- `?` - Match single character
- `[abc]` - Match a, b, or c
- `**` - Match directories recursively

---

## JSON Tools

### json.parse

Parse JSON string to Python object.

**Parameters:**
- `content` (string, required) - JSON string to parse

**Returns:**
- (dict/list/etc) - Parsed JSON object

**Example:**
```yaml
- id: "parse"
  action: "json.parse"
  params:
    content: "${file_content}"
  output: "data"
```

**Usage:**
```yaml
# Now you can access fields:
- id: "use_data"
  action: "log"
  params:
    message: "User ID: ${data.user_id}"
```

**Error Handling:**
- Fails if JSON is invalid
- Use `on_error: "fail"` for required data

---

### json.validate

Validate JSON data against schema.

**Parameters:**
- `data` (dict, required) - Data to validate
- `schema_path` (string, required) - Path to JSON schema file

**Returns:**
```json
{
  "valid": true|false,
  "errors": ["error1", "error2"],
  "recoverable": true|false
}
```

**Example:**
```yaml
- id: "validate"
  action: "json.validate"
  params:
    data: "${parsed_json}"
    schema_path: "/schemas/user.json"
  output: "validation"
```

**Schema Format:**
```json
{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "name": {"type": "string"},
    "email": {"type": "string"}
  },
  "required": ["id", "name", "email"]
}
```

**Validation Checks:**
- Required fields present?
- Unknown fields present?
- Field types match?

---

### json.stringify

Convert Python object to JSON string.

**Parameters:**
- `data` (dict/list/etc, required) - Object to convert

**Returns:**
- (string) - JSON string

**Example:**
```yaml
- id: "to_json"
  action: "json.stringify"
  params:
    data: ${parsed_data}
  output: "json_string"
```

---

## Logging Tools

### log

Write message to agent log.

**Parameters:**
- `message` (string, required) - Message to log
- `level` (string, default: "info") - Log level

**Returns:**
```json
{
  "logged": "message text"
}
```

**Log Levels:**
- `debug` - Detailed debugging information
- `info` - General information
- `warning` - Warning about potential issue
- `error` - Error that occurred

**Example:**
```yaml
- id: "log_success"
  action: "log"
  params:
    level: "info"
    message: "File processed: ${trigger.file_name}"

- id: "log_error"
  action: "log"
  params:
    level: "warning"
    message: "Validation failed: ${validation_result.errors}"
```

**Notes:**
- Logs appear in console and log file
- Use appropriate level for filtering

---

## Messaging Tools

### message.send

Send message to another agent.

**Parameters:**
- `recipient` (string, required) - Target agent ID
- `message` (dict, required) - Message payload

**Returns:**
```json
{
  "recipient": "other_agent",
  "message": { ... },
  "status": "queued_for_hub"
}
```

**Example:**
```yaml
- id: "notify_processor"
  action: "message.send"
  params:
    recipient: "data_processor"
    message:
      action: "process_file"
      file_path: "/processed/data.json"
  output: "sent"
```

**Status (v0.1):**
- `queued_for_hub` - Message queued (hub not connected in v0.1)

**Status (v0.5):**
- `sent` - Message delivered to agent
- `failed` - Agent not reachable

**Notes:**
- v0.1: Messages are logged only (hub not connected)
- v0.5: Will actually send via hub
- Use for coordination between agents

---

## Tool Availability

### Enabling Tools

In `config.yaml`, enable/disable tools:

```yaml
tools:
  - name: "file.read"
    enabled: true      # Can use in workflows

  - name: "file.write"
    enabled: false     # Cannot use
```

### Using Tools

In workflows, call by name:

```yaml
- id: "read"
  action: "file.read"  # Must match tool name exactly
  params:
    path: "/path"
```

---

## Custom Tools

### Creating Custom Tools

Create Python function:

```python
# tools/my_tools.py
def analyze_data(params):
    """Analyze data and return insights"""
    data = params.get("data")
    if not data:
        raise ValueError("Missing 'data' parameter")

    return {
        "count": len(data),
        "type": type(data).__name__
    }
```

### Registering Custom Tools

In `config.yaml`:

```yaml
tools:
  - name: "custom.analyze"
    enabled: true
    custom_module: "tools.my_tools"
    custom_function: "analyze_data"
```

### Using Custom Tools

In workflows:

```yaml
- id: "analyze"
  action: "custom.analyze"
  params:
    data: ${my_data}
  output: "analysis"
```

---

## Error Handling

### Tool Failures

When tool fails (parameters invalid, file missing, etc.):

```yaml
- id: "read"
  action: "file.read"
  params: { path: "/nonexistent" }
  on_error: "fail"      # Stop workflow
  # OR
  on_error: "skip"      # Skip step, continue
  # OR
  on_error: "retry"     # Try again
```

### Checking Results

After tool execution, check for errors:

```yaml
- id: "read"
  action: "file.read"
  params: { path: "/path" }
  output: "content"

- id: "check_read"
  action: "conditional"
  condition: "${content} != ''"
  if_true:
    - id: "use_content"
      action: "log"
      params: { message: "${content}" }
  if_false:
    - id: "file_empty"
      action: "log"
      params:
        level: "warning"
        message: "File was empty"
```

---

## Performance Tips

### 1. Use Appropriate Error Handling
- Use `on_error: "skip"` for optional steps (faster failure)
- Use `on_error: "retry"` for flaky operations
- Use `on_error: "fail"` only for critical steps

### 2. Cache Results
- Store tool outputs in variables, reuse them
- Don't call same tool multiple times

```yaml
# Good: Read once, use twice
- id: "read"
  action: "file.read"
  params: { path: "/data" }
  output: "content"

- id: "parse"
  action: "json.parse"
  params: { content: "${content}" }  # Reuse

- id: "analyze"
  action: "custom.analyze"
  params: { data: "${content}" }  # Reuse again

# Bad: Read multiple times
- id: "parse"
  action: "json.parse"
  params: { content: "${file_read.output}" }
  # Where file_read was called 3 times
```

### 3. Use Patterns Efficiently
- `file.find` with specific patterns
- `*.json` faster than `*`

---

## v0.2+ Tools (Coming Soon)

- `api.call` - Make HTTP requests
- `csv.parse` - Parse CSV files
- `database.query` - Query databases
- `crypto.hash` - Hash data
- Custom actions defined in AGENTS.md

---

For workflow examples using tools, see WORKFLOWS.md
For architecture details, see ARCHITECTURE.md
