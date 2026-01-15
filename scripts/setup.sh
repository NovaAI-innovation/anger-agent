#!/bin/bash
# Agent Framework Setup Script
#
# Performs one-time setup:
# - Creates data directories
# - Installs Python dependencies
# - Validates example configs

set -e  # Exit on error

echo "=================================================="
echo "Agent Framework v0.1 - Setup"
echo "=================================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo ""
echo "1. Creating data directories..."
mkdir -p data/inbox data/processed data/errors
mkdir -p logs
mkdir -p /tmp/agent_inbox /tmp/agent_processed /tmp/agent_errors
echo "   ✓ Directories created"

echo ""
echo "2. Installing Python dependencies..."
if command -v pip &> /dev/null; then
    pip install -q -r requirements.txt
    echo "   ✓ Dependencies installed"
else
    echo "   ✗ pip not found. Please install Python 3.9+"
    exit 1
fi

echo ""
echo "3. Verifying Python runtime..."
python3 -c "from runtime import Agent; print('   ✓ Runtime verified')" || {
    echo "   ✗ Runtime error"
    exit 1
}

echo ""
echo "4. Checking example configs..."
if python3 -c "
import sys
sys.path.insert(0, '.')
from runtime.config import Config
try:
    Config('agents/examples/file_validator/config.yaml')
    print('   ✓ Example agent config valid')
except Exception as e:
    print(f'   ✗ Config error: {e}')
    sys.exit(1)
"; then
    :
else
    exit 1
fi

echo ""
echo "=================================================="
echo "✓ Setup complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Run example agent:"
echo "     ./scripts/run.sh examples/file_validator"
echo ""
echo "  2. In another terminal, test it:"
echo "     echo '{\"id\": 1, \"name\": \"Test\", \"email\": \"test@example.com\"}' > /tmp/agent_inbox/valid.json"
echo ""
echo "  3. Create your own agent:"
echo "     ./scripts/new_agent.sh my_agent"
echo ""
