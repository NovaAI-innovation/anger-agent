# LLM Provider Guide

## Overview

The framework supports a **provider-agnostic LLM abstraction** that allows you to switch between different language models through configuration alone—no code changes required.

**Supported Providers (Phase 3 - IMPLEMENTED)**:
- **mock**: Keyword-based mock (deterministic, no API needed)
- **openai**: OpenAI GPT models (gpt-4, gpt-3.5-turbo)
- **claude**: Anthropic Claude models (claude-3-opus, claude-3-sonnet, claude-3-haiku)

## Architecture

### Provider Interface

All providers implement the same interface:

```python
class LLMProvider:
    def analyze(self, text: str, prompt: str, params: Dict) -> Dict:
        """Returns: {category, tags, confidence, summary, analysis}"""
```

This means:
- **Same input format** across all providers
- **Same output structure** for full compatibility
- **Same error handling** patterns

### Provider Factory

```python
from runtime.tools import get_llm_provider

# Get any provider
provider = get_llm_provider("mock")      # Keyword-based mock
provider = get_llm_provider("openai")    # OpenAI API
provider = get_llm_provider("claude")    # Claude API
```

Factory Features:
- Case-insensitive provider names ("MOCK", "mock", "Mock" all work)
- Runtime provider selection
- Clear error messages for missing SDKs

## Mock Provider (v0.1)

**Best For**: Development, testing, proof-of-concept

### Setup
No setup required - built-in, no dependencies.

### Usage
```yaml
- action: "llm.analyze"
  params:
    text: "${document_text}"
    provider: "mock"  # Default
    # Optional: custom prompt
    prompt: "Categorize this text..."
```

### Behavior
Deterministic categorization based on keywords:

| Keywords | Category | Confidence |
|----------|----------|-----------|
| error, failed, problem, issue, bug | error | 0.95 |
| success, completed, done, finished, working | success | 0.92 |
| warning, caution, attention, careful | warning | 0.88 |
| info, information, note, notice | info | 0.85 |
| (none match) | unknown | 0.50 |

Tags extracted from content:
- Text > 100 chars → `detailed`
- Contains user/account words → `user-related`
- Contains system/server words → `system-related`
- Contains security/auth words → `security-related`

### Example Output
```json
{
  "category": "error",
  "tags": ["system-related", "detailed"],
  "confidence": 0.95,
  "summary": "Text classified as error",
  "analysis": {
    "word_count": 15,
    "character_count": 87,
    "provider": "mock",
    "model": "mock-v1"
  }
}
```

## OpenAI Provider (v0.2)

**Best For**: Production, high-quality categorization, access to latest models

### Setup
```bash
# Install SDK
pip install openai>=1.0.0

# Set API key
export OPENAI_API_KEY="sk-..."
```

### Usage
```yaml
- action: "llm.analyze"
  params:
    text: "${document_text}"
    provider: "openai"
    model: "gpt-4"  # or "gpt-3.5-turbo"
    api_key: "${OPENAI_API_KEY}"  # From environment
```

### Configuration Options

**Model Selection:**
- `gpt-4`: Best quality, higher cost, slower
- `gpt-3.5-turbo`: Fast, cheaper, good quality (recommended)

**Parameters:**
- `text` (required): Text to analyze
- `prompt` (optional): Custom prompt (default provided)
- `provider` (required): "openai"
- `model` (optional): Model name (default: gpt-3.5-turbo)
- `api_key` (optional): API key (reads from OPENAI_API_KEY if not provided)

### Features
- Structured prompt engineering for consistent JSON
- Handles JSON in markdown code blocks
- Response validation (fixes invalid categories, clamps confidence)
- Graceful error handling:
  - Rate limit errors → helpful retry message
  - Connection errors → clear diagnostics
  - API errors → detailed logging

### Example Configuration
```yaml
# For gpt-4 (high quality)
- action: "llm.analyze"
  params:
    text: "${document_text}"
    provider: "openai"
    model: "gpt-4"

# For gpt-3.5-turbo (fast & cheap)
- action: "llm.analyze"
  params:
    text: "${document_text}"
    provider: "openai"
    model: "gpt-3.5-turbo"
```

### Pricing
- gpt-4: ~$0.03-0.06 per 1K tokens
- gpt-3.5-turbo: ~$0.0005-0.0015 per 1K tokens

## Claude Provider (v0.3)

**Best For**: High-quality analysis, complex reasoning, strong safety defaults

### Setup
```bash
# Install SDK
pip install anthropic>=0.15.0

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Usage
```yaml
- action: "llm.analyze"
  params:
    text: "${document_text}"
    provider: "claude"
    model: "claude-3-sonnet-20240229"  # or other Claude models
    api_key: "${ANTHROPIC_API_KEY}"  # From environment
```

### Configuration Options

**Model Selection:**
- `claude-3-opus-20240229`: Most capable, slower, higher cost
- `claude-3-sonnet-20240229`: Best balance (recommended)
- `claude-3-haiku-20240307`: Fastest, cheapest

**Parameters:**
- Same as OpenAI (text, prompt, provider, model, api_key)

### Features
- Structured prompt engineering
- JSON extraction from markdown responses
- Response validation and normalization
- Error handling for API errors and authentication

### Example Configuration
```yaml
# For best balance (recommended)
- action: "llm.analyze"
  params:
    text: "${document_text}"
    provider: "claude"
    model: "claude-3-sonnet-20240229"

# For maximum capability
- action: "llm.analyze"
  params:
    text: "${document_text}"
    provider: "claude"
    model: "claude-3-opus-20240229"
```

### Pricing
- claude-3-opus: ~$0.015-0.075 per 1K tokens
- claude-3-sonnet: ~$0.003-0.015 per 1K tokens
- claude-3-haiku: ~$0.00025-0.00125 per 1K tokens

## Switching Providers

### One-Line Configuration Change

**Step 1: Update provider parameter**
```yaml
# Change this single line in config.yaml
provider: "mock"      # Current
provider: "openai"    # To use OpenAI
provider: "claude"    # To use Claude
```

**Step 2: Set API key (if needed)**
```bash
export OPENAI_API_KEY="sk-..."      # For OpenAI
export ANTHROPIC_API_KEY="sk-ant-..."  # For Claude
# (No key needed for mock)
```

**Step 3: Install SDK (if needed)**
```bash
pip install openai        # For OpenAI
pip install anthropic     # For Claude
# (No SDK needed for mock)
```

### Real-World Example

Same workflow, three different configurations:

**config.mock.yaml** (testing)
```yaml
- action: "llm.analyze"
  params:
    text: "${document_text}"
    provider: "mock"
```

**config.openai.yaml** (production)
```yaml
- action: "llm.analyze"
  params:
    text: "${document_text}"
    provider: "openai"
    model: "gpt-3.5-turbo"
    api_key: "${OPENAI_API_KEY}"
```

**config.claude.yaml** (production alternative)
```yaml
- action: "llm.analyze"
  params:
    text: "${document_text}"
    provider: "claude"
    model: "claude-3-sonnet-20240229"
    api_key: "${ANTHROPIC_API_KEY}"
```

Run with any configuration—**same workflow, zero code changes**:
```bash
OPENAI_API_KEY="sk-..." python run.py config.openai.yaml
ANTHROPIC_API_KEY="sk-ant-..." python run.py config.claude.yaml
python run.py config.mock.yaml  # No API key needed
```

## Choosing a Provider

### Mock
Use when:
- Developing workflows
- Testing logic (no API dependency)
- Prototyping
- Cost is critical

Avoid when:
- You need accurate categorization
- Workflow depends on nuanced analysis

### OpenAI (GPT)
Use when:
- You want latest models (gpt-4 bleeding edge)
- You're familiar with OpenAI API
- You need competitive pricing
- Text categorization is your primary use case

Model choice:
- **gpt-4**: Complex reasoning, edge cases (cost/latency trade-off)
- **gpt-3.5-turbo**: Fast, cheap, good for categorization ✓ (recommended)

### Claude
Use when:
- You want strong safety & consistency
- You prefer Anthropic's approach
- You do complex multi-step reasoning
- You value transparent pricing

Model choice:
- **claude-3-opus**: Maximum capability
- **claude-3-sonnet**: Best balance ✓ (recommended)
- **claude-3-haiku**: Speed critical

## Response Format (All Providers)

Every provider returns the same structure:

```json
{
  "category": "error|success|warning|info|unknown",
  "tags": ["tag1", "tag2"],
  "confidence": 0.0-1.0,
  "summary": "Human-readable description",
  "analysis": {
    "word_count": 15,
    "character_count": 87,
    "provider": "mock|openai|claude",
    "model": "model-name"
  }
}
```

This consistency means:
- Same downstream workflows
- Easy provider swapping
- Predictable error handling

## Error Handling

### Missing SDK
```
ImportError: OpenAI SDK not installed. Run: pip install openai
ImportError: Anthropic SDK not installed. Run: pip install anthropic
```

### Missing API Key
```
ValueError: OpenAI API key not provided. Set OPENAI_API_KEY environment variable or provide api_key parameter.
ValueError: Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable or provide api_key parameter.
```

### API Errors
```
ValueError: OpenAI API rate limit exceeded. Please retry after a moment.
ValueError: Failed to connect to OpenAI API. Check your internet connection and API key.
ValueError: Claude API error: <details>
```

All errors are caught and re-raised with helpful messages. Workflows use `on_error: "fail"` to handle gracefully.

## Environment Variables

### For OpenAI
```bash
export OPENAI_API_KEY="sk-..."
# Optional: override model
export OPENAI_MODEL="gpt-4"
```

### For Claude
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Optional: override model
export ANTHROPIC_MODEL="claude-3-opus-20240229"
```

### For Mock
No environment variables needed.

## Testing Without APIs

All tests use mocked providers (no real API calls):

```bash
# Mock provider tests (no setup needed)
pytest tests/test_document_categorizer.py::TestLLMTool::test_mock_llm_error_category

# OpenAI tests (mocked client, no API key needed)
pytest tests/test_document_categorizer.py::TestLLMTool::test_openai_llm_analyze_success

# Claude tests (mocked client, no API key needed)
pytest tests/test_document_categorizer.py::TestLLMTool::test_claude_llm_analyze_success

# Provider switching tests (all mocked)
pytest tests/test_document_categorizer.py::TestLLMTool::test_provider_switching

# All tests
pytest tests/ -v
```

## Future Extensions

### v0.4: Local Models
Support for local LLM models (Llama 2, Mistral, etc.) via:
- Ollama
- LM Studio
- HuggingFace

### v0.5: Multi-Model Ensembling
Combine multiple providers for higher confidence:
```yaml
provider: "ensemble"
models:
  - provider: "openai"
    model: "gpt-4"
  - provider: "claude"
    model: "claude-3-sonnet-20240229"
```

### v0.6: Provider Caching
Cache responses to reduce API calls and costs.

## Examples

All document_categorizer configurations:
- `config.yaml`: Mock provider (default)
- `config.openai.yaml`: OpenAI integration
- `config.claude.yaml`: Claude integration

Run any configuration:
```bash
cd agents/examples/document_categorizer
python run.py  # Uses config.yaml (mock)
OPENAI_API_KEY="sk-..." python run.py --config config.openai.yaml
ANTHROPIC_API_KEY="sk-ant-..." python run.py --config config.claude.yaml
```

## Summary

| Feature | Mock | OpenAI | Claude |
|---------|------|--------|--------|
| No setup | ✓ | ✗ | ✗ |
| No API cost | ✓ | ✗ | ✗ |
| Deterministic | ✓ | ✗ | ✗ |
| Smart analysis | ✗ | ✓ | ✓ |
| Fast | ✓ | ~ | ~ |
| Latest models | N/A | ✓ | ✓ |
| Best balance | N/A | ✓ | ✓ |
| Safest | N/A | ~ | ✓ |

**Recommendation for Production**:
- Use **mock** for testing
- Use **openai (gpt-3.5-turbo)** for cost-effective production
- Use **claude (claude-3-sonnet)** for balanced capability & cost
