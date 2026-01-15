#!/bin/bash
# Generate a new agent from template
#
# Usage:
#   ./scripts/new_agent.sh my_agent

set -e

if [ $# -eq 0 ]; then
    echo "Usage: ./scripts/new_agent.sh <agent_name>"
    echo ""
    echo "Examples:"
    echo "  ./scripts/new_agent.sh my_validator"
    echo "  ./scripts/new_agent.sh data_processor"
    exit 1
fi

AGENT_NAME=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$PROJECT_ROOT/agents/_template"
TARGET_DIR="$PROJECT_ROOT/agents/$AGENT_NAME"

# Check if template exists
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: Template not found at $TEMPLATE_DIR"
    exit 1
fi

# Check if agent already exists
if [ -d "$TARGET_DIR" ]; then
    echo "Error: Agent already exists: agents/$AGENT_NAME"
    exit 1
fi

# Copy template
echo "Creating new agent: $AGENT_NAME"
cp -r "$TEMPLATE_DIR" "$TARGET_DIR"
echo "✓ Created: agents/$AGENT_NAME"

echo ""
echo "Next steps:"
echo "  1. Edit configuration:"
echo "     vim agents/$AGENT_NAME/config.yaml"
echo ""
echo "  2. Edit documentation:"
echo "     vim agents/$AGENT_NAME/AGENTS.md"
echo ""
echo "  3. Run your agent:"
echo "     ./scripts/run.sh $AGENT_NAME"
echo ""
echo "For more help, see: docs/CREATE_AGENT.md"
