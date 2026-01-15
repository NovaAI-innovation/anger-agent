# Design Reasoning: v0.1 Architecture Decisions

This document explains WHY each architectural decision was made, not just WHAT was built.

---

## Core Principle: Configuration-Driven Design

### Decision
All agent behavior is defined in `config.yaml` and `AGENTS.md`, not in Python code.

### Reasoning
1. **Non-coder accessibility:** Teams without Python expertise can customize agents
2. **Reduced maintenance:** Changes don't require code review/testing/deployment
3. **Version control clarity:** Changes to behavior appear as config diffs, not code diffs
4. **Safety:** Users can't accidentally break the runtime, only modify configuration
5. **Auditability:** Easy to see what changed and when

### Trade-offs
- ❌ Less powerful (can't express arbitrary logic in config)
- ❌ More verbose for complex workflows (vs. Python)
- ✅ But 95% of real agent workflows don't need arbitrary logic
- ✅ Can always add custom tools for edge cases

### Implementation
- `config.yaml` uses YAML for declarative syntax
- Workflows are sequences of tool invocations with conditionals
- Variable interpolation (`${variable}`) for dynamic data

---

## Choice 1: YAML for Workflows (Not Python DSL)

### Decision
Use YAML for workflow definition instead of embedded Python DSL.

### Reasoning
1. **Familiar syntax:** JSON/YAML are familiar to non-coders
2. **Visual structure:** Indentation shows nesting (clearer than code)
3. **Validation:** Can validate YAML structure before execution
4. **Version control:** YAML diffs are human-readable
5. **Tool independence:** Works with any language runtime (future multi-lang)

### Trade-offs
- ❌ Can't express arbitrary logic (limited to conditionals, loops)
- ❌ More verbose for simple operations
- ✅ But clarity matters more than conciseness for non-coders
- ✅ Complex logic can use custom tools

### Alternative Considered
- **Python DSL:** `@workflow def my_workflow(): read(); validate()...`
  - Pro: Powerful
  - Con: Requires Python knowledge, harder to audit

---

## Choice 2: Variable Interpolation with `${}` Syntax

### Decision
Use `${variable_name}` for variable interpolation throughout config.

### Reasoning
1. **Familiar:** Users know this from bash/templating languages
2. **Unambiguous:** Clear what's a variable vs. literal string
3. **Searchable:** `${` is unique, easy to grep
4. **Nested access:** `${trigger.file_path}` for dictionary traversal
5. **Escapable:** Can use `\$` if you need literal `$`

### Trade-offs
- ❌ Special syntax to learn
- ✅ But familiar from bash (most users know it)
- ✅ Worth it for clarity

### Alternative Considered
- **Mustache syntax:** `{{variable}}` (used by other frameworks)
  - Pro: Also familiar
  - Con: Less clear for command substitution (could look like code)

- **Implicit interpolation:** All strings are templates
  - Pro: No special syntax
  - Con: Can't use literal strings with special meanings

---

## Choice 3: Built-in Tool System (Not Pure Functions)

### Decision
Implement a tool registry with built-in tools rather than Python functions.

### Reasoning
1. **Consistency:** All tools have same interface (name, params, output)
2. **Discoverability:** Can list/inspect tools at runtime
3. **LLM-ready:** Tools have schemas, can be called by LLM (v0.2)
4. **Extensibility:** Custom tools register same way as built-ins
5. **Decoupling:** Tools are independent of runtime

### Trade-offs
- ❌ More infrastructure (Tool, ToolRegistry classes)
- ✅ Worth it for composability and future LLM support

### Built-in Tools Philosophy
- Core: `file.*`, `json.*`, `log.*` (cover 80% of use cases)
- Others: `message.*` (stub for v0.5)
- Custom: Users add via tool modules

---

## Choice 4: Async/Await Throughout (Even Though v0.1 Doesn't Need It)

### Decision
Use async/await even though v0.1 doesn't need non-blocking I/O.

### Reasoning
1. **Future-ready:** v0.2+ will need it (LLM calls, hub messages)
2. **Consistency:** Don't want to refactor later
3. **Non-blocking file watcher:** Watchdog library is thread-based; async lets us integrate cleanly
4. **Performance:** Prepared for high-throughput deployments

### Trade-offs
- ❌ Adds complexity (async syntax, asyncio loops)
- ✅ But necessary for production scalability
- ✅ Python 3.9+ makes it manageable

---

## Choice 5: File Watcher Only in v0.1 (Not Message Triggers)

### Decision
Support only file_watch triggers in v0.1. Message triggers come in v0.5 (hub integration).

### Reasoning
1. **Testability:** File watching is easy to test (drop files, see results)
2. **Simplicity:** Hub dependency deferred to v0.5
3. **Use case:** Most agent data pipelines are file-based anyway
4. **Clear progression:** v0.1 (file) → v0.5 (messages)

### Trade-offs
- ❌ Can't test multi-agent communication in v0.1
- ✅ Keeps v0.1 scope manageable
- ✅ File validator is more useful than echo agent

---

## Choice 6: Task Executor First (Not LLM Inference)

### Decision
Implement Task Executor only in v0.1. LLM modes come in v0.2+.

### Reasoning
1. **Clarity:** Users understand explicit workflows
2. **Cost:** No API costs during development/testing
3. **Testability:** Deterministic behavior (same input → same output)
4. **Simplicity:** Workflow engine simpler than LLM integration
5. **Validation:** Proves config-driven approach before adding complexity

### Trade-offs
- ❌ Less powerful (can't reason about novel situations)
- ✅ Sufficient for 95% of automation tasks
- ✅ Can add LLM in v0.2 without major refactoring

---

## Choice 7: Structured JSON Logging

### Decision
Log in JSON format (machine-parseable) while printing readable text to console.

### Reasoning
1. **Production-ready:** JSON logs are queryable/filterable
2. **Debugging:** File logs include full context (agent_id, step, status)
3. **Usability:** Console output is human-readable
4. **Auditability:** All actions permanently logged
5. **Monitoring:** Tools can parse logs for metrics

### Implementation
- Console: Simple text format (easy to read)
- File: JSON format (easy to parse)
- Rotation: Prevent disk bloat with log rotation

---

## Choice 8: Hub as Stub in v0.1

### Decision
Include hub configuration in v0.1, but actual connection comes in v0.5.

### Reasoning
1. **Consistency:** config.yaml is future-proof
2. **No surprises:** Users see hub config early
3. **Scaffolding:** v0.5 hub implementation starts with this stub
4. **Separation:** v0.1 focus is on single-agent Task Executor

### Trade-offs
- ❌ Users might expect hub to work in v0.1
- ✅ But docs clearly mark it as v0.5 feature
- ✅ Config is ready for v0.5 implementation

---

## Choice 9: Minimal Dependencies

### Decision
Only depend on: pyyaml, watchdog, python-json-logger

### Reasoning
1. **Lightweight:** Framework doesn't bloat user's environment
2. **Stability:** Fewer dependencies = fewer version conflicts
3. **Install speed:** Quick `pip install`
4. **Maintainability:** Fewer things to update

### Dependencies Chosen
- `pyyaml` (7.1K ⭐) - YAML parsing, industry standard
- `watchdog` (6.8K ⭐) - File system monitoring, well-maintained
- `python-json-logger` (1.3K ⭐) - JSON logging, lightweight

### Not Included
- ❌ No web framework (HTTP is v0.5+ feature)
- ❌ No ORM (agents don't need databases)
- ❌ No validators (lightweight schema checking built-in)

---

## Choice 10: Single Agent Class (Universal Template)

### Decision
One `Agent` class that supports all agent types (selected via config).

### Reasoning
1. **DRY:** Don't repeat event loop, logging, trigger code
2. **Consistency:** Same runtime for all agent types
3. **Maintainability:** Bug fixes apply everywhere
4. **Future-proof:** v0.2+ just adds execution modes, not new classes

### Implementation
- `Agent` class orchestrates subsystems
- `agent_type` in config selects which executor runs
- v0.1: `task_executor` mode
- v0.2+: Add `llm_inference`, `hybrid` modes without changing core

---

## Choice 11: Configuration Schema Validation at Load Time

### Decision
Validate config.yaml structure before agent starts.

### Reasoning
1. **Fast failure:** Errors caught before runtime
2. **Helpful messages:** Users see exactly what's wrong
3. **Safety:** Can't accidentally misconfigure agent
4. **Consistency:** Schema documents expected structure

### Implementation
- `Config` class validates on load
- Checks required fields (agent_id, agent_type)
- Validates agent_type is known value
- Recursively validates environment variable references

---

## Choice 12: Example Agent > Echo Agent

### Decision
First example is File Validator (realistic workflow) not Echo Agent (trivial).

### Reasoning
1. **Relevance:** File validation is actual use case
2. **Learning:** Users see real workflow with branching
3. **Testing:** Easy to test (drop files, see results)
4. **Reference:** Good template for own agents

### Trade-offs
- ❌ Slightly more complex
- ✅ More educational
- ✅ More immediately useful

---

## Summary: Philosophy

This architecture embodies:

1. **Abstraction over Implementation** - Config-driven, not code-driven
2. **Clarity over Cleverness** - Explicit workflows, readable YAML
3. **Simplicity over Completeness** - v0.1 does one thing well
4. **Future-Ready over Over-Engineering** - Async, schemas, extensibility built in
5. **Non-Coder Focus** - Every decision considers: "Would a non-programmer understand?"

---

## Future Evolution (Informed by v0.1)

Based on this v0.1 foundation:

- **v0.2:** Add LLM Inference mode (same config structure)
- **v0.3:** Add Hybrid mode (workflows + LLM escalation)
- **v0.4:** Add MCP Tool Server mode (agents as services)
- **v0.5:** Add Hub integration (multi-agent communication)

Each version extends the architecture without breaking existing agents.

---

*This document explains the reasoning, not just the implementation. Questions? See `ARCHITECTURE.md` for system design.*
