# User Guide - Document Categorizer Agent

## What This Agent Does

Reads text files, uses an AI model to categorize them (error, success, warning, info), and automatically moves them to the right folder.

## Setup (5 minutes)

### Option 1: No API (Testing)
```bash
pip install -r requirements.txt
# Done. Uses built-in mock categorizer.
```

### Option 2: With OpenAI (Production)
```bash
pip install -r requirements.txt openai>=1.0.0
export OPENAI_API_KEY="sk-your-key-here"
```

### Option 3: With Claude (Production)
```bash
pip install -r requirements.txt anthropic>=0.15.0
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

## How to Run

### Step 1: Create test folders
```bash
mkdir -p /tmp/doc_test/{inbox,processed,errors,review}
```

### Step 2: Create test documents
```bash
echo "System error: Database connection failed" > /tmp/doc_test/inbox/error.txt
echo "Task completed successfully" > /tmp/doc_test/inbox/success.txt
echo "Use caution with this approach" > /tmp/doc_test/inbox/warning.txt
```

### Step 3: Run the agent (choose one)

**Option A: Built-in mock (no API)**
```bash
cd agents/examples/document_categorizer
INBOX_PATH="/tmp/doc_test/inbox" \
PROCESSED_PATH="/tmp/doc_test/processed" \
ERRORS_PATH="/tmp/doc_test/errors" \
REVIEW_PATH="/tmp/doc_test/review" \
python run.py
```

**Option B: OpenAI**
```bash
cd agents/examples/document_categorizer
OPENAI_API_KEY="sk-..." \
INBOX_PATH="/tmp/doc_test/inbox" \
PROCESSED_PATH="/tmp/doc_test/processed" \
ERRORS_PATH="/tmp/doc_test/errors" \
REVIEW_PATH="/tmp/doc_test/review" \
python -c "from runtime.agent import Agent; Agent(config_path='config.openai.yaml').run_sync()"
```

**Option C: Claude**
```bash
cd agents/examples/document_categorizer
ANTHROPIC_API_KEY="sk-ant-..." \
INBOX_PATH="/tmp/doc_test/inbox" \
PROCESSED_PATH="/tmp/doc_test/processed" \
ERRORS_PATH="/tmp/doc_test/errors" \
REVIEW_PATH="/tmp/doc_test/review" \
python -c "from runtime.agent import Agent; Agent(config_path='config.claude.yaml').run_sync()"
```

### Step 4: Check results
```bash
ls /tmp/doc_test/errors/          # error.txt should be here
ls /tmp/doc_test/processed/       # success.txt should be here
ls /tmp/doc_test/review/          # warning.txt should be here
```

Each folder will also contain `.meta.json` files with detailed analysis.

## Run Tests

```bash
cd /path/to/agent-framework
python -m pytest tests/ -v
```

Expected: 61 tests passing

## Troubleshooting

### "Module not found: runtime"
Make sure you're running from the framework root directory.

### "API key not found"
```bash
# Check if variable is set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Set it
export OPENAI_API_KEY="sk-..."
```

### "Folder not found"
Create the folders first:
```bash
mkdir -p /tmp/doc_test/{inbox,processed,errors,review}
```

## How Categorization Works

### Mock (Built-in)
Looks for keywords:
- "error", "failed", "problem" → **error**
- "success", "completed", "done" → **success**
- "warning", "caution", "attention" → **warning**
- "info", "information", "note" → **info**
- (no match) → **unknown**

### OpenAI
Sends text to GPT-3.5-turbo (or gpt-4) and asks it to categorize.

### Claude
Sends text to Claude and asks it to categorize.

## Configuration Files

Each agent can use different configurations:

**document_categorizer/config.yaml** (Mock - free, instant)
```yaml
provider: "mock"
```

**document_categorizer/config.openai.yaml** (OpenAI - fast, cheap)
```yaml
provider: "openai"
model: "gpt-3.5-turbo"
```

**document_categorizer/config.claude.yaml** (Claude - high quality)
```yaml
provider: "claude"
model: "claude-3-sonnet-20240229"
```

Change which config to use by changing the `-config_path` parameter.

## Performance

- **Mock**: Instant (< 1ms)
- **OpenAI**: ~200-500ms per document
- **Claude**: ~300-800ms per document

## Cost Estimates

Analyzing 1,000 documents:

- **Mock**: Free
- **OpenAI**: ~$0.50-1.50
- **Claude**: ~$0.50-2.00

## File Structure

```
inbox/              ← Put text files here
  error.txt
  success.txt
  warning.txt

errors/             ← Agent puts error files here
  error.txt
  error.txt.meta.json

processed/          ← Agent puts success files here
  success.txt
  success.txt.meta.json

review/             ← Agent puts other files here
  warning.txt
  warning.txt.meta.json
```

## Metadata Format

Each file gets a `.meta.json` file with analysis:

```json
{
  "filename": "error.txt",
  "category": "error",
  "tags": ["system-related"],
  "confidence": 0.95,
  "summary": "Text classified as error",
  "analysis": {
    "word_count": 12,
    "character_count": 65,
    "provider": "mock",
    "model": "mock-v1"
  }
}
```

## What's Next?

1. Run the basic test above
2. Try switching providers (mock → openai → claude)
3. Check the metadata files to understand categorization
4. Modify the config to use different models/settings

## Still Have Questions?

- Read `agents/examples/document_categorizer/AGENTS.md` for agent details
- Read `docs/LLM_PROVIDERS.md` for provider comparison
- Check `tests/test_document_categorizer.py` to see usage examples
