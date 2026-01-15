# Document Categorizer Agent

## What It Does

Automatically categorizes text documents based on content and moves them to appropriate folders.

**Input**: Text files in a watched folder
**Output**: Documents moved to category folders + metadata JSON files

**Categories**: error, success, warning, info, unknown

## Quick Start

```bash
# Create test folders
mkdir -p /tmp/doc_test/{inbox,processed,errors,review}

# Create a test file
echo "System error occurred" > /tmp/doc_test/inbox/test.txt

# Run agent
cd agents/examples/document_categorizer
INBOX_PATH="/tmp/doc_test/inbox" \
PROCESSED_PATH="/tmp/doc_test/processed" \
ERRORS_PATH="/tmp/doc_test/errors" \
REVIEW_PATH="/tmp/doc_test/review" \
python run.py

# Check result
ls /tmp/doc_test/errors/  # test.txt should be here
```

## Configuration

### Three Provider Options

**Default (Mock) - config.yaml**
```bash
python run.py
# Uses keyword-based mock (free, instant)
```

**OpenAI - config.openai.yaml**
```bash
OPENAI_API_KEY="sk-..." python -c "from runtime.agent import Agent; Agent(config_path='config.openai.yaml').run_sync()"
# Uses GPT-3.5-turbo (fast, $)
```

**Claude - config.claude.yaml**
```bash
ANTHROPIC_API_KEY="sk-ant-..." python -c "from runtime.agent import Agent; Agent(config_path='config.claude.yaml').run_sync()"
# Uses Claude 3 Sonnet (quality, $$)
```

## How It Works

1. Watches `INBOX_PATH` for new `.txt` files
2. Reads file content
3. Sends to LLM for categorization
4. Routes based on category:
   - **error** → ERRORS_PATH
   - **success** → PROCESSED_PATH
   - **warning, info, unknown** → REVIEW_PATH
5. Creates `.meta.json` file with analysis

## Workflow Steps

```yaml
read_file → analyze_content → create_metadata → route_by_category → move_file
```

### Conditional Routing

```
Is category == "error"?
  ├─ YES → move to errors/
  └─ NO  → Is category == "success"?
           ├─ YES → move to processed/
           └─ NO  → move to review/
```

## Environment Variables

```bash
INBOX_PATH        # Folder to watch for new files (required)
PROCESSED_PATH    # Folder for success files (required)
ERRORS_PATH       # Folder for error files (required)
REVIEW_PATH       # Folder for other files (required)
OPENAI_API_KEY    # Only needed for OpenAI provider
ANTHROPIC_API_KEY # Only needed for Claude provider
```

## Test

```bash
# Run tests
pytest ../../tests/test_document_categorizer.py -v

# Test specific provider
pytest ../../tests/test_document_categorizer.py -k "mock" -v      # Mock tests
pytest ../../tests/test_document_categorizer.py -k "openai" -v    # OpenAI tests
pytest ../../tests/test_document_categorizer.py -k "claude" -v    # Claude tests
pytest ../../tests/test_document_categorizer.py -k "switching" -v # Provider switching
```

## Output

Each categorized file gets a metadata JSON:

```json
{
  "filename": "error.txt",
  "category": "error",
  "tags": ["system-related"],
  "confidence": 0.95,
  "summary": "Text classified as error",
  "analysis": {
    "word_count": 10,
    "provider": "mock",
    "model": "mock-v1"
  }
}
```

## Troubleshooting

**Files not moving?**
- Check `INBOX_PATH` exists and is readable
- Check other path variables are set
- Check agent log file (e.g., `document_categorizer.log`)

**API key error?**
- Verify `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set
- Check key format is correct

**Wrong categorization?**
- Mock provider uses keyword matching (not AI)
- Use OpenAI or Claude for better accuracy

## Files in This Folder

- `config.yaml` - Mock provider configuration
- `config.openai.yaml` - OpenAI provider configuration
- `config.claude.yaml` - Claude provider configuration
- `schema.json` - Metadata validation schema
- `run.py` - Quick start script
- `AGENTS.md` - This file

## Next

See root `USER_GUIDE.md` for detailed setup and testing instructions.
