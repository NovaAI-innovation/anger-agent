# Document Categorizer Agent

## Purpose

The Document Categorizer Agent demonstrates a **configuration-driven agent** that combines:
- **Deterministic operations** (file I/O, JSON handling)
- **Variable LLM inference** (mock categorization in v0.1, real LLM in v0.2+)

This agent processes text documents, analyzes their content using an LLM, and routes them to different output folders based on the assigned category.

## Use Case

**Scenario**: You have a folder of incoming documents that need to be automatically triaged and organized.

- `inbox/` - Raw documents arrive
- Agent reads each document
- Mock LLM analyzes content and assigns category (error, success, warning, info)
- Document is moved to appropriate folder with metadata:
  - `errors/` - Problem reports, failures
  - `processed/` - Successful/completed items
  - `review/` - Warnings, info, unknown categories

## How It Works

### Configuration-Driven Behavior

No Python code changes needed. Behavior is entirely defined by:

**config.yaml**:
- Trigger: watches `$INBOX_PATH` for `*.txt` files
- Workflow: 7-step pipeline with nested conditional routing
- Tools: file.read, llm.analyze, json.stringify, file.move, log
- Logging: debug level with full step tracking

### Workflow Steps

1. **read_document** (deterministic)
   - Reads raw document content from file
   - Input: `${trigger.file_path}`
   - Output: `document_text`

2. **analyze_content** (variable - LLM inference)
   - Passes document text to LLM
   - Provider: "mock" (returns deterministic responses based on keywords)
   - Output: `analysis_result` with:
     - `category` (error, success, warning, info, unknown)
     - `tags` (list of extracted topics)
     - `confidence` (0.0-1.0 score)
     - `summary` (brief description)
     - `analysis` (detailed metrics)

3. **create_metadata** (deterministic)
   - Packages analysis result as JSON metadata
   - Combines filename, timestamp, category, tags, analysis
   - Output: `metadata_json` (stringified)

4. **route_by_category** (deterministic conditional)
   - First decision: Is category == "error"?
   - If true -> route to errors folder
   - If false -> check next condition

5. **check_success** (nested deterministic conditional)
   - Is category == "success"?
   - If true -> route to processed folder
   - If false -> route to review folder

6-7. **Routing Actions** (deterministic)
   - Write metadata JSON to `.meta.json` file
   - Move original document to destination folder
   - Log result with appropriate level

## Variable vs Deterministic Behavior

### Deterministic Operations
```yaml
# File I/O - same input always produces same output
- action: "file.read"
  params:
    path: "${trigger.file_path}"

# JSON operations - same input = same output
- action: "json.stringify"
  params:
    data: {...}

# Conditional logic - based on concrete values
- action: "conditional"
  condition: "${analysis_result.category} == error"
```

### Variable Operations (LLM Inference)
```yaml
# LLM analysis - can vary based on content
- action: "llm.analyze"
  params:
    text: "${read_document.document_text}"
    provider: "mock"  # Will switch to "openai" in v0.2
```

The **mock provider** in v0.1 returns **deterministic results** based on keyword matching, making tests repeatable.

## Mock LLM Behavior

The mock provider implements keyword-based categorization:

| Keywords | Category | Confidence |
|----------|----------|-----------|
| error, failed, problem, issue, bug | error | 0.95 |
| success, completed, done, finished, working | success | 0.92 |
| warning, caution, attention, careful | warning | 0.88 |
| info, information, note, notice | info | 0.85 |
| (none match) | unknown | 0.50 |

Tags are added based on:
- Text > 100 chars -> `detailed`
- Contains user/account/profile words -> `user-related`
- Contains system/server/network words -> `system-related`
- Contains security/auth/permission words -> `security-related`

## Configuration

### Environment Variables
```bash
export INBOX_PATH="/path/to/inbox"          # Where documents arrive
export ERRORS_PATH="/path/to/errors"        # Route for error category
export PROCESSED_PATH="/path/to/processed"  # Route for success category
export REVIEW_PATH="/path/to/review"        # Route for other categories
```

### Quick Test
```bash
cd agents/examples/document_categorizer
python run.py
```

## Upgrade Path

### v0.2 - Real OpenAI Integration (IMPLEMENTED)

Phase 2 is complete! The framework now supports real OpenAI API calls with the same configuration-driven approach.

**Setup:**
```bash
pip install openai>=1.0.0
export OPENAI_API_KEY="sk-..."
```

**Configuration Changes:**
```yaml
- action: "llm.analyze"
  params:
    text: "${read_document.document_text}"
    prompt: "Your custom prompt here..."
    provider: "openai"           # <- Changed from "mock"
    model: "gpt-3.5-turbo"       # <- New (or "gpt-4")
    api_key: "${OPENAI_API_KEY}" # <- New (from environment)
```

**Key Features:**
- **Structured Output**: Prompts are designed to return JSON with category, tags, confidence
- **Error Handling**: Graceful handling of API errors, rate limits, connection issues
- **Response Parsing**: Handles JSON in markdown code blocks or raw format
- **Validation**: Normalizes responses (fixes invalid categories, clamps confidence scores)
- **Same Interface**: Returns same structure as mock provider for full compatibility

**Using the OpenAI Config:**
```bash
# Use the provided openai config instead of default mock config
cd agents/examples/document_categorizer
OPENAI_API_KEY="sk-..." INBOX_PATH="/tmp/inbox" python -c "
from runtime.agent import Agent
agent = Agent(config_path='config.openai.yaml')
agent.run_sync()
"
```

**Testing without API:**
All tests use mock OpenAI client, so you can verify the integration without API costs:
```bash
pytest tests/test_document_categorizer.py::TestLLMTool::test_openai_llm_analyze_success -v
pytest tests/test_document_categorizer.py -k openai -v
```

### v0.3 - Provider Abstraction (FUTURE)
```yaml
- action: "llm.analyze"
  params:
    text: "${read_document.document_text}"
    provider: "${LLM_PROVIDER}"  # From env or config
    model: "${LLM_MODEL}"        # From env or config
    api_key: "${LLM_API_KEY}"    # From env
```

Switch between Claude, OpenAI, local models by changing environment variables only.

## Why This Design Matters

1. **Configuration Over Code**
   - Non-technical users can modify routing logic
   - Change category thresholds, add routes, adjust prompts - no deployment needed

2. **Deterministic Testing**
   - Mock provider ensures reproducible results
   - Test routing logic before integrating real LLM API

3. **Gradual Integration**
   - Start with mock for proof-of-concept
   - Swap to OpenAI for production
   - Later add Claude or other providers
   - Each upgrade is a config change, not code refactor

4. **Single Responsibility**
   - Agent does one thing: categorize and route documents
   - All complexity lives in the workflow config
   - Tool implementations stay simple and composable

## Testing the Agent

### Test Files (Mock Scenarios)
Create test documents in `INBOX_PATH`:

**error_log.txt** (triggers error category)
```
System error occurred: Database connection failed
Problem: Connection timeout after 30 seconds
```

**success_report.txt** (triggers success category)
```
Task completed successfully.
All validations passed.
```

**warning_notice.txt** (triggers warning category)
```
Please use caution with the following approach.
Attention needed for edge cases.
```

### Expected Output
```
inbox/
  (empty after processing)
errors/
  error_log.txt
  error_log.txt.meta.json
processed/
  success_report.txt
  success_report.txt.meta.json
review/
  warning_notice.txt
  warning_notice.txt.meta.json
```

### Metadata Example
```json
{
  "filename": "error_log.txt",
  "timestamp": "2026-01-15T10:50:29Z",
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

## Architecture Decisions

### Why Mock Provider First?
- No API costs during development
- Instant deterministic responses
- Easy to test routing logic
- Clear upgrade path to real LLM

### Why Nested Conditionals?
- Demonstrates framework's conditional branching
- Shows how to handle multiple categories
- Routes can be extended without changing workflow logic

### Why Metadata Alongside Documents?
- JSON metadata validates against schema
- Enables downstream systems to process results
- Future: send metadata to other agents/APIs

## Limitations (By Design)

- **Mock LLM is keyword-based**: Not true AI inference
  - Real OpenAI integration in v0.2
  - Demonstrates the upgrade path

- **Single document per trigger**: File watcher processes files sequentially
  - Shows framework behavior clearly
  - v0.5: May add batch processing

- **No memory**: Agent doesn't remember previous documents
  - Stateless by design (framework principle)
  - External storage (logs, metadata files) is the memory

## Next Steps

1. **Run the mock version**: Verify routing logic works
2. **Write test documents**: See categorization in action
3. **Inspect metadata**: Validate schema and output structure
4. **Plan OpenAI integration**: Design v0.2 configuration changes
5. **Extend categories**: Add domain-specific routing rules (YAML-only)
