# Agent Examples

This folder contains fully tested and documented agent examples demonstrating different capabilities of the configuration-driven agent framework.

## Overview

All agents in this directory are **production-ready** with complete test coverage and comprehensive documentation.

## Available Agents

### 1. File Validator Agent

**Purpose**: Validates JSON files against a schema and routes them to appropriate folders

**Location**: `./file_validator/`

**What It Does**:
- Watches a folder for incoming JSON files
- Parses and validates each file against a schema
- Routes valid files to `processed` folder
- Routes invalid files to `errors` folder
- Generates detailed error logs

**Status**: ✅ **Fully Tested** (17 tests)

**Configuration**:
```bash
# Default (mock with environment variables)
cd file_validator
INBOX_PATH="./data/inbox" PROCESSED_PATH="./data/processed" ERRORS_PATH="./data/errors" SCHEMA_PATH="./schema.json" python run.py
```

**Files**:
- `config.yaml` - Configuration with environment variable support
- `schema.json` - Example validation schema (id, name, email required)
- `AGENTS.md` - Complete agent documentation
- `run.py` - Quick start script

**Complexity**: Low (deterministic file I/O only)

---

### 2. Document Categorizer Agent

**Purpose**: Categorizes documents using LLM analysis and routes them based on category

**Location**: `./document_categorizer/`

**What It Does**:
- Watches a folder for text documents
- Uses LLM to analyze and categorize content (error, success, warning, info, unknown)
- Routes documents to category-specific folders
- Generates metadata files with analysis results
- Demonstrates provider abstraction (mock/openai/claude)

**Status**: ✅ **Fully Tested** (32 tests including provider switching)

**Configurations Available**:

#### config.yaml (Mock Provider)
```bash
cd document_categorizer
python run.py
# or explicitly:
INBOX_PATH="./data/inbox" ERRORS_PATH="./data/errors" PROCESSED_PATH="./data/processed" REVIEW_PATH="./data/review" python run.py
```

**Provider**: Mock (deterministic, keyword-based)
**Setup**: None (built-in)
**Cost**: Free
**Best for**: Testing, development, proof-of-concept

#### config.openai.yaml (OpenAI GPT)
```bash
cd document_categorizer
OPENAI_API_KEY="sk-..." INBOX_PATH="./data/inbox" ERRORS_PATH="./data/errors" PROCESSED_PATH="./data/processed" REVIEW_PATH="./data/review" python -c "
from runtime.agent import Agent
agent = Agent(config_path='config.openai.yaml')
agent.run_sync()
"
```

**Provider**: OpenAI (gpt-3.5-turbo by default)
**Setup**: `pip install openai>=1.0.0` + API key
**Cost**: ~$0.0005-0.0015 per 1K tokens
**Best for**: Production, cost-effective, latest models

#### config.claude.yaml (Claude)
```bash
cd document_categorizer
ANTHROPIC_API_KEY="sk-ant-..." INBOX_PATH="./data/inbox" ERRORS_PATH="./data/errors" PROCESSED_PATH="./data/processed" REVIEW_PATH="./data/review" python -c "
from runtime.agent import Agent
agent = Agent(config_path='config.claude.yaml')
agent.run_sync()
"
```

**Provider**: Claude (claude-3-sonnet by default)
**Setup**: `pip install anthropic>=0.15.0` + API key
**Cost**: ~$0.003-0.015 per 1K tokens
**Best for**: Production, higher quality analysis, balanced cost

**Files**:
- `config.yaml` - Mock provider (default, testing)
- `config.openai.yaml` - OpenAI GPT integration
- `config.claude.yaml` - Claude integration
- `schema.json` - Metadata validation schema
- `AGENTS.md` - Complete documentation with provider details
- `run.py` - Quick start script

**Complexity**: Medium (demonstrates LLM provider abstraction)

---

## Quick Start by Use Case

### I want to test agents without API costs
```bash
# File Validator (deterministic)
cd file_validator
python run.py

# Document Categorizer (mock LLM)
cd document_categorizer
python run.py
```

### I want to use OpenAI GPT
```bash
cd document_categorizer
OPENAI_API_KEY="sk-..." python -c "from runtime.agent import Agent; Agent(config_path='config.openai.yaml').run_sync()"
```

### I want to use Claude
```bash
cd document_categorizer
ANTHROPIC_API_KEY="sk-ant-..." python -c "from runtime.agent import Agent; Agent(config_path='config.claude.yaml').run_sync()"
```

### I want to understand the framework
```bash
# Read the agent documentation
cat file_validator/AGENTS.md
cat document_categorizer/AGENTS.md

# Read the provider guide
cat ../docs/LLM_PROVIDERS.md
```

---

## Agent Comparison

| Feature | File Validator | Document Categorizer |
|---------|---|---|
| Purpose | Validate JSON files | Categorize documents |
| Complexity | Low | Medium |
| Tests | 17 ✅ | 32 ✅ |
| Deterministic | Yes | No (uses LLM) |
| Requires API | No | Optional (mock works) |
| Provider Support | N/A | Mock, OpenAI, Claude |
| Config Variants | 1 | 3 (mock, openai, claude) |
| Best For | Proof-of-concept | Production categorization |

---

## Provider Quick Reference

### Setup Requirements

**Mock** (Built-in)
```bash
# No setup needed, works out of the box
python run.py
```

**OpenAI**
```bash
pip install openai>=1.0.0
export OPENAI_API_KEY="sk-..."
# Then use config.openai.yaml
```

**Claude**
```bash
pip install anthropic>=0.15.0
export ANTHROPIC_API_KEY="sk-ant-..."
# Then use config.claude.yaml
```

### Provider Selection Guide

| Provider | Cost | Speed | Quality | Best For |
|----------|------|-------|---------|----------|
| Mock | Free | Instant | Low (keyword-based) | Testing, dev |
| OpenAI | $$ | Fast | High | Production, cost-effective |
| Claude | $$ | Medium | Very High | Production, quality-focused |

---

## Testing All Agents

```bash
# Run all tests
cd ..  # Go to framework root
python -m pytest tests/ -v

# Test specific agent
pytest tests/test_document_categorizer.py -v
pytest tests/test_framework_components.py::TestFileValidatorConfiguration -v

# Test providers (without API calls)
pytest tests/ -k "openai or claude or provider" -v
```

**Current Test Status**: ✅ 61 tests passing

---

## File Structure

```
agents/examples/
├── README.md (this file)
├── file_validator/
│   ├── config.yaml              # Configuration
│   ├── schema.json              # Validation schema
│   ├── AGENTS.md                # Documentation
│   └── run.py                   # Quick start script
└── document_categorizer/
    ├── config.yaml              # Mock provider config
    ├── config.openai.yaml       # OpenAI provider config
    ├── config.claude.yaml       # Claude provider config
    ├── schema.json              # Metadata schema
    ├── AGENTS.md                # Documentation
    └── run.py                   # Quick start script
```

---

## Creating a Test Workflow

### File Validator Example

```bash
# 1. Set up directories
mkdir -p ./data/{inbox,processed,errors}

# 2. Create a test file
echo '{"id": 1, "name": "John", "email": "john@example.com"}' > ./data/inbox/valid.json

# 3. Run agent (set env vars)
cd file_validator
INBOX_PATH="./data/inbox" PROCESSED_PATH="./data/processed" ERRORS_PATH="./data/errors" SCHEMA_PATH="./schema.json" python run.py

# 4. Check output
ls ./data/processed/  # Should contain valid.json and valid.json.meta.json
```

### Document Categorizer Example

```bash
# 1. Set up directories
mkdir -p ./data/{inbox,processed,errors,review}

# 2. Create test documents
echo "System error occurred: Database connection failed" > ./data/inbox/error.txt
echo "Task completed successfully" > ./data/inbox/success.txt
echo "Please use caution with this approach" > ./data/inbox/warning.txt

# 3. Run agent with mock provider
cd document_categorizer
INBOX_PATH="./data/inbox" PROCESSED_PATH="./data/processed" ERRORS_PATH="./data/errors" REVIEW_PATH="./data/review" python run.py

# 4. Check output
ls ./data/errors/      # error.txt
ls ./data/processed/   # success.txt
ls ./data/review/      # warning.txt
```

---

## Next Steps

1. **Try the agents**: Start with mock provider for testing
2. **Read documentation**: Check `AGENTS.md` in each agent folder
3. **Review configuration**: See how workflows are defined in `config.yaml`
4. **Integrate APIs**: Add `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` to use real LLM
5. **Create your own**: Use these as templates for custom agents

---

## Support & Documentation

- **Framework Overview**: See `../README.md`
- **Architecture Details**: See `../docs/ARCHITECTURE.md`
- **Agent Design**: See individual agent `AGENTS.md` files
- **Provider Guide**: See `../docs/LLM_PROVIDERS.md`
- **Tool Reference**: See `../docs/TOOLS.md`
- **Workflow Syntax**: See `../docs/WORKFLOWS.md`

---

## Status Summary

✅ **File Validator**
- Fully tested (17 tests)
- 1 configuration variant
- Deterministic (no external dependencies)

✅ **Document Categorizer**
- Fully tested (32 tests including provider switching)
- 3 configuration variants (mock, openai, claude)
- Demonstrates provider abstraction

✅ **Total Test Coverage**: 61 passing tests
