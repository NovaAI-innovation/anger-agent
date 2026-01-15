#!/bin/bash
# Run any agent
#
# Usage:
#   ./scripts/run.sh examples/file_validator
#   ./scripts/run.sh my_agent

set -e

if [ $# -eq 0 ]; then
    echo "Usage: ./scripts/run.sh <agent_name>"
    echo ""
    echo "Examples:"
    echo "  ./scripts/run.sh examples/file_validator"
    echo "  ./scripts/run.sh my_agent"
    echo ""
    echo "Available agents:"
    ls -d agents/*/ 2>/dev/null | sed 's|agents/||g' | sed 's|/||g' || echo "  (none yet)"
    exit 1
fi

AGENT_NAME=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
AGENT_DIR="$PROJECT_ROOT/agents/$AGENT_NAME"

if [ ! -d "$AGENT_DIR" ]; then
    echo "Error: Agent not found: agents/$AGENT_NAME"
    exit 1
fi

if [ ! -f "$AGENT_DIR/run.py" ]; then
    echo "Error: No run.py found in agents/$AGENT_NAME"
    exit 1
fi

echo "Starting agent: $AGENT_NAME"
echo "Config: $AGENT_DIR/config.yaml"
echo ""

cd "$AGENT_DIR"
python3 run.py
