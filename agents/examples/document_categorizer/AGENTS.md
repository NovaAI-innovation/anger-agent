# Document Categorizer Agent

## What It Does

Automatically categorizes text documents based on content and moves them to appropriate folders.

**Input**: Text files in a watched folder
**Output**: Documents moved to category folders + metadata JSON files

**Categories**: error, success, warning, info, unknown

## Quick Start

```bash
# Setup (creates data directories and .env)
cd agents/examples/document_categorizer
./setup.sh              # or setup.bat on Windows

# Create a test file
echo "System error occurred" > ./data/inbox/test.txt

# Run agent (uses env vars from .env)
python run.py

# Check result
ls ./data/errors/  # test.txt should be here
```

## Configuration

### LLM Provider Selection

Configure which LLM provider to use via the `LLM_PROVIDER` environment variable in your `.env` file.

**Setup**:
```bash
# Copy template
cp .env.example .env

# Edit .env and set provider
LLM_PROVIDER=mock      # or: openai, claude
```

### Provider Options

#### 1. Mock Provider (Default)
- **Cost**: Free
- **Speed**: Instant (<1ms)
- **Quality**: Keyword-based (good for testing)
- **Setup**: No API key needed

```bash
# Run with mock (default)
./setup.sh              # Creates .env with mock provider
python run.py
```

#### 2. OpenAI Provider
- **Cost**: ~$0.50-1.50 per 1,000 documents
- **Speed**: 200-500ms per document
- **Quality**: High (GPT-3.5-turbo)
- **Setup**: Requires OPENAI_API_KEY

```bash
# Setup
./setup.sh
# Edit .env:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-...

python run.py
```

#### 3. Claude Provider
- **Cost**: ~$0.50-2.00 per 1,000 documents
- **Speed**: 300-800ms per document
- **Quality**: Very High (Claude)
- **Setup**: Requires ANTHROPIC_API_KEY

```bash
# Setup
./setup.sh
# Edit .env:
# LLM_PROVIDER=claude
# ANTHROPIC_API_KEY=sk-ant-...

python run.py
```

---

**Note**: The config.yaml file works with all providers. Provider selection is managed entirely through environment variables in .env - see docs/LLM_PROVIDERS.md for details.

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

- `config.yaml` - Agent behavior and workflow definition
- `schema.json` - Metadata validation schema
- `.env.example` - Configuration template (copy to `.env` and customize)
- `setup.sh` / `setup.bat` - Setup script (creates directories and .env)
- `run.py` - Agent entry point
- `AGENTS.md` - This file

## Next Steps

1. Run `./setup.sh` (or `setup.bat` on Windows)
2. Edit `.env` to configure paths and LLM provider
3. Run `python run.py` to start the agent
4. See `../../docs/AGENT_SETUP.md` for detailed configuration guide
