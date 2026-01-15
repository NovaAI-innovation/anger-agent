# System Architecture

## Overview

The agent framework consists of several interconnected subsystems working together to provide a configuration-driven agent runtime.

```
┌─────────────────────────────────────┐
│        Agent Main Loop              │
│  (runtime/agent.py)                 │
└──────────────┬──────────────────────┘
               │
       ┌───────┼────────┬──────────┐
       │       │        │          │
       ▼       ▼        ▼          ▼
   ┌─────┐ ┌────┐ ┌─────────┐ ┌──────────┐
   │Config│ │Tools│ │Triggers│ │Workflows │
   │Loader│ │Reg. │ │System  │ │Engine    │
   └─────┘ └────┘ └─────────┘ └──────────┘
       │       │        │          │
       └───────┼────────┼──────────┘
               │
            Hub
          (stub v0.1)
```

## Subsystems

### 1. Agent (runtime/agent.py)

**Role:** Main orchestrator and event loop

**Responsibilities:**
- Load configuration
- Set up logging
- Initialize all subsystems
- Run async event loop
- Handle signals (SIGINT, SIGTERM)
- Orchestrate trigger → workflow execution

**Design:**
- Single `Agent` class for all agent types
- `agent_type` in config determines execution mode
- Async event loop ready for v0.2+ features

**Entry Point:**
```python
agent = Agent(config_path="config.yaml")
agent.run_sync()  # Blocks until shutdown
```

### 2. Config Loader (runtime/config.py)

**Role:** Load and validate agent configuration

**Responsibilities:**
- Parse config.yaml (YAML → Python dict)
- Load AGENTS.md (documentation)
- Validate required fields
- Interpolate environment variables
- Provide typed accessors for config values

**Design:**
- `ConfigError` exceptions with helpful messages
- Fail fast on invalid config
- Lazy property access (don't compute until needed)
- Supports nested key access via `get()`

**Usage:**
```python
config = Config("config.yaml", "AGENTS.md")
agent_id = config.agent_id
triggers = config.triggers
workflows = config.workflows
```

### 3. Trigger System (runtime/triggers.py)

**Role:** Detect events and fire workflows

**Responsibilities:**
- Register all triggers from config
- Listen for events (file changes, messages, schedules)
- Match events to trigger definitions
- Route events to workflow execution

**v0.1 Trigger Types:**
- `file_watch` - Monitor directory for file changes

**v0.5 Trigger Types (future):**
- `message` - Receive from other agents via hub
- `schedule` - Run on cron schedule

**Design:**
- `TriggerSystem` owns all event listeners
- `TriggerHandler` converts OS events → trigger events
- Uses watchdog library for file system monitoring
- Async callback when trigger fires

**Usage:**
```python
trigger_system = TriggerSystem(logger)
trigger_system.register_trigger(trigger_def)
await trigger_system.start(callback_fn)
```

### 4. Tool System (runtime/tools.py)

**Role:** Provide reusable capabilities for workflows

**Responsibilities:**
- Register all available tools
- Execute tools with parameters
- Handle tool errors gracefully
- Provide tool discovery/introspection

**Built-in Tools (v0.1):**
- File: `file.read`, `file.write`, `file.move`, `file.find`
- JSON: `json.parse`, `json.validate`, `json.stringify`
- Logging: `log`
- Messaging: `message.send` (stub)

**Design:**
- `Tool` class wraps functions with metadata
- `ToolRegistry` stores tools by name
- Async execution (`await tool.execute(params)`)
- Consistent error handling

**Usage:**
```python
registry = ToolRegistry()
result = await registry.execute("file.read", {"path": "/path"})
```

### 5. Workflow Engine (runtime/workflows.py)

**Role:** Execute workflows step by step

**Responsibilities:**
- Load workflow from config
- Create execution context
- Execute steps in sequence
- Handle conditionals (if/then/else)
- Perform variable interpolation
- Handle errors per step's `on_error` setting

**Design:**
- `WorkflowContext` maintains state during execution
- `WorkflowEngine` orchestrates step execution
- Supports:
  - Tool invocation
  - Conditional branching
  - Error handling (fail, skip, retry)
  - Variable interpolation

**Step Execution Flow:**
```
1. Load step definition from workflow
2. Interpolate variables in params
3. Execute tool
4. Store output
5. Check on_error if failed
6. Return to next step
```

**Usage:**
```python
engine = WorkflowEngine(tool_registry, logger)
context = WorkflowContext("workflow_id", trigger_data)
result = await engine.execute_workflow("workflow_id", workflow_def, context)
```

### 6. Logger (runtime/logger.py)

**Role:** Structured logging with audit trail

**Responsibilities:**
- Set up logging (console + file)
- Format logs (readable for console, JSON for file)
- Include context (agent_id, step, action) in all logs
- Rotate log files to prevent disk bloat

**Design:**
- Console: Simple text format (human-readable)
- File: JSON format (machine-parseable)
- Structured fields: timestamp, level, agent_id, message
- Auto-rotation: Max 10MB per file, keep 5 backups

**Usage:**
```python
logger = setup_logger(agent_id, log_file, log_level)
logger.info("Agent started")
log_step_execution(logger, step_id, action, status, details)
```

### 7. Hub Connector (runtime/hub.py)

**Role:** Interface to agent mesh (v0.5 feature)

**Responsibilities (v0.5):**
- Connect to hub via WebSocket
- Send messages to other agents
- Receive messages from other agents
- Authenticate via seed phrase

**Current Status (v0.1):**
- Stub implementation
- Validates hub config exists
- Logs messages instead of sending
- v0.5 will implement actual connection

**Design:**
- `HubConnector` provides consistent interface
- Ready for async WebSocket implementation
- Config-driven (hub address, credentials)

---

## Data Flow

### Startup

```
User runs: python run.py
    ↓
Agent.__init__()
    ├─ Config.load(config.yaml)
    ├─ setup_logger()
    ├─ ToolRegistry()
    ├─ WorkflowEngine()
    ├─ TriggerSystem()
    │  └─ register_trigger() for each trigger
    └─ HubConnector()
    ↓
Agent.run_sync()
    ↓
await Agent.run()
    ├─ await hub_connector.initialize()
    ├─ await trigger_system.start(on_trigger_callback)
    └─ while running: await asyncio.sleep()
```

### Event Processing

```
File appears: /tmp/agent_inbox/data.json
    ↓
TriggerHandler.on_created(event)
    ├─ Check path matches
    ├─ Check pattern matches
    ├─ asyncio.create_task(fire_trigger())
    └─ (non-blocking)
    ↓
Agent._on_trigger(trigger_event)
    ├─ TriggerSystem.match_trigger(event)
    │  └─ Find which trigger definition matches
    ├─ TriggerSystem.get_trigger_workflow(trigger_id)
    │  └─ Get workflow_id from trigger
    ├─ Load workflow definition from config
    ├─ Create WorkflowContext(workflow_id, trigger_event)
    └─ await workflow_engine.execute_workflow()
        ├─ For each step:
        │  ├─ Interpolate variables
        │  ├─ Execute tool
        │  ├─ Store output
        │  └─ Handle errors
        ├─ Log workflow result
        └─ Return to event loop
```

---

## Design Patterns

### 1. Configuration Over Code

Everything is defined in `config.yaml`, not Python:
- Triggers: What events cause workflows?
- Workflows: What steps execute?
- Tools: What capabilities are available?

### 2. Async-First

All major operations use `async/await`:
- Trigger callbacks
- Tool execution
- Workflow execution
- (Ready for v0.2+ with LLM calls, hub messages)

### 3. Consistent Error Handling

Each step has `on_error` policy:
- `fail`: Stop workflow
- `skip`: Skip step, continue
- `retry`: Retry step
- `escalate_to_llm`: Escalate (v0.2+)

### 4. Variable Interpolation

Dynamic data via `${variable}` syntax:
- `${trigger.*}` - Event data
- `${step_output.*}` - Previous step results
- `${environment.*}` - Environment variables
- `${config.*}` - Config values

### 5. Structured Logging

Every action logged with context:
- Agent ID
- Workflow ID
- Step ID
- Action taken
- Result (success/failure)
- Duration

---

## Extension Points

### Adding Custom Tools

```python
# tools/my_tool.py
def my_function(params):
    return {"result": process(params)}

# config.yaml
tools:
  - name: "custom.my_function"
    enabled: true
    custom_module: "tools.my_tool"
    custom_function: "my_function"
```

### Adding Trigger Types

Extend `TriggerSystem._setup_*_triggers()` and `TriggerHandler`:

```python
# v0.2: Message triggers
await trigger_system._setup_message_triggers(...)

# v0.2: Schedule triggers
await trigger_system._setup_schedule_triggers(...)
```

### Adding Execution Modes

Update `Agent.run()` to support new `agent_type`:

```python
if self.config.agent_type == "llm_inference":
    executor = LLMExecutor(...)
elif self.config.agent_type == "hybrid":
    executor = HybridExecutor(...)
```

---

## Performance Characteristics (v0.1)

| Operation | Latency | Notes |
|-----------|---------|-------|
| Agent startup | < 1 sec | Load config, init subsystems |
| File detection | < 500ms | Watchdog event → callback |
| Workflow execution | 50-200ms | Depends on tool complexity |
| Tool execution | 10-100ms | File I/O, JSON parsing |
| Logging | < 50ms | Both console and file |

---

## Testing Strategy

### Unit Tests (runtime/*)
- Test each subsystem in isolation
- Mock dependencies
- Test error cases

### Integration Tests (tests/test_integration.py)
- Test full workflow: trigger → execution → result
- Use real config and example files
- Verify end-to-end behavior

### Manual Testing (examples/)
- Run example agents
- Drop test files
- Verify output

---

## Future Architecture (v0.2+)

### v0.2: Add LLM Inference Mode
```
LLMExecutor
    ├─ Build prompt from AGENTS.md
    ├─ Call LLM API
    ├─ LLM selects tools
    └─ Execute LLM's tool calls
```

### v0.3: Add Hybrid Mode
```
HybridExecutor
    ├─ Try workflow first (fast)
    ├─ If fails and recoverable:
    │  └─ Escalate to LLM
    └─ Return result
```

### v0.5: Add Hub Integration
```
HubConnector (real implementation)
    ├─ WebSocket to hub
    ├─ Send/receive messages
    └─ Process remote triggers
```

---

*For design reasoning, see DESIGN_REASONING.md*
*For workflow syntax, see WORKFLOWS.md*
*For tool reference, see TOOLS.md*
