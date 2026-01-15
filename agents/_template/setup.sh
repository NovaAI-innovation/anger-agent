#!/bin/bash
# ============================================================================
# Agent Template - Setup Script (Unix/Linux/macOS)
# ============================================================================
#
# Purpose: Sets up environment for any new agent
#   - Creates necessary directories
#   - Configures .env file from template
#   - Validates everything works
#
# Usage:
#   ./setup.sh              (interactive prompts)
#   ./setup.sh --quiet      (use defaults)
#   ./setup.sh --help       (show help)
#
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Show help
if [[ "$1" == "--help" ]]; then
    echo "Agent - Setup Script"
    echo ""
    echo "Usage: ./setup.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --quiet    Use default values (no prompts)"
    echo "  --help     Show this help message"
    echo ""
    exit 0
fi

QUIET=$([[ "$1" == "--quiet" ]] && echo true || echo false)

echo "=================================================="
echo "Agent - Setup"
echo "=================================================="
echo ""

# Step 1: Create directories
echo "1. Creating data directories..."
mkdir -p "$SCRIPT_DIR/data/inbox"
mkdir -p "$SCRIPT_DIR/data/processed"
mkdir -p "$SCRIPT_DIR/data/errors"
mkdir -p "$SCRIPT_DIR/logs"
echo -e "   ${GREEN}✓${NC} Directories created"

# Step 2: Create .env file
echo ""
echo "2. Configuring environment..."

if [ -f "$SCRIPT_DIR/.env" ]; then
    echo -e "   ${YELLOW}!${NC} .env already exists"
    if [[ "$QUIET" == false ]]; then
        read -p "   Overwrite? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "   Skipping .env creation"
        else
            cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env" 2>/dev/null || true
            echo -e "   ${GREEN}✓${NC} Created .env from template"
        fi
    fi
else
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env" 2>/dev/null || true
    echo -e "   ${GREEN}✓${NC} Created .env from template"
fi

# Step 3: Prompt for customization
if [[ "$QUIET" == false ]]; then
    echo ""
    echo "3. (Optional) Customize paths..."
    echo "   Edit .env to change paths, or press Enter to use defaults"
    read -p "   Edit .env now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} "$SCRIPT_DIR/.env"
    fi
fi

# Step 4: Verify
echo ""
echo "4. Verifying configuration..."

if [ ! -f "$SCRIPT_DIR/run.py" ]; then
    echo -e "   ${RED}✗${NC} run.py not found"
    exit 1
fi
echo -e "   ${GREEN}✓${NC} Agent runner found"

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Setup complete!${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Edit your agent configuration:"
echo "     vim config.yaml"
echo ""
echo "  2. Verify your .env file:"
echo "     cat .env"
echo ""
echo "  3. Run the agent from project root:"
echo "     ./scripts/run.sh <agent_name>"
echo ""
