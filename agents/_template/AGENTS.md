# Agent: [Your Agent Name]

## Purpose
[One sentence: What does this agent do?]

## What This Agent Does

[Describe the agent's behavior in plain English]

### Example Flow

[Walk through a concrete example of what the agent does]

## Configuration

See `config.yaml` for settings and behavior definition.

Key configuration:
- **Trigger**: What event causes workflows to run?
- **Workflows**: What steps should execute?
- **Tools**: What capabilities are available?

## Tools Used

[List the tools this agent uses]

See `docs/TOOLS.md` for full tool documentation.

## How to Test

### 1. Start the Agent
```bash
cd agents/[your_agent_name]
python run.py
```

### 2. Trigger an Event
[Describe how to trigger your agent]

### 3. Check Results
[Describe how to verify it worked]

## Customization

You can customize this agent by editing `config.yaml`:

- **Change triggers:** Modify the `triggers` section
- **Add workflow steps:** Add to `workflows`
- **Enable/disable tools:** Change the `tools` section

No Python code changes needed!

## Troubleshooting

[Add troubleshooting tips specific to your agent]

## Next Steps

- Explore: [What should users try?]
- Extend: [How could they extend this?]
- Create: [How do they create similar agents?]

---

See `README.md` for more information.
