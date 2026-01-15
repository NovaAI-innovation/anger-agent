# Workflows: Step-by-Step Task Execution

Workflows are the heart of what agents do. A workflow is a sequence of steps that execute when triggered.

---

## Basic Workflow Structure

```yaml
workflows:
  my_workflow:
    description: "What this workflow does"
    timeout_seconds: 60

    steps:
      - id: "step1"
        action: "tool_name"
        params:
          param1: "value"
          param2: "${variable}"
        output: "result_var"
        on_error: "fail"

      - id: "step2"
        action: "tool_name"
        params: {...}
```

**Components:**
- `id` - Unique step identifier (for logging)
- `action` - Tool to execute or action type (conditional, etc.)
- `params` - Parameters passed to tool
- `output` - Variable name to store result in
- `on_error` - What to do if step fails

---

## Step Types

### 1. Tool Invocation

Execute a registered tool:

```yaml
- id: "read_file"
  action: "file.read"
  params:
    path: "/path/to/file"
  output: "file_content"
```

**How it works:**
1. Find tool named "file.read"
2. Interpolate variables in params
3. Execute tool with params
4. Store result in "file_content"
5. Next steps can use `${file_content}`

### 2. Conditional (if/then/else)

Branch based on condition:

```yaml
- id: "check_valid"
  action: "conditional"
  condition: "${validation_result.valid} == true"

  if_true:
    - id: "success_step"
      action: "file.move"
      params: {...}

  if_false:
    - id: "error_step"
      action: "log"
      params: {...}
```

**Condition Syntax:**
- Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Variables: `${variable}`
- Examples:
  - `"${validation_result.valid} == true"`
  - `"${error_count} > 0"`
  - `"${status} == 'success'"`

**Nested Conditionals:**
```yaml
if_true:
  - id: "nested_check"
    action: "conditional"
    condition: "${other_result.value} == 'something'"
    if_true:
      # More steps
    if_false:
      # More steps
```

---

## Variable System

Variables store data that flows from step to step.

### Variable Types

**1. Trigger Data** - From the triggering event
```yaml
# Available as:
${trigger.file_path}       # Full path of file
${trigger.file_name}       # Just filename
${trigger.file_stem}       # Filename without extension
${trigger.type}            # Event type ("file_created")
```

**2. Step Outputs** - Results from previous steps
```yaml
# If step "read_file" outputs to "content":
${read_file.content}  # Use the output

# In workflow:
- id: "read_file"
  action: "file.read"
  params: { path: "${trigger.file_path}" }
  output: "content"

- id: "use_content"
  action: "some_tool"
  params: { data: "${read_file.content}" }  # Access here
```

**3. Environment Variables** - From config or OS
```yaml
# In config.yaml:
environment:
  INBOX_PATH: "/tmp/inbox"

# In workflow:
- id: "watch_inbox"
  action: "file.read"
  params: { path: "${environment.INBOX_PATH}/myfile" }
```

**4. Config Values** - From config.yaml
```yaml
# In config:
timeout_seconds: 60
max_retries: 3

# In workflow:
- id: "step"
  action: "log"
  params: { message: "Timeout: ${config.timeout_seconds}" }
```

### Accessing Nested Variables

For dictionaries/objects:
```yaml
# If step output is: { "user": { "id": 123, "name": "Alice" } }
${step_output.user}        # Whole object
${step_output.user.id}     # Nested field
${step_output.user.name}   # Another nested field
```

---

## Error Handling

Each step can handle failures differently:

### `on_error: "fail"` (default)

Stop workflow immediately:
```yaml
- id: "critical_step"
  action: "file.read"
  params: { path: "/critical/file" }
  on_error: "fail"  # If this fails, workflow stops
```

### `on_error: "skip"`

Skip this step, continue with next:
```yaml
- id: "optional_step"
  action: "file.read"
  params: { path: "/optional/file" }
  on_error: "skip"  # If fails, skip and continue
```

### `on_error: "retry"`

Retry the step:
```yaml
- id: "unreliable_api_call"
  action: "api.call"
  params: { url: "https://api.example.com/data" }
  on_error: "retry"  # Try again if fails
```

### `on_error: "escalate_to_llm"` (v0.2+)

Escalate to LLM reasoning (future):
```yaml
- id: "complex_decision"
  action: "some_tool"
  params: {...}
  on_error: "escalate_to_llm"  # Ask LLM if fails
```

---

## Real-World Examples

### Example 1: File Validation

```yaml
validate_and_process:
  steps:
    - id: "read"
      action: "file.read"
      params: { path: "${trigger.file_path}" }
      output: "content"
      on_error: "fail"

    - id: "parse"
      action: "json.parse"
      params: { content: "${content}" }
      output: "data"
      on_error: "fail"

    - id: "validate"
      action: "json.validate"
      params:
        data: "${data}"
        schema_path: "/schemas/user.json"
      output: "result"

    - id: "branch"
      action: "conditional"
      condition: "${result.valid} == true"
      if_true:
        - id: "move_valid"
          action: "file.move"
          params:
            source: "${trigger.file_path}"
            dest: "/processed/${trigger.file_name}"
      if_false:
        - id: "log_error"
          action: "log"
          params:
            level: "warning"
            message: "Invalid file: ${result.errors}"
```

### Example 2: Data Transformation

```yaml
transform_data:
  steps:
    - id: "read"
      action: "file.read"
      params: { path: "${trigger.file_path}" }
      output: "content"

    - id: "parse"
      action: "json.parse"
      params: { content: "${content}" }
      output: "data"

    - id: "transform"
      action: "custom.transform_user"
      params: { user: "${data}" }
      output: "transformed"

    - id: "save"
      action: "file.write"
      params:
        path: "/output/${trigger.file_stem}_processed.json"
        content: "${transformed}"

    - id: "notify"
      action: "log"
      params:
        message: "Transformed: ${trigger.file_name}"
```

### Example 3: Multi-Step Processing

```yaml
process_order:
  steps:
    - id: "read_order"
      action: "file.read"
      params: { path: "${trigger.file_path}" }
      output: "order_json"

    - id: "parse_order"
      action: "json.parse"
      params: { content: "${order_json}" }
      output: "order"

    - id: "check_status"
      action: "conditional"
      condition: "${order.status} == 'pending'"
      if_true:
        - id: "validate_items"
          action: "json.validate"
          params:
            data: "${order.items}"
            schema_path: "/schemas/items.json"
          output: "items_valid"

        - id: "check_items"
          action: "conditional"
          condition: "${items_valid.valid} == true"
          if_true:
            - id: "confirm_order"
              action: "message.send"
              params:
                recipient: "order_processor"
                message: { order_id: "${order.id}", status: "confirmed" }
          if_false:
            - id: "reject_order"
              action: "message.send"
              params:
                recipient: "order_processor"
                message: { order_id: "${order.id}", status: "rejected", reason: "Invalid items" }

      if_false:
        - id: "skip_processing"
          action: "log"
          params: { message: "Order not pending, skipping" }
```

---

## Best Practices

### 1. Clear Step IDs

Use descriptive, snake_case IDs:
```yaml
✓ Good:  id: "read_input_file"
✗ Bad:   id: "step1"

✓ Good:  id: "validate_schema"
✗ Bad:   id: "v"
```

### 2. Use Outputs for Each Step

Store meaningful results:
```yaml
- id: "parse"
  action: "json.parse"
  params: { content: "${content}" }
  output: "parsed_data"  # ✓ Will use later

- id: "validate"
  action: "json.validate"
  params: { data: "${parsed_data}" }
  # output: missing  # ✗ If you need result, specify it
```

### 3. Meaningful Conditionals

Make conditions easy to understand:
```yaml
✓ Good:
condition: "${validation_result.valid} == true"

✗ Bad:
condition: "${result.v} == 1"
```

### 4. Error Handling

Choose appropriate error strategy:
```yaml
# Critical step: fail fast
- id: "read_config"
  action: "file.read"
  on_error: "fail"

# Optional step: skip if missing
- id: "read_optional_data"
  action: "file.read"
  on_error: "skip"

# Unreliable step: retry
- id: "api_call"
  action: "api.call"
  on_error: "retry"
```

### 5. Avoid Deep Nesting

Keep conditionals readable:
```yaml
# ✓ OK - two levels
- action: "conditional"
  if_true:
    - action: "tool"
    - action: "conditional"  # Nested once
      if_true:
        - action: "tool"

# ✗ Avoid - too deep
- action: "conditional"
  if_true:
    - action: "conditional"
      if_true:
        - action: "conditional"  # Three levels
          if_true:
            - action: "tool"
```

---

## Troubleshooting

### "Undefined variable" Error

**Problem:** Workflow uses `${variable}` that doesn't exist

**Solutions:**
- Check variable name is spelled correctly
- Make sure previous step set `output:`
- Check step ID matches (e.g., `${read_file.content}`)
- For trigger data, use correct trigger type (e.g., `file_watch` provides `${trigger.file_path}`)

### "Tool not found" Error

**Problem:** Workflow references tool that isn't registered

**Solutions:**
- Check tool name in workflow matches config
- Make sure tool is enabled in `tools` section
- Check tool is registered in runtime

### "Invalid condition" Error

**Problem:** Conditional syntax is wrong

**Solutions:**
- Use proper operators: `==`, `!=`, `>`, `<`
- Quote string values: `"${field} == 'value'"` ✓
- Don't use `&&` or `||` (not supported in v0.1)
- Simple conditions only: `"${a} == 'b"` not `"${a} == 'b' and ${c} == 'd'"`

### Workflow Never Completes

**Problem:** Workflow seems to hang

**Solutions:**
- Check logs for step that's running
- Verify `timeout_seconds` in workflow
- Check if tool is blocking (v0.1 doesn't handle blocked I/O well)

---

## Workflow Testing

### Manual Testing

```bash
# Start agent
./scripts/run.sh my_agent

# In another terminal, trigger event:
# For file_watch:
cp /tmp/test.json /tmp/agent_inbox/

# Check logs:
tail -f /tmp/my_agent.log

# Check output:
ls -la /tmp/agent_processed/
```

### Log Inspection

Logs show step-by-step execution:

```
2025-01-15 10:30:01 | INFO | Executing workflow: validate_and_process
2025-01-15 10:30:01 | INFO |   Step: read_file
2025-01-15 10:30:01 | INFO | Step[read_file] file.read → success
2025-01-15 10:30:01 | INFO |   Step: validate
2025-01-15 10:30:01 | WARNING | Step[validate] json.validate → failed
2025-01-15 10:30:01 | INFO |   Workflow complete (failed)
```

---

## v0.2+ Future Features

- **For loops:** `action: "for_each"`
- **Call other workflows:** `action: "workflow.call"`
- **Try/catch:** `action: "try_catch"`
- **Parallel execution:** Multiple steps at once
- **Custom actions:** Plugins for domain-specific logic

---

For tool reference, see TOOLS.md
For architecture, see ARCHITECTURE.md
For design decisions, see DESIGN_REASONING.md
