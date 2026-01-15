# Contributing to Agent Framework

Thank you for your interest in contributing! This guide explains how to set up a development environment and contribute to the Agent Framework.

---

## Developer Setup

### 1. Clone the Repository

```bash
git clone https://github.com/anthropics/agent-framework.git
cd agent-framework
```

### 2. Create a Python Virtual Environment (Recommended)

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .  # Install package in development mode
```

### 4. Run Setup

**Windows:**
```cmd
scripts\setup.bat
```

**Linux / macOS:**
```bash
./scripts/setup.sh
```

### 5. Verify Installation

```bash
# Test runtime
python3 -c "from runtime import Agent; print('✓ Runtime loaded')"

# Run tests
python -m pytest tests/ -v
```

---

## Project Structure

```
agent-framework/
├── runtime/                    # Core runtime components
│   ├── agent.py               # Main agent class
│   ├── config.py              # Configuration loader
│   ├── triggers.py            # Trigger implementations
│   ├── workflows.py           # Workflow executor
│   ├── tools.py               # Tool registry
│   ├── hub.py                 # Hub connector (stub)
│   ├── logger.py              # Logging
│   └── __init__.py
│
├── agents/                     # Agent definitions
│   ├── _template/             # Template for new agents
│   │   ├── config.yaml
│   │   ├── AGENTS.md
│   │   ├── setup.sh
│   │   └── setup.bat
│   │
│   └── examples/              # Example agents
│       ├── file_validator/    # File validation example
│       └── document_categorizer/  # LLM categorization example
│
├── scripts/                    # Helper scripts
│   ├── setup.sh / setup.bat    # Project setup
│   ├── run.sh / run.bat        # Run agents
│   └── new_agent.sh / new_agent.bat  # Generate agents
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md
│   ├── DESIGN_REASONING.md
│   ├── WORKFLOWS.md
│   ├── TOOLS.md
│   ├── SETUP_WINDOWS.md
│   ├── SETUP_LINUX.md
│   ├── PATH_REFERENCE.md
│   ├── AGENT_SETUP.md
│   └── LLM_PROVIDERS.md
│
├── tests/                      # Test suite
│   ├── test_config.py
│   ├── test_framework_components.py
│   ├── test_document_categorizer.py
│   └── test_file_validator_agent.py
│
├── QUICKSTART.md              # 5-minute quickstart
├── README.md                  # Project overview
├── requirements.txt           # Python dependencies
└── .env.example               # Environment template
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow the style guidelines below.

### 3. Test Your Changes

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_config.py -v

# Run with coverage
python -m pytest tests/ --cov=runtime --cov-report=html
```

### 4. Commit Changes

```bash
git add .
git commit -m "descriptive commit message"
```

**Commit Message Format:**
- Start with a verb: `Add`, `Fix`, `Update`, `Refactor`, `Remove`
- Be specific about what changed
- Reference issues: `Closes #123`

Examples:
```
Add Windows batch script setup support
Fix environment variable expansion in config loader
Update documentation for cross-platform paths
Refactor workflow execution engine for clarity
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub with:
- Clear description of changes
- Reference to any related issues
- Testing notes

---

## Code Style Guidelines

### Python

- **Format**: Follow PEP 8
- **Tools**: We use `black` for formatting (optional but recommended)
  ```bash
  black runtime/
  ```
- **Linting**: Use `flake8` to check for issues
  ```bash
  flake8 runtime/
  ```

### YAML (Configs)

- Use 2-space indentation
- Quote strings containing special characters
- Comment complex configurations
- Example:
  ```yaml
  environment:
    INBOX_PATH: "${AGENT_INBOX_PATH:./data/inbox}"

  workflows:
    my_workflow:
      steps:
        - id: "step1"
          action: "tool_name"
  ```

### Shell Scripts

- Use `set -e` for error handling
- Add comments for clarity
- Test on both bash and sh
- Use `#!/bin/bash` for bash-specific features

### Documentation

- Use clear, simple language
- Include examples
- Link to related docs
- Platform-specific instructions use tabs (Windows/Linux/macOS)

---

## Testing

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test
python -m pytest tests/test_config.py::TestConfigLoading -v

# With coverage report
python -m pytest tests/ --cov=runtime --cov-report=html
```

### Writing Tests

Create test files in `tests/` directory:

```python
# tests/test_my_feature.py
import pytest
from runtime import Agent

def test_my_feature():
    """Test description"""
    # Arrange
    config = {"agent_id": "test"}

    # Act
    agent = Agent(config)
    result = agent.some_method()

    # Assert
    assert result == expected_value
```

### Test Coverage Goals

- Aim for 80%+ coverage
- Test happy paths and error cases
- Test Windows and Linux paths separately

---

## Documentation Standards

### Markdown Files

- Clear headings hierarchy (# → ##)
- Code examples with syntax highlighting
- Platform-specific sections with tabs:
  ```markdown
  ==="Windows"
      ```cmd
      command
      ```

  === "Linux/macOS"
      ```bash
      command
      ```
  ```

### In-Code Documentation

- Docstrings for all public functions/classes
- Type hints where possible
- Comments for complex logic

Example:
```python
def execute_workflow(workflow_id: str, context: dict) -> dict:
    """Execute a workflow by ID.

    Args:
        workflow_id: ID of the workflow to execute
        context: Variable context for interpolation

    Returns:
        Workflow execution result

    Raises:
        WorkflowNotFoundError: If workflow doesn't exist
    """
    pass
```

---

## Common Tasks

### Adding a New Tool

1. **Implement the tool** in `runtime/tools.py`:
   ```python
   def my_new_tool(param1: str, param2: int) -> dict:
       """Description of what the tool does"""
       return {"result": "value"}
   ```

2. **Register in tool registry** in `runtime/tools.py`

3. **Add tests** in `tests/`

4. **Document** in `docs/TOOLS.md`

### Creating a New Example Agent

1. **Use the template**:
   ```bash
   ./scripts/new_agent.sh my_example_agent
   cd agents/my_example_agent
   ```

2. **Configure the agent**:
   - Edit `config.yaml` with triggers and workflows
   - Edit `AGENTS.md` with documentation
   - Create `.env` from `.env.example`

3. **Add tests** in `tests/test_my_example_agent.py`

4. **Document** in `agents/examples/README.md`

### Updating Documentation

1. Choose the right file:
   - `QUICKSTART.md` - 5-minute intro
   - `docs/ARCHITECTURE.md` - System design
   - `docs/WORKFLOWS.md` - Workflow syntax
   - `docs/AGENT_SETUP.md` - Configuration guide
   - `docs/SETUP_WINDOWS.md` - Windows-specific
   - `docs/SETUP_LINUX.md` - Linux-specific

2. Make changes with clear examples

3. Test rendering (if using markdown tabs)

4. Get review from maintainers

---

## Release Process

1. **Update version** in appropriate files
2. **Update CHANGELOG** with new features
3. **Create release branch**: `release/v0.2.0`
4. **Merge to main** and tag: `v0.2.0`
5. **Push tags**: `git push --tags`

---

## Reporting Issues

### Bug Report Template

```markdown
**Description**
[Clear description of the bug]

**Steps to Reproduce**
1. [First step]
2. [Second step]
3. [etc.]

**Expected Behavior**
[What should happen]

**Actual Behavior**
[What actually happens]

**Environment**
- OS: [Windows 10 / Ubuntu 20.04 / macOS 12]
- Python: [python --version output]
- Branch: [feature branch name]

**Logs**
[Error messages, stack trace, etc.]
```

### Feature Request Template

```markdown
**Description**
[Clear description of desired feature]

**Use Case**
[Why this feature is needed]

**Proposed Solution**
[How it might be implemented]

**Alternatives Considered**
[Other approaches that were considered]
```

---

## Getting Help

- **Slack**: [Project workspace]
- **Discussions**: GitHub Discussions tab
- **Issues**: Open an issue with bug/feature label

---

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Accept criticism gracefully
- Focus on ideas, not individuals

---

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md
- Release notes
- GitHub contributors page

Thank you for contributing to Agent Framework! 🎉
